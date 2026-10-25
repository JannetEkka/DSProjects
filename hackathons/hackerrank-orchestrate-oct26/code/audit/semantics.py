"""Observation semantics: what one observation says about a resource (category + state), and
whether it carries a subject's identifier. Pure functions, no engine state."""
from __future__ import annotations

import re

from .evidence import Observation, resource_prefix
from .identity import Identity

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
