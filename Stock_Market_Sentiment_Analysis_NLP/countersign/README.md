# Countersign

**Every claim checked before you read.** A weekly market brief about Apple where a claim is shown only if a second model, a calculation and a guardrail could all confirm it, and where everything that was removed stays visible with the reason.

**Who it helps:** anyone who publishes or reads summaries that a model wrote from source text and cannot reread every source. In our run about 1 claim in 14 had no support in the news it cited; the 2024 version of this project showed all of them as fact.

- **Use it:** https://countersign-6my.pages.dev, the "Check a text" screen. Paste a model-written summary and the text it was written from; each sentence is checked live and the unsupported ones are struck, with the reason.
- **See the work:** [`countersign.ipynb`](countersign.ipynb) has every figure and finding inline, built from the saved run.

Live page: https://countersign-6my.pages.dev · Built for the Mozilla Otari hackathon (Devs Wilding Online) on branch `otari-hackathon`. Every model call goes through the hosted [Otari](https://otari.ai) gateway.

## The side project this finishes

[Stock Market Sentiment Analysis](../README.md) (PGP in AI/ML, Nov–Dec 2024) classified 349 Apple-related headlines from Jan–Apr 2019 and wrote weekly summaries with Mistral-7B on a notebook GPU. Two things were left open, both written down in [the project note](../../projects/stock-sentiment-nlp.md) before this hackathon:

1. The summaries had no grounding check ("LLM summaries can invent facts").
2. Sentiment was weak: weighted F1 of 0.366 on the test split for the selected model.

## What changed, with the numbers

All numbers are from the run in [`runs/results.json`](runs/results.json) (2026-11-11), built by `pipeline.py`.

**The check.** Across all 18 weeks the writer model made 108 claims. The check removed 8 (7%): 5 because the checker model found the cited headlines did not support them, and 3 because the passage the checker quoted as support was not in the cited headline. Compared with the 2024 project, which showed every sentence its model wrote: a reader of these 18 briefs would have been shown those 8 claims as fact, and can now see which ones they were and why they failed.

Two checks found nothing, and that is reported too: no claim cited a headline that did not exist, and none of the price figures differed from the sandbox's recomputation.

