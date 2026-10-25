"""Identity resolution through the audit log (historical emails, phones, hashes)."""
import csv

from audit.identity import IdentityResolver


def _write(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def make(tmp_path, bom=False):
    _write(tmp_path / "user_identities.csv", ["user_id", "name", "email", "phone", "email_hash", "updated_at"],
           [["user_7", "Ana Lima", "ana.new@example.com", "+1 555 0100", "h-new", "2026-01-01T00:00:00Z"],
            ["user_8", "Ana Lima", "other@example.com", "+1 555 0199", "h-other", "2026-01-01T00:00:00Z"]])
    _write(tmp_path / "user_audit_log.csv", ["audit_id", "user_id", "event_time", "field_name", "old_value", "new_value"],
           [["audit_1", "user_7", "2025-06-01T00:00:00Z", "email", "Ana.Old@Example.com", "ana.new@example.com"],
            ["audit_2", "user_7", "2025-07-01T00:00:00Z", "phone", "+1 555 0000", "+1 555 0100"]])
    if bom:
        p = tmp_path / "user_identities.csv"
        p.write_bytes(b"\xef\xbb\xbf" + p.read_bytes())
    return IdentityResolver(tmp_path)


def test_historical_email_resolves_to_same_user(tmp_path):
    ids = make(tmp_path)
    old = ids.resolve("ana.old@example.com")
    assert old.user_id == "user_7"
    assert {"ana.old@example.com", "ana.new@example.com"} <= old.emails
    assert {"+1 555 0000", "+1 555 0100"} <= old.phones
    assert old.audit_ids == ["audit_1", "audit_2"]


def test_email_is_case_and_space_insensitive(tmp_path):
    assert make(tmp_path).resolve("  ANA.NEW@EXAMPLE.COM ").user_id == "user_7"


def test_names_never_link(tmp_path):
    ident = make(tmp_path).resolve("ana.new@example.com")
    assert not ident.matches_value("Ana Lima")  # two customers share the name
    assert ident.mentioned_in("ticket from ana.old@example.com about a refund")


def test_unknown_email_and_adhoc_identity(tmp_path):
    ids = make(tmp_path)
    assert ids.resolve("nobody@example.com") is None
    ad = ids.adhoc(" Nobody@Example.com ")
    assert ad.emails == {"nobody@example.com"} and ad.user_id.startswith("unregistered:")


def test_bom_prefixed_csv(tmp_path):
    assert make(tmp_path, bom=True).resolve("ana.new@example.com").user_id == "user_7"
