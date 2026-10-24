"""Policy -> ordered steps on real cases, and the contract validator catching each violation."""
import csv
import json

import pytest

from audit.planner import OP_META, OP_ORDER
from audit.validate import validate_output

PHASES = ["FINDING", "REMEDIATION", "VERIFICATION"]
HEADER = ["case_id", "deletion_status", "steps_json"]
REQ = {"case_id": "case_1", "email": "x@example.com", "requested_at": "2026-01-01T00:00:00Z",
       "reported_status": "COMPLETE", "reported_at": "2026-01-02T00:00:00Z", "audit_at": "2026-02-01T00:00:00Z",
       "request_text": "delete my account"}
MANIFEST = {"evidence_1": {"captured_at": "2026-01-15T00:00:00Z"}, "evidence_late": {"captured_at": "2026-03-01T00:00:00Z"}}


def step(n, op, rid="account_1", ev="evidence_1", system="account_service"):
    phase, state = OP_META[op]
    return {"step_no": n, "phase": phase, "system_id": system, "resource_id": rid, "operation": op,
            "state": state, "evidence_id": ev}


def run_validator(tmp_path, status, steps, header=HEADER):
    out, req = tmp_path / "out.csv", tmp_path / "req.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerow(["case_1", status, json.dumps(steps)])
    with open(req, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(REQ))
        w.writeheader()
        w.writerow(REQ)
    return validate_output(out, req, MANIFEST, None)


def test_valid_rows_pass(tmp_path):
    assert run_validator(tmp_path, "COMPLETE", [step(1, "VERIFY_RECORD_ABSENT")]) == []
    assert run_validator(tmp_path, "NOT_APPLICABLE", []) == []
    inc = [step(1, "REPORT_REMAINING_RECORD"), step(2, "DELETE_RECORD", ev=""), step(3, "VERIFY_RECORD_ABSENT", ev="")]
    assert run_validator(tmp_path, "INCOMPLETE", inc) == []


@pytest.mark.parametrize("status, steps, needle", [
    ("DONE", [step(1, "VERIFY_RECORD_ABSENT")], "bad status"),
    ("NOT_APPLICABLE", [step(1, "VERIFY_RECORD_ABSENT")], "must have []"),
    ("COMPLETE", [], "with no steps"),
    ("COMPLETE", [step(2, "VERIFY_RECORD_ABSENT")], "step_no"),
    ("COMPLETE", [{**step(1, "VERIFY_RECORD_ABSENT"), "state": "PRESENT"}], "mismatch"),
    ("COMPLETE", [step(1, "VERIFY_RECORD_ABSENT", ev="")], "without evidence"),
    ("COMPLETE", [step(1, "REPORT_REMAINING_RECORD")], "only contain verification"),
    ("INCOMPLETE", [step(1, "REPORT_REMAINING_RECORD", ev="")], "finding without evidence"),
    ("INCOMPLETE", [step(1, "REPORT_REMAINING_RECORD"), step(2, "DELETE_RECORD")], "future step"),
    ("INCOMPLETE", [step(1, "DELETE_RECORD", ev=""), step(2, "REPORT_REMAINING_RECORD")], "out of order"),
    ("COMPLETE", [step(1, "VERIFY_RECORD_ABSENT", ev="evidence_late")], "audit_at"),
    ("COMPLETE", [step(1, "VERIFY_RECORD_ABSENT", ev="evidence_nope")], "unknown evidence"),
    ("COMPLETE", [{k: v for k, v in step(1, "VERIFY_RECORD_ABSENT").items() if k != "state"}], "keys"),
])
def test_validator_catches(tmp_path, status, steps, needle):
    problems = run_validator(tmp_path, status, steps)
    assert any(needle in p for p in problems), problems


def test_validator_bad_header(tmp_path):
    assert any("bad header" in p for p in run_validator(tmp_path, "NOT_APPLICABLE", [], ["id", "status", "steps"]))


def test_planner_orders_phases_and_operations(engine):
    """Every planned case is phase-ordered and follows OP_ORDER within a phase (sample of real cases)."""
    cases = list(csv.DictReader(open(engine.dataset_dir / "sample_deletion_requests.csv", encoding="utf-8-sig")))
    engine.prepare(cases)
    for c in cases[:12]:
        status, steps, _ = engine.audit(c)
        keys = [(PHASES.index(s["phase"]), OP_ORDER.index(s["operation"])) for s in steps]
        assert keys == sorted(keys), c["case_id"]
        assert [s["step_no"] for s in steps] == list(range(1, len(steps) + 1))
        if status == "COMPLETE":
            assert steps and all(s["phase"] == "VERIFICATION" and s["evidence_id"] for s in steps)
        else:
            assert any(s["phase"] == "FINDING" for s in steps)
            assert all(not s["evidence_id"] for s in steps if s["phase"] != "FINDING")
        sec = [s for s in steps if s["system_id"] == "security_service"]
        assert all(s["operation"] == "VERIFY_RECORD_PRESENT" for s in sec)  # retained, never deleted
