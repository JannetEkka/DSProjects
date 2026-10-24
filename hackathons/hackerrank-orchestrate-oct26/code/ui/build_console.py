"""Build the Ghost Ledger audit console: a single self-contained HTML file.

    python3 code/ui/build_console.py            # reads output.trace.jsonl -> code/ui/ghost_ledger.html

The console embeds the run's explainability trace (no server, no network) so a reviewer can open
any case and see: claim vs. audited reality, the subject's identifiers (masked by default), a
timeline of the evidence, the resource map, and every step with the evidence and policy rule behind it.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def build(trace_path: Path, dataset: Path, requests_path: Path, out_path: Path, body_only_path: Path | None):
    traces = [json.loads(l) for l in open(trace_path, encoding="utf-8")]
    reqs = {r["case_id"]: r for r in csv.DictReader(open(requests_path, newline="", encoding="utf-8-sig"))}
    manifest = {r["file_id"]: r for r in csv.DictReader(open(dataset / "evidence_files.csv", newline="", encoding="utf-8-sig"))}
    acts = {r["activity_id"]: r for r in csv.DictReader(open(dataset / "system_activity.csv", newline="", encoding="utf-8-sig"))}
    rules = list(csv.DictReader(open(dataset / "deletion_rules.csv", newline="", encoding="utf-8-sig")))

    cited = set()
    cases = []
    for t in traces:
        r = reqs.get(t["case_id"], {})
        for res in t.get("resources", []):
            cited.add(res.get("evidence_id", ""))
            cited.update(res.get("linked_by", []))
        cases.append({
            "id": t["case_id"], "email": t["email"], "status": t["status"],
            "claim": r.get("reported_status", ""), "requested": r.get("requested_at", ""),
            "reported": r.get("reported_at", ""), "audit": r.get("audit_at", ""), "text": r.get("request_text", ""),
            "intent": t.get("intent", {}), "user": t.get("user_id"), "identity": t.get("identity", {}),
            "era": t.get("era_start", ""), "workflow": t.get("workflow", {}),
            "res": [{k: v for k, v in x.items() if k != "time"} | {"t": x.get("time", "")} for x in t.get("resources", [])],
            "steps": t.get("steps", []),
        })
    ev = {}
    for e in cited:
        if e in manifest:
            m = manifest[e]
            ev[e] = {"k": "file", "path": m["file_path"], "origin": m["origin"], "at": m["captured_at"]}
        elif e in acts:
            a = acts[e]
            ev[e] = {"k": "activity", "type": a["event_type"], "at": a["event_time"], "detail": a["details"],
                     "result": a["reported_result"]}
    data = {"cases": cases, "evidence": ev, "rules": rules,
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "source": requests_path.name}
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    body = (HERE / "console_template.html").read_text(encoding="utf-8").replace("__DATA__", payload)
    out_path.write_text("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
                        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">"
                        "</head><body>\n" + body + "\n</body></html>\n", encoding="utf-8")
    if body_only_path:
        body_only_path.write_text(body, encoding="utf-8")
    print(f"[console] {len(cases)} cases -> {out_path} ({out_path.stat().st_size / 1e6:.2f} MB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", default=str(ROOT / "output.trace.jsonl"))
    ap.add_argument("--dataset", default=str(ROOT / "dataset"))
    ap.add_argument("--requests", default=None)
    ap.add_argument("--out", default=str(HERE / "ghost_ledger.html"))
    ap.add_argument("--body-only", default=None, help="also write the page body without the html skeleton")
    a = ap.parse_args()
    ds = Path(a.dataset)
    build(Path(a.trace), ds, Path(a.requests) if a.requests else ds / "deletion_requests.csv", Path(a.out),
          Path(a.body_only) if a.body_only else None)


if __name__ == "__main__":
    main()
