# Token Usage and Cost Report

Final full-dataset run over `dataset/deletion_requests.csv`: **518 requests**.

## Where models are used

| Stage | Model | When it is called |
|---|---|---|
| Request intent (does the text authorize deletion?) | Gemini Flash, falling back to Groq `gpt-oss-120b`; JSON output, temperature 0 | distinct texts only, 10 per batched call |
| Screenshot transcription (VLM) | Gemini Flash vision, temperature 0 | once per screenshot file (11 PNGs), keyed by SHA-256 |
| Everything else (evidence parsing, identity, linking, state, policy, ordering) | none | deterministic Python, $0 |

Responses are cached in `code/cache/` (keyed by content hash), so a re-run reproduces `output.csv` with zero model calls. A rule-based intent model and local OCR (RapidOCR) always run as a fallback and as a cross-check; if the API is unreachable the agent finishes offline.

## Model calls recorded by the token ledger

The response cache was filled across several helper runs because free-tier quotas and retired model aliases interrupted the first attempts (the agent's model chain falls back Gemini -> Groq and keeps every answer as it arrives). The table below is the ledger of the run that completed the cache.

| Provider | Model | Calls by purpose | Calls | Input tokens | Output tokens | Total tokens | Avg tokens / request | Est. cost | Est. cost / request |
|---|---|---|---|---|---|---|---|---|---|
| gemini | `gemini-3.5-flash` | intent_classification_batch: 2 | 2 | 1,623 | 1,127 | 2,750 | 5.3 | $0.0033 | $0.000006 |
| groq | `openai/gpt-oss-120b` | intent_classification_batch: 28 | 28 | 23,178 | 16,734 | 39,912 | 77.1 | $0.0160 | $0.000031 |
| **Overall** | | | **30** | **24,801** | **17,861** | **42,662** | **82.4** | **$0.0193** | **$0.000037** |

Cache hits during this run: {"media": 11, "intent": 550}.

## Inventory of the response cache (what produced `output.csv`)

| Kind | Model | Cached answers | Used by the final run |
|---|---|---|---|
| intent answer | `gemini (earlier run, model not tagged)` | 3 | yes (looked up by text hash) |
| intent answer | `gemini:gemini-3-flash-preview` | 14 | yes (looked up by text hash) |
| intent answer | `gemini:gemini-3.5-flash` | 102 | yes (looked up by text hash) |
| intent answer | `gemini:gemini-3.8-flash` | 1 | yes (looked up by text hash) |
| intent answer | `gemini:gemini-flash-latest` | 12 | yes (looked up by text hash) |
| intent answer | `groq:openai/gpt-oss-120b` | 278 | yes (looked up by text hash) |
| screenshot transcription | `gemini:gemini-3.5-flash` | 2 | 2 of 11 files |
| screenshot transcription | `gemini:gemini-3.8-flash` | 6 | 4 of 11 files |
| screenshot transcription | `gemini:gemini-flash-latest` | 7 | 5 of 11 files |
| screenshot transcription | `rapidocr` | 11 | 0 of 11 files |

Model calls not in the ledger above: **15 vision transcriptions** and the intent answers tagged with an earlier model, made in runs whose token ledger was not saved. A Gemini Flash screenshot call costs roughly 1.3k input + 0.6k output tokens, so these add about 28k tokens (about $0.028) - an estimate, marked as such. The whole build stays well under $0.10.

## Warm re-run (response cache present)

518 requests, **0 model calls**, cache hits {"media": 11, "intent": 550}; output identical to the cold run.

## Cold-run experiment (2026-10-24, not shipped)

Goal: one coherent cold run (empty caches, one pinned model per stage) whose ledger could replace the one above. It was not shipped; the ledger above stays the record of the shipped run.

**Model probe** (one tiny call each): `gemini-flash-latest` 503 unavailable; `gemini-3.8-flash` timed out; `gemini-3.5-flash` 503 unavailable; `gemini-2.5-flash` 404 retired; `gemini-3-flash-preview` OK (text and vision) - pinned for both stages. Declared fallback: groq:openai/gpt-oss-120b (Mistral/NVIDIA keys unset).

**Run A** (all 518 requests, then the samples): 50 calls, 76k tokens, $0.042. The pinned model served the first calls and then hit its rate limit; the fallback served the rest.

| Provider | Model | Calls by purpose | Calls | Input tokens | Output tokens | Total tokens | Avg tokens / request | Est. cost | Est. cost / request |
|---|---|---|---|---|---|---|---|---|---|
| gemini | `gemini-3-flash-preview` | media_transcription: 10, intent_classification_batch: 4 | 14 | 15,846 | 7,021 | 22,867 | 44.1 | $0.0223 | $0.000043 |
| groq | `openai/gpt-oss-120b` | intent_classification_batch: 36 | 36 | 33,471 | 19,728 | 53,199 | 102.7 | $0.0198 | $0.000038 |
| **Overall** | | | **50** | **49,317** | **26,749** | **76,066** | **146.8** | **$0.0421** | **$0.000081** |

Result: 0 of 518 output rows changed, but the samples dropped to 27/32 exact / 97.1% step F1 / 93.8% status (suite 18/19): case_12, case_21 - the fallback model returned authorizes_deletion=false (ACCOUNT_SUPPORT) for two 'please verify my deletion' follow-ups, which the prompt counts as deletion; the shipped cache has the same model answering true on the same texts. **Fix:** the intent module now lets the rule model override an LLM refusal when the text has a clear deletion cue, no negation and no other purpose (the mirror of the existing veto), recorded as `override: rules_over_llm`; unit tests replay both refusals.

**Run B** (Gemini only, paced (LLM_MIN_INTERVAL_S=13, LLM_RATE_LIMIT_BACKOFF_S=20)): daily quota of gemini-3-flash-preview exhausted: 0 successful calls; the run finished on the rule model and RapidOCR. That fully offline path reproduced 517/518 rows; case_45: audit_record_001 is only recovered by the VLM transcription, not by OCR.

## Pricing assumptions (USD per 1M tokens, list price)

| Model | Input | Output |
|---|---|---|
| `gemini-2.5-flash` | $0.30 | $2.50 |
| `gemini-2.5-flash-lite` | $0.10 | $0.40 |
| `gemini-2.5-pro` | $1.25 | $10.00 |
| `gemini-flash-lite-latest` | $0.10 | $0.40 |
| `gemini-flash-latest` | $0.30 | $2.50 |
| `gemini-3.8-flash` | $0.30 | $2.50 |
| `gemini-3.5-flash` | $0.30 | $2.50 |
| `gemini-3-flash-preview` | $0.30 | $2.50 |
| `openai/gpt-oss-120b` | $0.15 | $0.75 |
| `llama-3.3-70b-versatile` | $0.59 | $0.79 |

Token counts come from the API's `usage_metadata` on every response (prompt and candidate tokens), accumulated in `code/audit/usage.py`. Estimated: dollar figures (list prices above) and the unledgered vision calls (marked).
