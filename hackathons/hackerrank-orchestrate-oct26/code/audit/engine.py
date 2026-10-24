"""Deletion-audit engine: identity resolution, resource linking, state reconstruction,
policy application and step planning. Fully deterministic."""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

from .evidence import EvidenceStore, Observation, RESOURCE_RE, resource_prefix, system_for

# ----------------------------------------------------------------------------- policy

# category -> required treatment (mirrors deletion_rules.csv; loaded & validated at runtime)
DEFAULT_TREATMENT = {
    "USER_PROFILE": "DELETE",
    "SECONDARY_IDENTIFIER": "DELETE",
    "SEARCH_INDEX_ENTRY": "DELETE",
    "CACHE_ENTRY": "DELETE",
    "SUPPORT_MESSAGE": "REDACT",
    "SUPPORT_ATTACHMENT": "DELETE",
    "ANALYTICS_PROFILE": "ANONYMIZE",
    "PRODUCT_TELEMETRY": "ANONYMIZE",
    "USER_EXPORT": "DELETE",
    "MARKETING_PROFILE": "DELETE",
    "EMAIL_DELIVERY_LOG": "REDACT",
    "SECURITY_AUDIT_LOG": "RETAIN",
    "LEGAL_HOLD_RECORD": "RETAIN",
    "BACKUP_ARCHIVE": "RETAIN",
    "ACCOUNT_TOMBSTONE": "REDACT",
    "DATA_FLOW": "DISABLE",
}

PREFIX_CATEGORY = {
    "account": "USER_PROFILE",
    "search": "SEARCH_INDEX_ENTRY",
    "analytics": "ANALYTICS_PROFILE",
    "support": "SUPPORT_MESSAGE",
    "export": "USER_EXPORT",
    "data_flow": "DATA_FLOW",
    "backup": "BACKUP_ARCHIVE",
    "audit_record": "SECURITY_AUDIT_LOG",
    "tombstone": "ACCOUNT_TOMBSTONE",
    "legal_hold": "LEGAL_HOLD_RECORD",
    "marketing": "MARKETING_PROFILE",
    "object": "SUPPORT_ATTACHMENT",
    "cache": "CACHE_ENTRY",
}

OP_ORDER = [
    "REPORT_REMAINING_RECORD", "REPORT_EXPOSED_PII", "REPORT_ACTIVE_DATA_FLOW", "REPORT_RESTORE_RISK",
    "DISABLE_DATA_FLOW", "BLOCK_RESTORE", "DELETE_RECORD", "REDACT_RECORD", "ANONYMIZE_RECORD",
    "VERIFY_RECORD_ABSENT", "VERIFY_RECORD_PRESENT", "VERIFY_RECORD_REDACTED", "VERIFY_RECORD_ANONYMIZED",
    "VERIFY_DATA_FLOW_DISABLED", "VERIFY_RESTORE_BLOCKED",
]
OP_META = {
    "REPORT_REMAINING_RECORD": ("FINDING", "PRESENT"),
    "REPORT_EXPOSED_PII": ("FINDING", "PRESENT"),
    "REPORT_ACTIVE_DATA_FLOW": ("FINDING", "ACTIVE"),
    "REPORT_RESTORE_RISK": ("FINDING", "ACTIVE"),
    "DISABLE_DATA_FLOW": ("REMEDIATION", "DISABLED"),
    "BLOCK_RESTORE": ("REMEDIATION", "BLOCKED"),
    "DELETE_RECORD": ("REMEDIATION", "ABSENT"),
    "REDACT_RECORD": ("REMEDIATION", "REDACTED"),
    "ANONYMIZE_RECORD": ("REMEDIATION", "ANONYMIZED"),
    "VERIFY_RECORD_ABSENT": ("VERIFICATION", "ABSENT"),
    "VERIFY_RECORD_PRESENT": ("VERIFICATION", "PRESENT"),
    "VERIFY_RECORD_REDACTED": ("VERIFICATION", "REDACTED"),
    "VERIFY_RECORD_ANONYMIZED": ("VERIFICATION", "ANONYMIZED"),
    "VERIFY_DATA_FLOW_DISABLED": ("VERIFICATION", "DISABLED"),
    "VERIFY_RESTORE_BLOCKED": ("VERIFICATION", "BLOCKED"),
}

# observation states
ABSENT, PRESENT, IDENT, CLEAN, ACTIVE, DISABLED, UNKNOWN = (
    "ABSENT", "PRESENT", "IDENT", "CLEAN", "ACTIVE", "DISABLED", "UNKNOWN")

