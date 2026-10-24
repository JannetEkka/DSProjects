"""Ghost Data Still Exists - deletion audit agent.

Usage (from the repository root):
    python3 code/main.py                       # audit dataset/deletion_requests.csv -> ./output.csv
    python3 code/main.py --requests dataset/sample_deletion_requests.csv --out code/evaluation/sample_predictions.csv
    python3 code/main.py --no-llm              # fully offline (rules + local OCR only)

Pipeline per request:
  1. intent      - does the text authorize deletion? (Gemini JSON classifier + multilingual rule model)
  2. identity    - resolve current + historical emails / phones / hashes from identities + audit log
  3. evidence    - every file under dataset/evidence normalized into time-stamped observations
                   (SQL replicas, JSON exports, 6 log dialects, handover text, PDFs, screenshots via VLM/OCR)
  4. linking     - observations that carry the subject's identifiers, catalog links verified against the
                   artifact they came from, connector/restore lineage, and the request's own workflow jobs
  5. state       - each resource's state at audit_at (claims in workflow statuses are ignored)
  6. policy      - deletion_rules.csv applied per data category; ordered findings/remediation/verification
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit import usage  # noqa: E402
from audit.engine import AuditEngine, IdentityResolver  # noqa: E402
from audit.evidence import EvidenceStore  # noqa: E402
from audit.intent import IntentClassifier  # noqa: E402
from audit.media import MediaExtractor  # noqa: E402
from audit.validate import validate_output  # noqa: E402

ROOT = HERE.parent


def load_env_file():
    """Optional .env at repo root (never committed) for GEMINI_API_KEY."""
    import os

    p = ROOT / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))


def build(dataset: Path, use_llm: bool):
    t0 = time.time()
    media = MediaExtractor(prefer="auto" if use_llm else "ocr")
    store = EvidenceStore(dataset, media)
    engine = AuditEngine(dataset, store, IdentityResolver(dataset))
    intent = IntentClassifier(use_llm=use_llm)
    print(f"[load] {len(store.manifest)} evidence files -> {len(store.observations)} observations "
          f"({time.time() - t0:.1f}s); parse errors: {len(store.parse_errors)}")
    return store, engine, intent


def run(requests_path: Path, out_path: Path, dataset: Path, use_llm: bool, trace_path: Path | None):
    store, engine, intent = build(dataset, use_llm)
    cases = list(csv.DictReader(open(requests_path, newline="", encoding="utf-8")))
    # all known requests (evaluation + sample) give the global view needed to attribute shared workflow jobs
    universe = {}
    for p in (dataset / "deletion_requests.csv", dataset / "sample_deletion_requests.csv", requests_path):
        if p.exists():
            for r in csv.DictReader(open(p, newline="", encoding="utf-8")):
                universe[r["case_id"]] = r
    intent.prefetch(r["request_text"] for r in universe.values())
    intents = {cid: intent.classify(r["request_text"]) for cid, r in universe.items()}
    engine.prepare([r for cid, r in universe.items() if intents[cid]["authorizes_deletion"]])

    rows, traces = [], []
    for c in sorted(cases, key=lambda r: _case_key(r["case_id"])):
        it = intents[c["case_id"]]
        if not it["authorizes_deletion"]:
            status, steps, trace = "NOT_APPLICABLE", [], {"resources": []}
        else:
            status, steps, trace = engine.audit(c)
        rows.append({"case_id": c["case_id"], "deletion_status": status,
                     "steps_json": json.dumps(steps, ensure_ascii=False, separators=(",", ":"))})
        traces.append({"case_id": c["case_id"], "email": c["email"], "status": status, "intent": it, **trace,
                       "steps": steps})

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["case_id", "deletion_status", "steps_json"])
        w.writeheader()
        w.writerows(rows)
    if trace_path:
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        with open(trace_path, "w", encoding="utf-8") as f:
            for t in traces:
                f.write(json.dumps(t, ensure_ascii=False, default=str) + "\n")

    problems = validate_output(out_path, requests_path, store.manifest, engine)
    counts = {}
    for r in rows:
        counts[r["deletion_status"]] = counts.get(r["deletion_status"], 0) + 1
    print(f"[done] {len(rows)} rows -> {out_path}  {counts}")
    print(f"[validate] {'OK' if not problems else str(len(problems)) + ' problem(s)'}")
    for p in problems[:20]:
        print("   -", p)
    calls, hits = usage.snapshot()
    print(f"[usage] model calls: {json.dumps(calls)}  cache hits: {hits}")
    usage_path = out_path.with_suffix(".usage.json")
    usage_path.write_text(json.dumps({"requests": len(rows), "calls": calls, "cache_hits": hits}, indent=1))
    return rows, traces


def _case_key(cid: str):
    try:
        return (0, int(cid.split("_")[1]))
    except (IndexError, ValueError):
        return (1, cid)


def main():
    load_env_file()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", default=str(ROOT / "dataset"))
    ap.add_argument("--requests", default=None, help="requests CSV (default: dataset/deletion_requests.csv)")
    ap.add_argument("--out", default=str(ROOT / "output.csv"))
    ap.add_argument("--trace", default=None, help="JSONL explainability trace (default: <out>.trace.jsonl)")
    ap.add_argument("--no-llm", action="store_true", help="offline mode: rule intent model + local OCR")
    a = ap.parse_args()
    dataset = Path(a.dataset)
    req = Path(a.requests) if a.requests else dataset / "deletion_requests.csv"
    out = Path(a.out)
    trace = Path(a.trace) if a.trace else out.with_suffix(".trace.jsonl")
    run(req, out, dataset, not a.no_llm, trace)


if __name__ == "__main__":
    main()
