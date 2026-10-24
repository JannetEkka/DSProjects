"""Contract validator: checks output.csv against every machine-checkable rule in problem_statement.md."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from .engine import OP_META, OP_ORDER

PHASES = ["FINDING", "REMEDIATION", "VERIFICATION"]
KEYS = {"step_no", "phase", "system_id", "resource_id", "operation", "state", "evidence_id"}


def validate_output(out_path: Path, requests_path: Path, manifest: dict, engine=None) -> list[str]:
    problems = []
    with open(out_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        if header != ["case_id", "deletion_status", "steps_json"]:
            problems.append(f"bad header {header}")
        rows = list(reader)
    req = {r["case_id"]: r for r in csv.DictReader(open(requests_path, newline="", encoding="utf-8"))}
    ids = [r[0] for r in rows]
    if sorted(ids) != sorted(req):
        problems.append(f"case ids differ from requests ({len(ids)} vs {len(req)})")
    if len(set(ids)) != len(ids):
        problems.append("duplicate case ids")
    key = lambda c: int(c.split("_")[1]) if c.split("_")[-1].isdigit() else c
    if ids != sorted(ids, key=key):
        problems.append("rows not sorted by case_id")
    activity_ids = {a["activity_id"]: a for a in engine.activities} if engine else {}
    audit_ids = {h["audit_id"]: h for h in engine.ids.history} if engine else {}
    for cid, status, sj in rows:
        audit_at = req.get(cid, {}).get("audit_at", "")
        try:
            steps = json.loads(sj)
        except json.JSONDecodeError as e:
            problems.append(f"{cid}: steps_json not JSON ({e})")
            continue
        if status not in ("COMPLETE", "INCOMPLETE", "NOT_APPLICABLE"):
            problems.append(f"{cid}: bad status {status}")
        if status == "NOT_APPLICABLE" and steps != []:
            problems.append(f"{cid}: NOT_APPLICABLE must have []")
        if status != "NOT_APPLICABLE" and not steps:
            problems.append(f"{cid}: {status} with no steps")
        last = (-1, -1)
        for i, s in enumerate(steps, 1):
            if set(s) != KEYS:
                problems.append(f"{cid}#{i}: keys {sorted(s)}")
                continue
            if s["step_no"] != i:
                problems.append(f"{cid}#{i}: step_no {s['step_no']}")
            if s["operation"] not in OP_META or OP_META[s["operation"]] != (s["phase"], s["state"]):
                problems.append(f"{cid}#{i}: op/phase/state mismatch {s['operation']} {s['phase']} {s['state']}")
                continue
            order = (PHASES.index(s["phase"]), OP_ORDER.index(s["operation"]))
            if order < last:
                problems.append(f"{cid}#{i}: out of order")
            last = order
            ev = s["evidence_id"]
            if status == "COMPLETE":
                if s["phase"] != "VERIFICATION":
                    problems.append(f"{cid}#{i}: COMPLETE may only contain verification")
                if not ev:
                    problems.append(f"{cid}#{i}: COMPLETE verification without evidence")
            if status == "INCOMPLETE":
                if s["phase"] == "FINDING" and not ev:
                    problems.append(f"{cid}#{i}: finding without evidence")
                if s["phase"] != "FINDING" and ev:
                    problems.append(f"{cid}#{i}: future step must have empty evidence_id")
            if ev:
                if ev in manifest:
                    seen_before = engine is None or any(
                        o.evidence_id == ev and o.time <= audit_at for o in engine.by_resource.get(s["resource_id"], []))
                    if manifest[ev]["captured_at"] > audit_at and not seen_before:
                        problems.append(f"{cid}#{i}: cites {ev} with no observation at or before audit_at")
                elif ev in activity_ids:
                    if activity_ids[ev]["event_time"] > audit_at:
                        problems.append(f"{cid}#{i}: cites {ev} after audit_at")
                elif ev not in audit_ids:
                    problems.append(f"{cid}#{i}: unknown evidence id {ev}")
    return problems