REFERENCE_FIELDS = {"customer_reference", "subject_reference", "user_id", "subject_ref"}
DIRECT_ID_FIELDS = {"email", "phone", "email_hash", "full_name", "name", "display_name", "requester_email",
                    "requester_name", "requester_phone", "owner_email", "owner_phone", "customer_email",
                    "document.email", "document.display_name"}
TEXT_FIELDS = {"message_text", "message_excerpt", "document_text"}


def _is_set(v):
    return v not in (None, "", "[REDACTED]", False) and str(v).lower() not in ("null", "none", "—", "-")


# ----------------------------------------------------------------------------- identity

@dataclass
class Identity:
    user_id: str
    emails: set = field(default_factory=set)
    phones: set = field(default_factory=set)
    hashes: set = field(default_factory=set)
    names: set = field(default_factory=set)
    audit_ids: list = field(default_factory=list)

    @property
    def strong(self) -> set:
        return {v.lower() for v in self.emails | self.phones | self.hashes} | {self.user_id.lower()}

    def matches_value(self, v) -> bool:
        if not isinstance(v, str):
            return False
        return v.strip().lower() in self.strong

    def mentioned_in(self, text) -> bool:
        if not isinstance(text, str) or not text:
            return False
        t = text.lower()
        if any(e.lower() in t for e in self.emails | self.hashes):
            return True
        if any(p in text for p in self.phones):
            return True
        return re.search(rf"\b{re.escape(self.user_id)}\b", text) is not None


