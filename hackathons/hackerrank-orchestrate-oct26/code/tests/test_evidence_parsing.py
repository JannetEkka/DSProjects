"""All six log dialects normalize to the same (timestamp, fields) shape."""
import pytest

from audit.evidence import parse_kv, parse_log_line

TS = "2026-05-14T11:51:20Z"
CASES = {
    "logfmt": f'{TS} level=INFO service=account_service trace_id=tr-1 resource_id=account_1 event=profile_lookup_completed rows=0',
    "json": f'{TS} {{"severity":"INFO","logger":"account_service","trace_id":"tr-1","resource_id":"account_1","event":"profile_lookup_completed"}}',
    "rfc5424": f'{TS} <15>1 node-8 account_service tr-1 - - level=INFO resource_id="account_1" event="profile_lookup_completed"',
    "bracketed": f'{TS} [INFO] [account_service] [tr-1] profile_lookup_completed: resource_id="account_1" rows="0"',
    "pipe": f'{TS} | INFO | account_service | tr-1 | profile_lookup_completed | resource_id="account_1" rows="0"',
    "cloud": f'{TS} requestId=tr-1 level=INFO function=account_service message="resource_id=\\"account_1\\" event=\\"profile_lookup_completed\\""',
}


@pytest.mark.parametrize("dialect", sorted(CASES))
def test_dialects_normalize(dialect):
    ts, d = parse_log_line(CASES[dialect])
    assert ts == TS
    assert d["service"] == "account_service"
    assert d["trace_id"] == "tr-1"
    assert d["resource_id"] == "account_1"
    assert d["event"] == "profile_lookup_completed"


def test_rfc5424_field_order():
    # <pri>version host app procid msgid: app is the service, procid the trace (a past bug swapped them)
    _, d = parse_log_line(f"{TS} <15>1 node-8 log_router collector-7 - - event=\"export_started\"")
    assert (d["service"], d["trace_id"]) == ("log_router", "collector-7")


def test_non_log_lines_are_ignored():
    assert parse_log_line("not a log line") is None
    assert parse_log_line("") is None


def test_kv_quoting():
    d = parse_kv('a=1 b="two words" c="esc \\"q\\""')
    assert d["b"] == "two words"
    assert "q" in d["c"]
