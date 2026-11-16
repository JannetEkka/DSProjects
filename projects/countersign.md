# Countersign: every claim in a model-written brief, checked

**Mozilla Otari Hackathon: Devs Wilding Online (DoraHacks), Nov 2026.** Brief 11-12, built and submitted 11-12 before the 10:29 IST close. Prize result: not recorded when written (11-16).
**Live app:** [countersign-6my.pages.dev](https://countersign-6my.pages.dev) · **Code:** branch [`otari-hackathon`](https://github.com/JannetEkka/DSProjects/tree/otari-hackathon/Stock_Market_Sentiment_Analysis_NLP/countersign) of this repo · **Video (4 min):** [youtube.com/watch?v=_qOCC5WpPpk](https://www.youtube.com/watch?v=_qOCC5WpPpk) · brief `hackathons/countersign/design.md`

## The 30-second version

The hackathon asked people to finish a side project using the hosted Otari gateway. This finishes [Stock Market Sentiment Analysis](stock-sentiment-nlp.md) (PGP, 2024), which left two things open: its LLM summaries had no grounding check, and its sentiment F1 was 0.366. Countersign writes a weekly brief about Apple from 349 headlines (Jan–Apr 2019) and shows a claim only if a checker model from another family, a sandbox recomputation of the prices and a no-investment-advice guardrail all confirm it. Removed claims stay visible with the reason. A "Check a text" screen does the same for any pasted summary and its sources.

## 1. Architectural reasoning

- **Python pipeline, no server**; the results page and the "Check a text" endpoint are Cloudflare Pages and a Pages Function.
- **Every model call through Otari**, which the hackathon required. Writer and classifier: `openai/gpt-oss-120b`; checker: `alibaba/qwen3-235b-a22b-instruct-2507` (different family, never sees the writer's reasoning). All open-weight.
- **Otari features each do a job:** routing with fallbacks (policy `countersign-writer`), code execution (recomputes open, close, high, low, change), web fetch (a live week of Apple news and prices), a $1.50 key budget, and a blocking guardrail.

## 2. Data & security pipelines

- Headlines → writer (claims citing headline ids or price figures) → checker (supported or not, with a quote) → sandbox recompute → decision rule in code (`decide.py`) → guardrail on the final text.
- A claim is kept only if it cites something, every cited id exists that week, every price matches the sandbox, the checker said "supported" and its quote really is in a cited headline, and the guardrail passed. "Supported" is necessary, never sufficient.
- The key is capped at $1.50; the account had a $2 welcome credit and no card.

## 3. Reliability & failure operations

- Every model reply is validated for required fields and allowed values.
- Drills, run on purpose: a fallback policy whose main model "does not exist" (Otari tried 2 candidates and gpt-oss wrote the brief); a budget refusal at week 6 (13 weeks marked missing, run marked incomplete); a guardrail block (403, model never called).
- Requests are kept short (one headline or one claim per call) because open Otari issues report 504s after about 30 s.

## 4. Evaluation & metrics

- **The check:** 108 claims across 18 weeks; 8 removed (5 unsupported per the checker, 3 whose quoted support wasn't in the cited headline). The 2024 version would have shown all 8 as fact.
- **How good the check is**, on a public labelled set (HaluEval summarization, 60 articles): caught 41 of 60 planted errors (68%); wrongly struck at least one sentence in 27 of 60 faithful summaries (42 of 223 sentences, 19%). The rule wasn't adjusted after seeing this.
- **Sentiment:** zero-shot gpt-oss-120b, weighted F1 **0.491** on the same 53 test rows the 2024 notebook used (2024 models 0.296–0.378, selected 0.366); 0.413 on all 349 rows.
- First-run lesson: given raw price rows, the checker removed 23 claims, 17 of them correct price claims, because it did the arithmetic itself and got it wrong. Now it gets the sandbox's figures; no model does arithmetic.

## Weak spots to own before they ask

- 53 test rows: one headline moves F1 by about 0.02, and the all-349 score is lower, so part of the gain over 2024 is likely the split. The course's labels are undocumented; 2019 news may be in the model's training text.
- The check is strict and imperfect: it says what to reread, not a final verdict.

## Sources

The Countersign README on branch `otari-hackathon` (numbers from `runs/results.json`, 2026-11-11, and `runs/benchmark.json`); `hackathons/countersign/design.md`; `hackathons/november-2026.md` row 5.
