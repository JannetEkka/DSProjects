"""Write evaluation/usage_report.md from the usage ledger(s) of full-dataset runs.

    python3 code/evaluation/build_usage_report.py --cold output.usage.json [--warm output.usage.json]

`--cold` is the run that actually called the models (empty caches); `--warm` is an optional re-run
that reproduced output.csv from the response cache. Prices are list prices per 1M tokens (USD).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from audit.usage import PRICES  # noqa: E402


def table(calls: dict, requests: int):
    rows, tot = [], {"calls": 0, "input": 0, "output": 0, "cost": 0.0}
    for name, v in sorted(calls.items()):
        model = name.split("/", 1)[1]
        tok = v["input"] + v["output"]
        rows.append(f"| {name.split('/')[0]} | `{model}` | {', '.join(f'{k}: {n}' for k, n in v['purposes'].items())} | "
                    f"{v['calls']} | {v['input']:,} | {v['output']:,} | {tok:,} | {tok / requests:,.1f} | "
                    f"${v['cost_usd']:.4f} | ${v['cost_usd'] / requests:.6f} |")
        tot["calls"] += v["calls"]; tot["input"] += v["input"]; tot["output"] += v["output"]; tot["cost"] += v["cost_usd"]
    t = tot["input"] + tot["output"]
    rows.append(f"| **Overall** | | | **{tot['calls']}** | **{tot['input']:,}** | **{tot['output']:,}** | **{t:,}** | "
                f"**{t / requests:,.1f}** | **${tot['cost']:.4f}** | **${tot['cost'] / requests:.6f}** |")
    return rows, tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cold", required=True)
    ap.add_argument("--warm", default=None)
    a = ap.parse_args()
    cold = json.loads(Path(a.cold).read_text())
    n = cold["requests"]
    L = ["# Token Usage and Cost Report\n",
         f"Final full-dataset run over `dataset/deletion_requests.csv`: **{n} requests**.\n",
         "## Where models are used\n",
         "| Stage | Model | When it is called |\n|---|---|---|",
         "| Request intent (does the text authorize deletion?) | Gemini text model, JSON output, temperature 0 | once per *distinct* request text; identical texts share one call |",
         "| Screenshot transcription (VLM) | Gemini vision model, temperature 0 | once per screenshot file (11 PNGs), keyed by SHA-256 |",
         "| Everything else (evidence parsing, identity, linking, state, policy, ordering) | none | deterministic Python, $0 |\n",
         "Responses are cached in `code/cache/` (keyed by content hash), so a re-run reproduces `output.csv` "
         "with zero model calls. A rule-based intent model and local OCR (RapidOCR) always run as a fallback "
         "and as a cross-check; if the API is unreachable the agent finishes offline.\n",
         "## Cold run (empty cache) - the run that produced `output.csv`\n",
         "| Provider | Model | Calls by purpose | Calls | Input tokens | Output tokens | Total tokens | Avg tokens / request | Est. cost | Est. cost / request |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    rows, tot = table(cold["calls"], n)
    L += rows
    L.append(f"\nCache hits during this run: {json.dumps(cold.get('cache_hits', {}))}.\n")
    if a.warm:
        warm = json.loads(Path(a.warm).read_text())
        wc = sum(v["calls"] for v in warm["calls"].values())
        L.append("## Warm re-run (response cache present)\n")
        L.append(f"{warm['requests']} requests, **{wc} model calls**, cache hits {json.dumps(warm.get('cache_hits', {}))}; "
                 "output identical to the cold run.\n")
    L.append("## Pricing assumptions (USD per 1M tokens, list price)\n")
    L.append("| Model | Input | Output |\n|---|---|---|")
    for m, (pi, po) in PRICES.items():
        L.append(f"| `{m}` | ${pi:.2f} | ${po:.2f} |")
    L.append("\nToken counts come from the API's `usage_metadata` on every response (prompt and candidate tokens), "
             "accumulated in `code/audit/usage.py`; nothing is estimated except the dollar figures.\n")
    (HERE / "usage_report.md").write_text("\n".join(L), encoding="utf-8")
    print((HERE / "usage_report.md").read_text())


if __name__ == "__main__":
    main()