class IdentityResolver:
    def __init__(self, dataset_dir: Path):
        self.users = {}
        with open(dataset_dir / "user_identities.csv", newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                self.users[r["user_id"]] = Identity(r["user_id"], {r["email"].lower()}, {r["phone"]},
                                                   {r["email_hash"]}, {r["name"]})
        self.history = []
        p = dataset_dir / "user_audit_log.csv"
        if p.exists():
            with open(p, newline="", encoding="utf-8") as f:
                self.history = list(csv.DictReader(f))
        self.by_email = {}
        for u in self.users.values():
            for e in u.emails:
                self.by_email.setdefault(e, set()).add(u.user_id)
        for h in self.history:
            if h["field_name"] == "email":
                for v in (h["old_value"], h["new_value"]):
                    self.by_email.setdefault(v.lower(), set()).add(h["user_id"])

    def resolve(self, email: str, as_of: str | None = None) -> Identity | None:
        cands = self.by_email.get(email.strip().lower(), set())
        if not cands:
            return None
        return self.resolve_user(sorted(cands)[0])

    def resolve_user(self, uid: str) -> Identity:
        base = self.users[uid]
        ident = Identity(uid, set(base.emails), set(base.phones), set(base.hashes), set(base.names))
        for h in self.history:
            if h["user_id"] != uid:
                continue
            fld = h["field_name"]
            vals = [h["old_value"], h["new_value"]]
            target = {"email": ident.emails, "phone": ident.phones, "email_hash": ident.hashes,
                      "name": ident.names}.get(fld)
            if target is not None:
                for v in vals:
                    if v:
                        target.add(v.lower() if fld == "email" else v)
            ident.audit_ids.append(h["audit_id"])
        return ident


# ----------------------------------------------------------------------------- observation semantics

def classify(o: Observation):
    """Return (category or None, state) for one observation."""
    f = o.fields
    pre = resource_prefix(o.resource_id)
    cat = f.get("record_type") if isinstance(f.get("record_type"), str) else None
    result = str(f.get("result") or "").upper()

    if f.get("mentions_only"):
        return classify_document(o)

    # record_type/result style digests (handover, lookups, history)
    if cat and result:
        m = {"FOUND": PRESENT, "NOT_FOUND": ABSENT, "IDENTIFIABLE": IDENT, "ANONYMIZED": CLEAN,
             "REDACTED": CLEAN, "ACTIVE": ACTIVE, "DISABLED": DISABLED, "BLOCKED": DISABLED,
             "ABSENT": ABSENT, "PRESENT": PRESENT}
        st = m.get(result, UNKNOWN)
        if st == PRESENT and cat in ("SUPPORT_MESSAGE", "ANALYTICS_PROFILE", "ACCOUNT_TOMBSTONE",
                                     "EMAIL_DELIVERY_LOG", "PRODUCT_TELEMETRY"):
            st = IDENT
        return cat, st

    ev = str(f.get("event") or "")
    if pre == "data_flow":
        en = f.get("enabled")
        if en is None and "scheduler_registered" in f:
            en = f.get("scheduler_registered")
        if en is None:
            return "DATA_FLOW", UNKNOWN
        return "DATA_FLOW", ACTIVE if en in (True, 1, "1") else DISABLED
    if pre == "backup":
        if "restore_allowed" in f:
            return "BACKUP_ARCHIVE", ACTIVE if f["restore_allowed"] in (True, 1, "1") else DISABLED
        if "eligible" in f or "deletion_block" in f:
            active = f.get("eligible") in (True, "1") and f.get("deletion_block") not in (True, "1")
            return "BACKUP_ARCHIVE", ACTIVE if active else DISABLED
        if "decision" in f:
            return "BACKUP_ARCHIVE", ACTIVE if str(f["decision"]).lower() in ("allow", "allowed", "approve") else DISABLED
        return "BACKUP_ARCHIVE", UNKNOWN
    if pre == "account":
        if "http_status" in f or "rows" in f or "status_code" in f:
            code = str(f.get("http_status") or f.get("status_code") or "")
            rows = str(f.get("rows") or "")
            if code == "404" or rows == "0":
                return "USER_PROFILE", ABSENT
            return "USER_PROFILE", PRESENT
        return "USER_PROFILE", PRESENT
    if pre == "search":
        r = str(f.get("result") or "").lower()
        if r in ("miss", "not_found", "none"):
            return "SEARCH_INDEX_ENTRY", ABSENT
        if str(f.get("total_hits") or "") == "0":
            return "SEARCH_INDEX_ENTRY", ABSENT
        return "SEARCH_INDEX_ENTRY", PRESENT
    if pre == "export":
        av = f.get("available", f.get("download_available"))
        if av is False:
            return "USER_EXPORT", ABSENT
        return "USER_EXPORT", PRESENT
    if pre == "audit_record":
        if str(f.get("rows") or "1") == "0":
            return "SECURITY_AUDIT_LOG", ABSENT
        return "SECURITY_AUDIT_LOG", PRESENT
    if pre == "legal_hold":
        return "LEGAL_HOLD_RECORD", PRESENT
    if pre == "analytics":
        if "contact" in ev:  # marketing-contact lookup keyed on an identifier -> secondary identifier
            return "SECONDARY_IDENTIFIER", PRESENT
        if ev == "analytics_identity_scan" or (f.get("matched_value") and f.get("detector")):
            return "ANALYTICS_PROFILE", IDENT
        if "direct_identifiers" in f:
            return "ANALYTICS_PROFILE", IDENT if str(f["direct_identifiers"]) != "0" else CLEAN
        ident = any(_is_set(f.get(k)) for k in ("email", "phone", "email_hash", "user_id", "customer_reference"))
        return "ANALYTICS_PROFILE", IDENT if ident else CLEAN
    if pre == "tombstone":
        ident = any(_is_set(f.get(k)) for k in ("name", "email", "phone", "email_hash", "full_name"))
        return "ACCOUNT_TOMBSTONE", IDENT if ident else CLEAN
    if pre == "support":
        is_attach = (ev.startswith("attachment") or "file" in f or "file_name" in f
                     or f.get("collection") == "ticket_attachments" or f.get("collection_name") == "ticket_attachments"
                     or f.get("storage_class") == "ticket_attachment")
        if is_attach:
            return "SUPPORT_ATTACHMENT", PRESENT
        if ev in ("contact_query_completed", "deletion_marker_check"):
            # legacy contact-index entry keyed on an identifier -> secondary identifier record
            if ev == "deletion_marker_check" and f.get("marker_found") is True:
                return "SECONDARY_IDENTIFIER", ABSENT
            if str(f.get("rows") or "1") == "0":
                return "SECONDARY_IDENTIFIER", ABSENT
            return "SECONDARY_IDENTIFIER", PRESENT
        if ev == "message_pii_scan":
            return "SUPPORT_MESSAGE", IDENT
        if ev == "thumbnail_failed":
            return None, UNKNOWN
        ident = any(_is_set(f.get(k)) for k in ("requester_email", "requester_name", "requester_phone", "email",
                                                 "phone", "name"))
        txt = " ".join(str(f.get(k) or "") for k in ("message_text", "message_excerpt"))
        if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+|\+\d[\d ()-]{6,}", txt):
            ident = True
        return "SUPPORT_MESSAGE", IDENT if ident else CLEAN
    return PREFIX_CATEGORY.get(pre), PRESENT


EMAIL_OR_PHONE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\+\d{1,3}[\d ()-]{6,}\d")


def classify_document(o: Observation):
    """State of a resource shown in a business artifact (PDF / screenshot). Artifacts do not state a
    verdict; they show the record as it existed at capture time."""
    text = o.fields.get("document_text") or ""
    low = text.lower()
    pre = resource_prefix(o.resource_id)
    has_pii = bool(EMAIL_OR_PHONE.search(text))
    if pre == "data_flow":
        off = re.search(r"\b(disabled|paused|stopped|inactive|suspended)\b", low)
        return "DATA_FLOW", DISABLED if off else ACTIVE
    if pre == "backup":
        blocked = re.search(r"restore (blocked|disabled|denied)|deletion[ _-]block(ed)?\s*[:|]?\s*(true|yes|on)|not restorable", low)
        return "BACKUP_ARCHIVE", DISABLED if blocked else ACTIVE
    if pre == "tombstone":
        return "ACCOUNT_TOMBSTONE", IDENT if has_pii else CLEAN
    if pre == "analytics":
        return "ANALYTICS_PROFILE", IDENT if has_pii else CLEAN
    if pre == "support":
        if o.source == "pdf" or re.search(r"attachment|\.pdf|\.jpg|\.png", low):
            return "SUPPORT_ATTACHMENT", PRESENT
        return "SUPPORT_MESSAGE", IDENT if has_pii else CLEAN
    if pre == "export" and re.search(r"expired|deleted|unavailable", low) and not re.search(r"available|download", low):
        return "USER_EXPORT", ABSENT
    return PREFIX_CATEGORY.get(pre), PRESENT


def links_to(o: Observation, ident: Identity) -> bool:
    if o.fields.get("no_link"):  # linked through its catalog activity instead
        return False
    if any(ident.matches_value(k) for k in o.keys):
        return True
    for k, v in o.fields.items():
        if k in TEXT_FIELDS:
            if ident.mentioned_in(v):
                return True
        elif isinstance(v, str) and ident.matches_value(v):
            return True
    return False


# ----------------------------------------------------------------------------- engine

@dataclass
class ResourceState:
    system_id: str
    resource_id: str
    category: str
    state: str
    evidence_id: str
    time: str


class AuditEngine:
    def __init__(self, dataset_dir: Path, store: EvidenceStore, identities: IdentityResolver):
        self.dataset_dir = Path(dataset_dir)
        self.store = store
        self.ids = identities
        self.rules = self._load_rules()
        self.activities = self._load_activities()
        self.by_resource: dict[str, list[Observation]] = {}
        for o in store.observations:
            self.by_resource.setdefault(o.resource_id, []).append(o)
        self.catalog_media = {}
        self._attach_catalog_media()
        for lst in self.by_resource.values():
            lst.sort(key=lambda o: (o.time, o.evidence_id))
        self.owners = self._build_owner_index()

    def _attach_catalog_media(self):
        """The data catalog registers each business artifact (screenshot / PDF) a few minutes after
        capture and names the resource it shows. Pair the artifact with that resource so its contents
        become an observation of the resource."""
        from datetime import datetime
        P = lambda t: datetime.fromisoformat(t.replace("Z", "+00:00"))
        media = [(eid, row) for eid, row in self.store.manifest.items()
                 if row["file_path"].lower().endswith((".png", ".jpg", ".jpeg", ".pdf"))]
        for a in self.activities:
            if a["event_type"] != "LINK_RESOURCE_IDENTITY":
                continue
            t = P(a["event_time"])
            best = None
            for eid, row in media:
                dt = (t - P(row["captured_at"])).total_seconds()
                if 0 <= dt <= 1800 and (best is None or dt < best[0]):
                    best = (dt, eid, row)
            if not best:
                continue
            _, eid, row = best
            text = self.store.media_text.get(eid, "")
            o = Observation(eid, row["captured_at"], row["captured_at"], a["target_system"], a["resource_id"],
                            "catalog_media", {"document_text": text + "\n" + a["details"], "mentions_only": True, "no_link": True},
                            set())
            self.store.observations.append(o)
            self.by_resource.setdefault(a["resource_id"], []).append(o)
            self.catalog_media[a["activity_id"]] = (eid, text)

    def _artifact_contradicts(self, activity, ident) -> bool:
        """A catalog link is a claim. If the artifact it was registered from shows the resource with
        someone else's contact details and none of the subject's, the claim is rejected."""
        eid, text = self.catalog_media.get(activity["activity_id"], (None, ""))
        if not text or self.TRUST_CATALOG:
            return False
        rid = activity["resource_id"]
        rows = [l for l in text.splitlines() if rid in l.replace(" ", "")] or text.splitlines()
        ctx = "\n".join(rows)
        if ident.mentioned_in(ctx) or ident.mentioned_in(text):
            return False
        emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", ctx)
        return bool(emails)

    def _build_owner_index(self):
        """resource_id -> set(user_id) linked by any direct identifier in any evidence (global view).
        Used to avoid attributing another person's resource to the subject."""
        val2u = {}
        for uid in self.ids.users:
            ident = self.ids.resolve_user(uid)
            for v in ident.strong:
                val2u.setdefault(v, set()).add(uid)
        owners = {}
        for o in self.store.observations:
            vals = [k.lower() for k in o.keys] + [str(v).strip().lower() for v in o.fields.values() if isinstance(v, str)]
            for v in vals:
                for u in val2u.get(v, ()):
                    owners.setdefault(o.resource_id, set()).add(u)
        for a in self.activities:
            if a["event_type"] == "LINK_RESOURCE_IDENTITY":
                for m in re.finditer(r"\buser_\d+\b", a["details"]):
                    owners.setdefault(a["resource_id"], set()).add(m.group(0))
        return owners

    def _load_rules(self):
        rules = dict(DEFAULT_TREATMENT)
        p = self.dataset_dir / "deletion_rules.csv"
        with open(p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rules[r["data_category"]] = r["required_action"]
        return rules

    def _load_activities(self):
        with open(self.dataset_dir / "system_activity.csv", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    # ------------------------------------------------------------------ linking
    def linked_resources(self, ident: Identity, audit_at: str, since: str = "") -> dict[str, list[str]]:
        """resource_id -> list of evidence ids that link it to the subject (in (since, audit_at])."""
        key = (ident.user_id, audit_at, since, self.TRUST_CATALOG)
        cache = self.__dict__.setdefault("_link_cache", {})
        if key not in cache:
            cache[key] = self._linked_resources(ident, audit_at, since)
        return {k: list(v) for k, v in cache[key].items()}

    def _build_value_index(self):
        """Inverted index: lower-cased identifier value -> observations carrying it (exact-value fields
        and lookup keys). Free-text observations are kept aside and scanned with substring matching."""
        idx, text_obs = {}, []
        for o in self.store.observations:
            if o.fields.get("no_link"):
                continue
            vals = {k.strip().lower() for k in o.keys}
            for k, v in o.fields.items():
                if k in TEXT_FIELDS:
                    if v:
                        text_obs.append(o)
                elif isinstance(v, str):
                    vals.add(v.strip().lower())
            for v in vals:
                idx.setdefault(v, []).append(o)
        self._value_index, self._text_obs = idx, text_obs

    def _linked_resources(self, ident: Identity, audit_at: str, since: str = "") -> dict[str, list[str]]:
        linked: dict[str, list[str]] = {}
        if not hasattr(self, "_value_index"):
            self._build_value_index()
        cands = {id(o): o for v in ident.strong for o in self._value_index.get(v, [])}
        for o in self._text_obs:
            cands.setdefault(id(o), o)
        for o in sorted(cands.values(), key=lambda o: (o.time, o.evidence_id, o.resource_id)):
            if o.time > audit_at or o.time <= since:
                continue
            if links_to(o, ident):
                linked.setdefault(o.resource_id, []).append(o.evidence_id)
        # catalog links and connector->downstream dependencies from the activity stream
        for a in self.activities:
            if a["event_time"] > audit_at or a["event_time"] <= since:
                continue
            d = a["details"]
            if a["event_type"] == "LINK_RESOURCE_IDENTITY":
                if (ident.mentioned_in(d) or re.search(rf"\b{re.escape(ident.user_id)}\b", d)) \
                        and not self._artifact_contradicts(a, ident):
                    linked.setdefault(a["resource_id"], []).append(a["activity_id"])
        changed = True
        while changed:
            changed = False
            for a in self.activities:
                if a["event_time"] > audit_at:
                    continue
                if a["event_type"] in ("SYNC_RECORD", "RESTORE_BACKUP") and "repopulated downstream resource" in a["details"]:
                    m = RESOURCE_RE.search(a["details"].split("resource", 1)[1])
                    if m and m.group(0) in linked and a["resource_id"] not in linked:
                        linked[a["resource_id"]] = [a["activity_id"]]
                        changed = True
        return linked

    # ------------------------------------------------------------------ workflow attribution
    STATUS_RESULT = {"COMPLETE": "SUCCESS", "PARTIALLY_COMPLETE": "PARTIAL", "NOT_STARTED": "FAILED"}

    # ablation switches (used by evaluation/main.py)
    DISABLE_WORKFLOW = False
    TRUST_CATALOG = False
    DISABLE_ERAS = False

    def workflow_resources(self, case, ident, linked, window_h=3.0):
        """Resources processed by *this request's* deletion workflow.

        Records that were already scrubbed (404 profile, anonymized analytics row) no longer carry
        identifiers, so evidence alone cannot tie them to the subject. The deletion workflow's own
        activity can: its account job runs shortly before `reported_at`, and its outcome is what the
        workflow reported (COMPLETE<-SUCCESS, PARTIALLY_COMPLETE<-PARTIAL, NOT_STARTED<-FAILED).
        Only resources that no evidence attributes to a different person are eligible."""
        from datetime import datetime, timedelta
        if self.DISABLE_WORKFLOW:
            return {}
        P = lambda t: datetime.fromisoformat(t.replace("Z", "+00:00"))
        rep = P(case["reported_at"])
        lo = max(P(case["requested_at"]), rep - timedelta(hours=window_h))
        expected = self.STATUS_RESULT.get(case["reported_status"])
        out = {}

        def eligible(rid):
            own = self.owners.get(rid, set())
            return not own or own == {ident.user_id}

        has_account = any(resource_prefix(r) == "account" for r in linked)
        acc_time = None
        if not has_account and case["case_id"] in self.assigned_accounts:
            a = self.assigned_accounts[case["case_id"]]
            if a is not None:
                out[a["resource_id"]] = a["activity_id"]
                acc_time = P(a["event_time"])
        elif not has_account:
            cands = [a for a in self.activities
                     if a["source_system"] == "deletion_worker" and a["target_system"] == "account_service"
                     and lo <= P(a["event_time"]) <= rep and a["reported_result"] == expected
                     and eligible(a["resource_id"])]
            if cands:
                a = max(cands, key=lambda a: a["event_time"])
                out[a["resource_id"]] = a["activity_id"]
                acc_time = P(a["event_time"])
        else:
            accs = [a for a in self.activities if a["resource_id"] in linked
                    and a["target_system"] == "account_service" and a["source_system"] == "deletion_worker"
                    and lo <= P(a["event_time"]) <= rep]
            if accs:
                acc_time = P(min(accs, key=lambda a: a["event_time"])["event_time"])
        if acc_time is not None and self.case_windows is not None:
            for a in self.activities:
                if a["source_system"] != "deletion_worker" or a["target_system"] == "account_service":
                    continue
                t = P(a["event_time"])
                if not (acc_time <= t <= rep) or a["resource_id"] in linked or self.owners.get(a["resource_id"]):
                    continue
                # attribute only when no other request's workflow window could explain this activity
                others = [cid for cid, (w0, w1) in self.case_windows.items()
                          if cid != case["case_id"] and w0 <= t <= w1
                          and self.case_subject.get(cid) != ident.user_id]
                if not others:
                    out.setdefault(a["resource_id"], a["activity_id"])
        return out

    case_windows = None
    case_subject: dict = {}
    TIEBREAK_EARLIEST = True
    all_cases: list = []
    assigned_accounts: dict = {}

    def era_start(self, case, ident):
        """Audit time of the same subject's previous request: older evidence belongs to that request."""
        prev = ""
        if self.DISABLE_ERAS:
            return prev
        for c in self.all_cases:
            if c["case_id"] == case["case_id"] or c["requested_at"] >= case["requested_at"]:
                continue
            other = self.ids.resolve(c["email"])
            if other and other.user_id == ident.user_id and c["audit_at"] > prev:
                prev = c["audit_at"]
        return prev

    def prepare(self, cases):
        """Pre-compute every request's workflow window [account job, reported_at] (global view)."""
        from datetime import datetime, timedelta
        P = lambda t: datetime.fromisoformat(t.replace("Z", "+00:00"))
        self.case_windows = None
        self.case_subject = {}
        self.all_cases = list(cases)
        self.assigned_accounts = {}
        # 1) candidate workflow account jobs per request lacking an evidence-linked account
        cand = {}
        taken = set()
        alias = {}  # duplicate submissions (same subject + same workflow timing) share one workflow
        first_of = {}
        for c in cases:
            ident = self.ids.resolve(c["email"])
            if ident is None:
                continue
            wkey = (ident.user_id, c["requested_at"], c["reported_at"], c["reported_status"])
            if wkey in first_of:
                alias[c["case_id"]] = first_of[wkey]
                continue
            first_of[wkey] = c["case_id"]
            linked = self.linked_resources(ident, c["audit_at"], self.era_start(c, ident))
            accs = [r for r in linked if resource_prefix(r) == "account"]
            taken.update(accs)
            if accs:
                continue
            rep = P(c["reported_at"])
            lo = max(P(c["requested_at"]), rep - timedelta(hours=3))
            exp = self.STATUS_RESULT.get(c["reported_status"])
            own_ok = lambda r: not self.owners.get(r) or self.owners.get(r) == {ident.user_id}
            cand[c["case_id"]] = [a for a in self.activities
                                  if a["source_system"] == "deletion_worker" and a["target_system"] == "account_service"
                                  and lo <= P(a["event_time"]) <= rep and a["reported_result"] == exp
                                  and own_ok(a["resource_id"])]
        # 2) resolve: requests with a single remaining candidate claim it first; others take the job
        #    closest to reported_at that nobody else claimed
        for cid in cand:
            cand[cid] = [a for a in cand[cid] if a["resource_id"] not in taken]
        pending = dict(cand)
        while pending:
            forced = [cid for cid, lst in pending.items() if len(lst) <= 1]
            pick = forced[0] if forced else min(pending)
            lst = pending.pop(pick)
            choice = (min if self.TIEBREAK_EARLIEST else max)(lst, key=lambda a: a["event_time"]) if lst else None
            self.assigned_accounts[pick] = choice
            if choice:
                for cid in pending:
                    pending[cid] = [a for a in pending[cid] if a["resource_id"] != choice["resource_id"]]
        for dup, orig in alias.items():
            if orig in self.assigned_accounts:
                self.assigned_accounts[dup] = self.assigned_accounts[orig]
        wins = {}
        for c in cases:
            if c["case_id"] in alias:
                continue
            ident = self.ids.resolve(c["email"])
            if ident is None:
                continue
            linked = self.linked_resources(ident, c["audit_at"], self.era_start(c, ident))
            wf = self.workflow_resources(c, ident, linked)
            accs = [r for r in list(linked) + list(wf) if resource_prefix(r) == "account"]
            times = [P(a["event_time"]) for a in self.activities if a["resource_id"] in accs
                     and a["source_system"] == "deletion_worker"
                     and P(c["requested_at"]) <= P(a["event_time"]) <= P(c["reported_at"])]
            if times:
                wins[c["case_id"]] = (min(times), P(c["reported_at"]))
                self.case_subject[c["case_id"]] = ident.user_id
        self.case_windows = wins

    # ------------------------------------------------------------------ state
    def state_at(self, rid: str, audit_at: str):
        obs = [o for o in self.by_resource.get(rid, []) if o.time <= audit_at]
        cat = None
        for o in obs:
            c, _ = classify(o)
            if c:
                cat = c
        cat = cat or PREFIX_CATEGORY.get(resource_prefix(rid))
        known = [(o, classify(o)[1]) for o in obs]
        known = [(o, s) for o, s in known if s != UNKNOWN]
        if not known:
            ev = obs[-1].evidence_id if obs else ""
            return cat, UNKNOWN, ev, obs[-1].time if obs else ""
        tmax = max(o.time for o, _ in known)
        latest = [(o, s) for o, s in known if o.time == tmax]
        severity = {IDENT: 5, ACTIVE: 5, PRESENT: 4, CLEAN: 2, DISABLED: 2, ABSENT: 1}
        o, s = max(latest, key=lambda x: (severity.get(x[1], 0), x[0].evidence_id))
        if o.captured_at > audit_at:
            # never cite a file captured after audit_at: fall back to the latest citable observation
            # that shows the same state
            # the observation itself predates audit_at (log exports are captured after their lines)
            same = [x for x, st in known if st == s and x.captured_at <= audit_at]
            ev = same[-1].evidence_id if same else o.evidence_id
            return cat, s, ev, o.time
        return cat, s, o.evidence_id, o.time

    # ------------------------------------------------------------------ planning
    def audit(self, case: dict) -> tuple[str, list[dict], dict]:
        audit_at = case["audit_at"]
        ident = self.ids.resolve(case["email"])
        trace = {"user_id": ident.user_id if ident else None, "resources": []}
        if ident is None:
            return "COMPLETE", [], trace
        linked = self.linked_resources(ident, audit_at, self.era_start(case, ident))
        for rid, src in self.workflow_resources(case, ident, linked).items():
            linked.setdefault(rid, []).append(src)
        findings, remediation, verification = [], [], []
        states = []
        for rid in sorted(linked):
            cat, st, ev, t = self.state_at(rid, audit_at)
            states.append(ResourceState(system_for(rid), rid, cat, st, ev, t))
        has_account = any(s.category == "USER_PROFILE" for s in states)
        if not has_account:
            acc = self._fallback_account(ident, audit_at)
            if acc:
                states.append(acc)
        for s in states:
            if s.category == "USER_PROFILE" and s.state == UNKNOWN:
                cov = self._coverage_state(s.resource_id, "account_service", audit_at)
                if cov:
                    s.state, s.evidence_id = cov
            if s.state == UNKNOWN and not s.evidence_id and linked.get(s.resource_id):
                s.evidence_id = linked[s.resource_id][0]
            trace["resources"].append(s.__dict__)
            treatment = self.rules.get(s.category or "", None)
            if s.category == "DATA_FLOW":
                if s.state == ACTIVE:
                    findings.append(("REPORT_ACTIVE_DATA_FLOW", s))
                    remediation.append(("DISABLE_DATA_FLOW", s))
                    verification.append(("VERIFY_DATA_FLOW_DISABLED", s, False))
                elif s.state == DISABLED:
                    verification.append(("VERIFY_DATA_FLOW_DISABLED", s, True))
            elif s.category == "BACKUP_ARCHIVE":
                if s.state == ACTIVE:
                    findings.append(("REPORT_RESTORE_RISK", s))
                    remediation.append(("BLOCK_RESTORE", s))
                    verification.append(("VERIFY_RESTORE_BLOCKED", s, False))
                elif s.state == DISABLED:
                    verification.append(("VERIFY_RESTORE_BLOCKED", s, True))
            elif treatment == "RETAIN":
                if s.state in (PRESENT, IDENT, CLEAN):
                    verification.append(("VERIFY_RECORD_PRESENT", s, True))
            elif treatment == "DELETE":
                if s.state in (PRESENT, IDENT):
                    findings.append(("REPORT_REMAINING_RECORD", s))
                    remediation.append(("DELETE_RECORD", s))
                    verification.append(("VERIFY_RECORD_ABSENT", s, False))
                elif s.category == "USER_PROFILE" and s.state in (ABSENT, UNKNOWN):
                    verification.append(("VERIFY_RECORD_ABSENT", s, True))
            elif treatment in ("REDACT", "ANONYMIZE"):
                op = "REDACT" if treatment == "REDACT" else "ANONYMIZE"
                vop = "VERIFY_RECORD_REDACTED" if op == "REDACT" else "VERIFY_RECORD_ANONYMIZED"
                if s.state in (IDENT, PRESENT):
                    findings.append(("REPORT_EXPOSED_PII", s))
                    remediation.append((f"{op}_RECORD", s))
                    verification.append((vop, s, False))
                elif s.state == CLEAN:
                    verification.append((vop, s, True))
        incomplete = bool(findings)
        status = "INCOMPLETE" if incomplete else "COMPLETE"
        steps = []
        if incomplete:
            # account must be verified absent even when it was already gone
            items = [(op, s, "evidence") for op, s in findings]
            items += [(op, s, "") for op, s in remediation]
            items += [(op, s, "") for op, s, _ in verification]
        else:
            items = [(op, s, "evidence") for op, s, _ in verification]
        def key(it):
            op, s, _ = it
            return (OP_ORDER.index(op), s.system_id, s.resource_id)
        phases = {"FINDING": [], "REMEDIATION": [], "VERIFICATION": []}
        seen = set()
        for it in sorted(items, key=key):
            op, s, evflag = it
            k = (op, s.resource_id)
            if k in seen:
                continue
            seen.add(k)
            phases[OP_META[op][0]].append(it)
        n = 0
        for ph in ("FINDING", "REMEDIATION", "VERIFICATION"):
            for op, s, evflag in phases[ph]:
                n += 1
                steps.append({"step_no": n, "phase": ph, "system_id": s.system_id, "resource_id": s.resource_id,
                              "operation": op, "state": OP_META[op][1],
                              "evidence_id": s.evidence_id if evflag else ""})
        return status, steps, trace

    def _coverage_state(self, rid, system, audit_at):
        """Absence proof from the latest non-empty snapshot that covers `system`."""
        nonempty = {o.evidence_id for o in self.store.observations}
        cov = [c for c in self.store.coverage if c[1] == system and c[2] <= audit_at
               and self.store.manifest[c[0]]["captured_at"] <= audit_at and c[0] in nonempty]
        if not cov:
            return None
        eid, _, cap, rids = max(cov, key=lambda c: (c[2], c[0]))
        return (PRESENT if rid in rids else ABSENT), eid

    def _fallback_account(self, ident: Identity, audit_at: str):
        """Account id not observed directly: look for a source_resource_id reference, else derive
        from the stable user number, and prove absence from the latest account snapshot."""
        rid = None
        for o in self.store.observations:
            src = o.fields.get("source_resource_id")
            if src and src.startswith("account_") and links_to(o, ident):
                rid = src
        if rid is None:
            m = re.match(r"user_(\d+)$", ident.user_id)
            if not m:
                return None
            rid = f"account_{int(m.group(1)):03d}"
        cov = self._coverage_state(rid, "account_service", audit_at)
        if not cov:
            return ResourceState("account_service", rid, "USER_PROFILE", ABSENT, "", "")
        return ResourceState("account_service", rid, "USER_PROFILE", cov[0], cov[1], audit_at)
