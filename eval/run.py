"""Measure Chithi on the synthetic letters: how many wrong dates and amounts
reach the reader as fact, and how many points are held back.

    python eval/run.py --backend mock            # no key; measures the check alone
    python eval/run.py --backend live --n 12     # Meta's models; costs about $0.02 a letter

A value "shown" is a date or number in a verified point. It is wrong if it is
not on the letter (compared with the generator's true text, not with what the
model read). The result goes to eval/results-<backend>.json and is printed as a
table for the README.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from chithi import agent, values  # noqa: E402
from chithi.mock import MockBackend  # noqa: E402

LANGS = ["bn", "hi", "en"]


def score(result, truth) -> dict:
    true_values = {values.key(f) for f in values.find_values(truth["text"])}
    row = {"id": truth["id"], "language": result.language, "verified": len(result.verified),
           "check_yourself": len(result.check_yourself), "shown": 0, "wrong_shown": 0, "wrong_held_back": 0,
           "wrong_examples": [], "cost_usd": result.cost_usd}
    for p in result.verified:
        for f in values.find_values(p["say"]):
            row["shown"] += 1
            if values.key(f) not in true_values:
                row["wrong_shown"] += 1
                row["wrong_examples"].append({"say": p["say"], "value": f.text})
    for p in result.check_yourself:
        row["wrong_held_back"] += sum(values.key(f) not in true_values for f in values.find_values(p["say"]))
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["mock", "live", "live-open"], default="mock")
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--no-repair", action="store_true")
    args = ap.parse_args()

    letters = sorted((ROOT / "letters" / "out").glob("*.json"))[: args.n]
    rows = []
    for i, path in enumerate(letters):
        truth = json.loads(path.read_text())
        lang = LANGS[i % len(LANGS)]
        if args.backend == "mock":
            backend = MockBackend(truth, seed=i)
        else:
            backend = agent.LiveBackend("spark-open" if args.backend == "live-open" else "spark")
        photo = (path.parent / f"{truth['id']}.photo.jpg").read_bytes()
        t = time.time()
        try:
            res = agent.run(photo, lang, backend, repair=not args.no_repair)
        except Exception as e:  # keep going; a failed letter is reported, not hidden
            rows.append({"id": truth["id"], "language": lang, "error": str(e)[:300]})
            print(f"{truth['id']} {lang}: ERROR {e}")
            continue
        row = score(res, truth)
        row["seconds"] = round(time.time() - t, 1)
        rows.append(row)
        print(f"{row['id']} {lang}: {row['verified']} verified, {row['check_yourself']} held back, "
              f"{row['wrong_shown']} wrong shown of {row['shown']}")

    ok = [r for r in rows if "error" not in r]
    total = {k: sum(r[k] for r in ok) for k in ["verified", "check_yourself", "shown", "wrong_shown", "wrong_held_back"]}
    total.update(letters=len(rows), errors=len(rows) - len(ok), cost_usd=round(sum(r["cost_usd"] for r in ok), 4))
    out = ROOT / "eval" / f"results-{args.backend}{'-norepair' if args.no_repair else ''}.json"
    out.write_text(json.dumps({"total": total, "letters": rows}, ensure_ascii=False, indent=1))
    pts = total["verified"] + total["check_yourself"]
    print(f"\n| letters | points | verified | held back | values shown | wrong values shown | wrong values held back | cost |")
    print(f"|---|---|---|---|---|---|---|---|")
    print(f"| {total['letters']} | {pts} | {total['verified']} | {total['check_yourself']} | {total['shown']} | "
          f"{total['wrong_shown']} | {total['wrong_held_back']} | ${total['cost_usd']} |")
    print(f"\nwrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
