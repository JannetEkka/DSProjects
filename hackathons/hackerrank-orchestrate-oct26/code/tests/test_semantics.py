"""classify(): category and state per resource type."""
import pytest

from audit.evidence import Observation
from audit.identity import Identity
from audit.semantics import ABSENT, ACTIVE, CLEAN, DISABLED, IDENT, PRESENT, classify, links_to


def obs(rid, **fields):
    return Observation("evidence_x", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z", "sys", rid, "test", fields, set())


@pytest.mark.parametrize("o, expected", [
    (obs("account_1", http_status="404"), ("USER_PROFILE", ABSENT)),
    (obs("account_1", rows="1"), ("USER_PROFILE", PRESENT)),
    (obs("search_1", total_hits="0"), ("SEARCH_INDEX_ENTRY", ABSENT)),
    (obs("search_1", result="hit"), ("SEARCH_INDEX_ENTRY", PRESENT)),
    (obs("analytics_1", email=None, phone=None, user_id=None), ("ANALYTICS_PROFILE", CLEAN)),
    (obs("analytics_1", email="a@b.co"), ("ANALYTICS_PROFILE", IDENT)),
    (obs("tombstone_1", user_id="user_1", name=None, email=None), ("ACCOUNT_TOMBSTONE", CLEAN)),
    (obs("tombstone_1", email="a@b.co"), ("ACCOUNT_TOMBSTONE", IDENT)),
    (obs("support_1", message_text="call me on +44 7700 900123"), ("SUPPORT_MESSAGE", IDENT)),
    (obs("support_1", message_text="thanks", requester_email="[REDACTED]"), ("SUPPORT_MESSAGE", CLEAN)),
    (obs("support_1", event="attachment_uploaded", file_name="id.pdf"), ("SUPPORT_ATTACHMENT", PRESENT)),
    (obs("data_flow_1", enabled=True), ("DATA_FLOW", ACTIVE)),
    (obs("data_flow_1", enabled=False), ("DATA_FLOW", DISABLED)),
    (obs("backup_1", restore_allowed=True), ("BACKUP_ARCHIVE", ACTIVE)),
    (obs("backup_1", restore_allowed=False), ("BACKUP_ARCHIVE", DISABLED)),
    (obs("export_1", available=False), ("USER_EXPORT", ABSENT)),
    (obs("audit_record_1", rows="1"), ("SECURITY_AUDIT_LOG", PRESENT)),
    (obs("analytics_1", record_type="ANALYTICS_PROFILE", result="ANONYMIZED"), ("ANALYTICS_PROFILE", CLEAN)),
])
def test_classify(o, expected):
    assert classify(o) == expected


def test_links_to_exact_values_only():
    ident = Identity("user_9", {"g.silva76@gmail.com"})
    assert links_to(obs("search_1", owner_email="g.silva76@gmail.com"), ident)
    assert not links_to(obs("search_1", owner_email="g.silva76.jr@gmail.com"), ident)  # near-miss decoy
    assert not links_to(obs("search_1", owner_email="g.silva76@gmail.com", no_link=True), ident)