**How good is the check itself?** Nobody has labelled the 108 claims, so the 18 briefs cannot say what the check misses. A public labelled set can. On [HaluEval](https://github.com/RUCAIBox/HaluEval)'s summarization data (60 news articles, fixed random sample, each with one faithful summary and one with a planted error; [`benchmark.py`](benchmark.py), result in [`runs/benchmark.json`](runs/benchmark.json)), the app's rule:

- caught **41 of 60** summaries with a planted error (68%), and missed 19;
- wrongly struck at least one sentence in **27 of 60** faithful summaries (42 of 223 faithful sentences, 19%).

So the check is strict and imperfect: it catches about two planted errors in three and strikes about one good sentence in five. It tells a reader what to reread; it is not a final verdict. The rule was not adjusted after seeing this result.

**Sentiment.** `openai/gpt-oss-120b`, with no training and one fixed prompt, scored on the same test rows the 2024 notebook used (split rebuilt with `random_state=42`, 70/15/15, stratified):

| Model | Weighted F1, 2024 test split (53 rows) |
|---|---|
| Random Forest (2024) | 0.296 |
| Gradient Boosting (2024) | 0.348 |
| Selected model (2024) | 0.366 |
| XGBoost (2024) | 0.378 |
| **openai/gpt-oss-120b, zero-shot, via Otari** | **0.491** |

On all 349 headlines the same model scores **0.413** (accuracy 0.456). That figure stands on its own: the 2024 models trained on 70% of those rows, so they cannot be fairly scored on them.

What this lets someone do: get a better sentiment label than the 2024 pipeline gave, without collecting training data or a GPU. Caveats that matter:

- 53 rows is a small test set; one headline moves weighted F1 by roughly 0.02. The all-349 score (0.413) is lower than the 53-row score, so part of the gap over 2024 is likely luck of the split.
- The labels (-1/0/+1; 170 neutral, 99 negative, 80 positive) are the course's. How they were made is not documented, and they may be the ceiling.
- 2019 news may be in the model's training text. These labels are not.
- The classifier's instruction was written once and not adjusted to raise the score. Rewording an instruction while watching F1 on these 53 rows would fit it to these answers and overstate the result. It was reworded one time, before any score was computed: the first wording said the news was "about Apple", and the model declined about 90 items that were about other companies.

**On news no model has memorised.** The same pipeline ran on 12 Apple headlines and 5 days of prices fetched through Otari on 2026-11-12: 8 claims written, 1 removed, price figures recomputed in the sandbox.

## How it works

```
stock_news.csv (349 headlines + daily prices, 2019)
   ├─► classifier model ─► label -1/0/+1 ─► code scores F1
   └─► 18 weeks
          ├─► writer model (routing policy) ─► claims, each citing headline ids or price figures
          ├─► checker model (other family)  ─► supported / not, with a quote
          ├─► Otari sandbox                 ─► recomputes open, close, high, low, change
          ├─► decision rule (decide.py)     ─► keep or remove, with the reason
          └─► Otari guardrail               ─► blocks buy/sell advice in the final text
```

**Models describe, code decides.** A claim is shown only if all of these hold ([`decide.py`](decide.py)): it cites something; every cited headline id exists in that week; every price figure matches the sandbox's recomputation; the checker said "supported" and, for a news claim, its quote really is in a cited headline; the guardrail did not flag it. A "supported" verdict is necessary, never sufficient. Every model reply is validated for required fields and allowed values ([`validate.py`](validate.py)); a rejected reply is retried once, and a second failure counts against the claim (or, for sentiment, as a wrong answer).

**Roles.** The writer (`openai/gpt-oss-120b`) summarises. The checker (`alibaba/qwen3-235b-a22b-instruct-2507`, a different model family) is asked to find what the evidence does not support and never sees the writer's reasoning. All three models used are open-weight.

**What went wrong in the first run.** The checker was first given the raw daily price rows. It removed 23 of 108 claims, and 17 of those were price claims whose figures were correct: the checker was doing the arithmetic itself and getting it wrong. The checker now gets the sandbox's figures as its evidence for price claims, so no model does arithmetic. The first run's output is kept in [`runs/first_run_results.json`](runs/first_run_results.json).

## The app: Check a text

[`functions/api/check.js`](functions/api/check.js) is a small endpoint behind the site's "Check a text" screen. It splits the pasted text into sentences and, for each one: sends it through Otari with the blocking guardrail, asks the checker model (Qwen3 235B, via Otari) whether the sources support it, validates the reply, and then code decides ([`functions/_rules.js`](functions/_rules.js)). A sentence stays only if the checker quoted a supporting passage that really is in the sources and every figure in the sentence appears in the sources. If Otari refuses for budget, nothing is shown as confirmed. The key it uses is a Cloudflare secret with its own small cap in Otari, so the cap is the most the public page can spend. The sources box also takes up to 3 links, which are read through Otari's web fetch, so an answer from a research chat can be checked against the pages it cites. It does not use the sandbox: figures are matched against the source text, not recomputed.

## Otari features used

| Feature | Where it is used | What it did in this run |
|---|---|---|
| Multiple models, distinct roles | classifier and writer vs checker | 852 calls to gpt-oss-120b, 148 to Qwen3 235B |
| Routing and fallbacks | briefs are requested from the policy `countersign-writer` (gpt-oss-120b, then Mistral Small 3.2) | drill policy `countersign-fallback-drill`: its main model's provider answers "does not exist", Otari tried 2 candidates and gpt-oss-120b wrote the brief (`Otari-Fallback: true`) |
| Code execution | `POST /code/execute` recomputes the price figures, no model involved | 2 runs: all 18 weeks of 2019, and the live week; every price claim was compared with the output |
| Web fetch | `POST /fetch` reads Yahoo Finance's Apple news feed and daily prices for the live week | 12 current headlines and 5 price rows through the same pipeline |
| Budgets and spending limits | the key is capped at $1.50; a refusal stops the run and lists the missing weeks | drill: Otari refused week 6 (`budget_exceeded`), 13 weeks marked missing, run marked incomplete |
| Guardrails | each brief's final text is sent with a blocking guardrail, profile `no-investment-advice` | 18 briefs passed; the drill sentence got 403 `guardrail_violation` and the model was never called |

The three drills are forced on purpose and labelled as drills on the page. The guardrail service is ours ([`functions/validate.js`](functions/validate.js), fixed patterns, no model): the hosted gateway has no built-in guardrail service and its catalog guardrails each need another vendor's key, but it accepts a guardrail service by URL and does the blocking itself.

Not used: MCP, per-user budgets.

Total spend on the key for everything above, including development reruns: **$0.16** of the $1.50 cap (1008 logged requests).

## Run it

```bash
pip install requests pandas scikit-learn pytest
export OTARI_API_KEY=...        # an otari.ai key; cap it in the dashboard
python -m pytest tests          # decision rule and reply validation, no network
python pipeline.py page         # rebuild site/index.html from the saved run, no cost
python pipeline.py all          # sentiment, briefs, drills, live week, page
jupyter nbconvert --to notebook --execute --inplace countersign.ipynb   # the notebook, no cost
```

Model replies are cached in `runs/cache/`, so a rerun is free; delete the folder for a fresh, paid run (about $0.05). A damaged cache file is ignored and asked again. The run needs two routing policies in the Otari dashboard (`countersign-writer` and `countersign-fallback-drill`, both Fallback policies with the models named in [`otari.py`](otari.py)) and web access switched on for the workspace. The writer's reply is streamed, because the hosted gateway cuts a non-streamed request at 30 seconds and a brief takes slightly longer.

If the budget cap is hit mid-run, Otari refuses every further request; the run stops, the remaining weeks are recorded as missing and the run is not marked complete.

## Article links

The 2024 dataset has no links, only summarised text. For the nine news items cited by the removed claims and the demo week, [`article_links.json`](article_links.json) records the likely original report, found by web search on 2026-11-12 and matched by date and subject. They are a reading aid; the check uses only the dataset's text.

## Data caveat

The price columns come from the course dataset as they are. Its `Close` values do not always sit between that day's `Low` and `High`, so the weekly figures describe the dataset, not necessarily Apple's real prices. The check is that the brief's numbers match the data it was given.

## Closest existing work

- [Daily Stock Analysis](https://github.com/ZhuLinsen/daily_stock_analysis): an LLM stock dashboard with sentiment scores; no second-model or calculation check found.
- [FinGPT](https://github.com/AI4Finance-Foundation/FinGPT): finance language models, not a checked brief.
- In this hackathon: Recount (recomputes numeric claims in Otari's sandbox), Lintel (one model writes, another checks, on NYC building records), Themis (a claim ledger for pull requests). None is about market news.

Stock-news sentiment is a common project. What is specific here is the checked brief, with the removed claims on show, and the before-and-after numbers on a 2024 project's own data.

Not investment advice.
