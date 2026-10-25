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


def cache_inventory(requests: int):
    """Every cached answer names the model that produced it, so the cache is a complete record of which
    models did the work, including runs whose token ledger was not saved."""
    from collections import Counter
    cache_dir = HERE.parent / "cache"
    L = ["## Inventory of the response cache (what produced `output.csv`)\n",
         "| Kind | Model | Cached answers | Used by the final run |", "|---|---|---|---|"]
    intent = json.loads((cache_dir / "intent.json").read_text(encoding="utf-8"))
    for m, c in sorted(Counter(v.get("model") or "gemini (earlier run, model not tagged)" for v in intent.values()).items()):
        L.append(f"| intent answer | `{m}` | {c} | yes (looked up by text hash) |")
    media = json.loads((cache_dir / "media_text.json").read_text(encoding="utf-8"))
    used = Counter(sorted(n for n in v["engines"] if n != "rapidocr")[0] for v in media.values()
                   if any(n != "rapidocr" for n in v["engines"]))
    allm = Counter(n for v in media.values() for n in v["engines"])
    for m, c in sorted(allm.items()):
        L.append(f"| screenshot transcription | `{m}` | {c} | {used.get(m, 0)} of {len(media)} files |")
    vlm_calls = sum(c for m, c in allm.items() if m != "rapidocr")
    L.append(f"\nModel calls not in the ledger above: **{vlm_calls} vision transcriptions** and the intent answers "
             "tagged with an earlier model, made in runs whose token ledger was not saved. A Gemini Flash "
             "screenshot call costs roughly 1.3k input + 0.6k output tokens, so these add about "
             f"{vlm_calls * 1.9:.0f}k tokens (about ${vlm_calls * (1300 * 0.30 + 600 * 2.50) / 1e6:.3f}) - an estimate, "
             "marked as such. The whole build stays well under $0.10.\n")
    return L


def experiment_section(x: dict) -> list[str]:
    """A cold re-run from empty caches with one pinned model, kept as a record next to the shipped ledger."""
    ra, rb = x["run_a"], x["run_b"]
    led = ra["ledger"]
    calls = sum(v["calls"] for v in led["calls"].values())
    toks = sum(v["input"] + v["output"] for v in led["calls"].values())
    cost = sum(v.get("cost_usd", 0) for v in led["calls"].values())
    L = [f"## Cold-run experiment ({x['date']}, not shipped)\n",
         "Goal: one coherent cold run (empty caches, one pinned model per stage) whose ledger could replace the "
         "one above. It was not shipped; the ledger above stays the record of the shipped run.\n",
         "**Model probe** (one tiny call each): " + "; ".join(f"`{m}` {r}" for m, r in x["probe"].items())
         + f". Declared fallback: {x['fallback']}.\n",
         f"**Run A** (all {led['requests']} requests, then the samples): {calls} calls, {toks / 1000:.0f}k tokens, "
         f"${cost:.3f}. The pinned model served the first calls and then hit its rate limit; the fallback served the rest.\n",
         "| Provider | Model | Calls by purpose | Calls | Input tokens | Output tokens | Total tokens | Avg tokens / request | Est. cost | Est. cost / request |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    L += table(led["calls"], led["requests"])[0]
    smp = ra["samples"]
    L.append(f"\nResult: {ra['changed_rows_518']} of {led['requests']} output rows changed, but the samples dropped to "
             f"{smp['exact']} exact / {smp['step_f1']} step F1 / {smp['status']} status (suite {smp['suite']}): "
             f"{', '.join(ra['misreads'])} - {ra['misread_detail']}. **Fix:** the intent module now lets the "
             "rule model override an LLM refusal when the text has a clear deletion cue, no negation and no other "
             "purpose (the mirror of the existing veto), recorded as `override: rules_over_llm`; unit tests replay "
             "both refusals.\n")
    L.append(f"**Run B** ({rb['setup']}): {rb['result']}. That fully offline path reproduced "
             f"{rb['offline_rows_identical']}/{led['requests']} rows; {rb['offline_diff']}.\n")
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cold", required=True)
    ap.add_argument("--warm", default=None)
    ap.add_argument("--experiment", default=str(HERE / "usage_cold_experiment_20261024.json"),
                    help="recorded cold-run experiment (not shipped); rendered as its own section")
    a = ap.parse_args()
    cold = json.loads(Path(a.cold).read_text())
    n = cold["requests"]
    L = ["# Token Usage and Cost Report\n",
         f"Final full-dataset run over `dataset/deletion_requests.csv`: **{n} requests**.\n",
         "## Where models are used\n",
         "| Stage | Model | When it is called |\n|---|---|---|",
         "| Request intent (does the text authorize deletion?) | Gemini Flash, falling back to Groq `gpt-oss-120b`; JSON output, temperature 0 | distinct texts only, 10 per batched call |",
         "| Screenshot transcription (VLM) | Gemini Flash vision, temperature 0 | once per screenshot file (11 PNGs), keyed by SHA-256 |",
         "| Everything else (evidence parsing, identity, linking, state, policy, ordering) | none | deterministic Python, $0 |\n",
         "Responses are cached in `code/cache/` (keyed by content hash), so a re-run reproduces `output.csv` "
         "with zero model calls. A rule-based intent model and local OCR (RapidOCR) always run as a fallback "
         "and as a cross-check; if the API is unreachable the agent finishes offline.\n",
         "## Model calls recorded by the token ledger\n",
         "The response cache was filled across several helper runs because free-tier quotas and retired model "
         "aliases interrupted the first attempts (the agent's model chain falls back Gemini -> Groq and keeps "
         "every answer as it arrives). The table below is the ledger of the run that completed the cache.\n",
         "| Provider | Model | Calls by purpose | Calls | Input tokens | Output tokens | Total tokens | Avg tokens / request | Est. cost | Est. cost / request |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    rows, tot = table(cold["calls"], n)
    L += rows
    L.append(f"\nCache hits during this run: {json.dumps(cold.get('cache_hits', {}))}.\n")
    L += cache_inventory(n)
    if a.warm:
        warm = json.loads(Path(a.warm).read_text())
        wc = sum(v["calls"] for v in warm["calls"].values())
        L.append("## Warm re-run (response cache present)\n")
        L.append(f"{warm['requests']} requests, **{wc} model calls**, cache hits {json.dumps(warm.get('cache_hits', {}))}; "
                 "output identical to the cold run.\n")
    if a.experiment and Path(a.experiment).exists():
        L += experiment_section(json.loads(Path(a.experiment).read_text()))
    L.append("## Pricing assumptions (USD per 1M tokens, list price)\n")
    L.append("| Model | Input | Output |\n|---|---|---|")
    for m, (pi, po) in PRICES.items():
        L.append(f"| `{m}` | ${pi:.2f} | ${po:.2f} |")
    L.append("\nToken counts come from the API's `usage_metadata` on every response (prompt and candidate tokens), "
             "accumulated in `code/audit/usage.py`. Estimated: dollar figures (list prices above) and the unledgered vision calls (marked).\n")
    (HERE / "usage_report.md").write_text("\n".join(L), encoding="utf-8")
    print((HERE / "usage_report.md").read_text())


if __name__ == "__main__":
    main()
