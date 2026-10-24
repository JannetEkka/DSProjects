"""State reconstruction at `audit_at` and policy planning: deletion_rules.csv applied per category,
steps ordered FINDING -> REMEDIATION -> VERIFICATION."""
from __future__ import annotations

import re
from dataclasses import dataclass

from .evidence import system_for
from .identity import Identity
from .semantics import (ABSENT, ACTIVE, CLEAN, DISABLED, IDENT, PRESENT, PREFIX_CATEGORY, UNKNOWN, classify,
                        links_to, resource_prefix)

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


@dataclass
class ResourceState:
    system_id: str
    resource_id: str
    category: str
    state: str
    evidence_id: str
    time: str



class PlannerMixin:
    """Expects `by_resource`, `store`, `rules`, `rule_rows`, `ids` and the linking/workflow mixins."""

    def state_at(self, rid: str, audit_at: str) -> tuple[str | None, str, str, str]:
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
        trace = {"user_id": ident.user_id if ident else None, "resources": [],
                 "identity": ({"emails": sorted(ident.emails), "phones": sorted(ident.phones),
                               "hashes": sorted(ident.hashes), "names": sorted(ident.names),
                               "audit_ids": ident.audit_ids} if ident else {}),
                 "era_start": "", "workflow": {}}
        adhoc = ident is None
        if adhoc:
            # unknown address: link only on the literal email (no workflow attribution, no derived
            # account id - nothing ties a workflow job or a scrubbed record to an unregistered person)
            ident = self.ids.adhoc(case["email"])
            trace["identity"] = {"emails": sorted(ident.emails), "source": "request email only"}
        trace["era_start"] = "" if adhoc else self.era_start(case, ident)
        linked = self.linked_resources(ident, audit_at, trace["era_start"])
        if adhoc and not linked:
            # No customer and no record matches the address, so no personal data is in deletion
            # scope and nothing can be verified. COMPLETE needs evidence-backed verification steps
            # and INCOMPLETE needs evidenced findings; the only contract-valid row is
            # NOT_APPLICABLE with [] (reason kept in the trace).
            trace["not_applicable_reason"] = "unresolved identity: no customer or record matches the request email"
            return "NOT_APPLICABLE", [], trace
        wf = {} if adhoc else self.workflow_resources(case, ident, linked)
        trace["workflow"] = wf
        for rid, src in wf.items():
            linked.setdefault(rid, []).append(src)
        findings, remediation, verification = [], [], []
        states = []
        for rid in sorted(linked):
            cat, st, ev, t = self.state_at(rid, audit_at)
            states.append(ResourceState(system_for(rid), rid, cat, st, ev, t))
        has_account = any(s.category == "USER_PROFILE" for s in states)
        if not has_account and not adhoc:
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
            rr = self.rule_rows.get(s.category or "", {})
            trace["resources"].append({**s.__dict__,
                                       "linked_by": sorted(set(linked.get(s.resource_id, []))),
                                       "rule_id": rr.get("rule_id", ""), "rule_action": rr.get("required_action", "DISABLE" if s.category == "DATA_FLOW" else ""),
                                       "rule_condition": rr.get("condition", "Active process can recreate data" if s.category == "DATA_FLOW" else "")})
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
