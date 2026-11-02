# Klarbrief: official Swiss letters explained offline

**Hack Apertus 2026, Track 2B (Own Project).** Built Oct 12–13, submitted Oct 14, 2026. Result: not placed (announced Oct 23).
**Code:** [github.com/JannetEkka/klarbrief](https://github.com/JannetEkka/klarbrief) (public, Apache-2.0) · report `track_2b/Klarbrief_Report.pdf` (5 pages) · demo `track_2b/docs/klarbrief-demo.mp4` (1:41)

## The 30-second version

Someone in Switzerland gets an official letter in German, French or Italian and can't read it well enough to catch the deadline. 27% of residents don't hold a Swiss passport (Avenir Suisse, FSO data, end of 2024). Klarbrief has Apertus 1.5 8B, Switzerland's open LLM, explain the letter in the reader's language. Every point must quote the letter, and plain code (not a model) finds that quote and checks the date or CHF amount before the point is shown. Points that fail go in a separate "Not shown as fact" list with the reason.

On 48 explanations, the model offered 7 wrong deadline dates and the verifier stopped 6. No wrong CHF amount reached the reader. All 48 replies were in the reader's language, and 28 of 29 true deadlines were shown. It all ran offline on a 4-core CPU with no GPU. The comparison is the same model without the verifier, which is what a plain "explain this letter" app would show.

## 1. Architectural reasoning

### Database / storage
- **No database at all.** Each letter is one stateless request: letter text in, explanation out. Nothing is stored, which is the point for a privacy use case: a letter has nowhere to persist.
- Evaluation data is flat files: `data/letters/letters.json` (28 fictional letters with labelled deadlines and amounts) and `data/results/*.jsonl` (every raw model reply, one per line, with token counts, timestamp and output mode). JSONL because each reply is appended as it finishes and the run can resume (`make eval` is resumable), and because `make score` can re-score every recorded reply exactly without a model.
- If they ask "why not a vector DB?": there is no retrieval. The whole letter (~790 prompt tokens) fits in the context window, so retrieval would only add a way to miss the relevant sentence.

### Compute & hosting
- The track **required** one of three deployments: on-premise, air-gapped, or sovereign Swiss cloud. Serverless on a US hyperscaler was ruled out by the brief itself.
- `make onprem` brings up two containers (`docker-compose.yml`): the official llama.cpp server with a 5 GB Q4_K_M GGUF of Apertus 1.5 8B, and the app. The model server is on a Docker network declared `internal: true`, so it has no route to the internet. The model file is mounted read-only. The only download is the model at build time, pinned to a Hugging Face revision and checked against its exact byte size (`MODEL_SIZE := 5059027136` in the Makefile).
- Why a dedicated box instead of serverless: an 8B model on CPU takes about 5 minutes per letter. That doesn't fit a serverless timeout, and it doesn't need to. A commune can run it on hardware it already has.
- Sovereign Swiss cloud is supported by the interface (three env vars: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_NAME`) but **untested**. Infomaniak and Swisscom serve Apertus on paid endpoints we never called. Say so if asked.

### Frameworks & libraries
- **Python standard library only at runtime.** The app image installs nothing: the HTTP server is `http.server`, the client is `urllib`, and the tests use `unittest`. Why: an air-gapped install can't `pip install`, and every dependency is something a public body's IT team would have to review. It also cuts supply-chain risk to zero for the app layer.
- **llama.cpp** over vLLM: it runs on CPU and enforces a JSON schema as a grammar during generation (`response_format=json_schema`).
- **OpenAI-compatible API** as the only contract, so the same code runs against local llama.cpp, the hackathon's CSCS endpoint or a Swiss cloud.
- **No agent framework.** It's one model call per letter, then deterministic checks, so an orchestration library would add nothing.

## 2. Data & security pipelines

### Authentication & access control
- There are no user accounts. It's a single-page tool for one reader at a time, and nothing is stored, so there is no per-user data to protect.
- The only secret is the optional `LLM_API_KEY` for a remote endpoint. It is read from the environment or `.env` and is never committed (`.env.example` holds placeholders). In on-prem mode there is no key at all.
- If asked how I'd deploy it at a commune: put it behind the commune's existing SSO or reverse proxy. The app has no auth layer of its own, and I'd say that plainly.

### Data ingestion & flows
- The flow is synchronous request/response: paste the letter → one chat call (`temperature 0`, `seed 0`, max 1,200 tokens, exact JSON schema) → language check (one retry if the reply is in the wrong language) → verifier → UI cards. There are no webhooks, queues or batches in the product.
- The evaluation is a batch job (`make eval`): 48 replies with 4 parallel llama.cpp slots, about 60 minutes in total.

### Privacy & compliance
- In on-prem mode **the letter never leaves the machine**: the model server has no internet route, and nothing is logged to a third party.
- All 28 test letters are fictional: invented names, communes ("Beispielwil", "Montexemple", "Esempiano") and case numbers. No personal data was used. Licence: CC-BY-4.0 / CDLA-Permissive-2.0.
- Model licence: Apertus is open weights and open data, Apache-2.0. Its openness is part of why a public body can run it at all.
- It is not legal advice, and the UI points the reader to the contact named in the letter.

## 3. Reliability & failure operations

### State management
- There is no session state to lose. If the server dies mid-request, the reader re-submits the letter. The evaluation run is resumable: it appends one JSONL line per reply and skips letters already done.

### Error handling & fallbacks
- **Output-mode ladder** (`llm.py`): it asks for `json_schema` first. If the endpoint rejects it with HTTP 400/422, it steps down to `json_object`, then to `text`. It prints which step it took and **records the mode in every reply**, so a weaker mode never goes unnoticed.
- **Retries:** HTTP 429/5xx gets exponential backoff (3 s × 2^n, capped at 60 s, 5 attempts). Network errors are retried with a shorter backoff. After that it raises an error rather than returning something empty.
- **Language retry:** if the reply isn't in the reader's language, it makes one retry ("rewrite in Ukrainian, keep quotes, dates and amounts"). If it's still wrong, the UI says so instead of hiding it.
- **Replay mode:** with no endpoint configured, the UI replays recorded replies for the sample letters, **labelled as replayed**, so judges can run it with no model and it never pretends to be live.
- **The verifier is the main fallback.** A point that fails is never dropped silently. It moves to the "Not shown as fact" list with the reason.

### Logging & observability
- Every model reply is recorded with prompt and completion tokens, seconds, output mode and timestamp, which is how I could measure cost per letter.
- The rejected-points list doubles as a review queue. That was the pilot idea: counter staff at a commune review what the verifier refused.

## 4. Evaluation & optimisation metrics

### Performance benchmarking
- **Baseline:** the same model's points without the verifier, which is what a plain "explain this letter" app shows. There are two ablations, both re-scored with the final verifier:

| Pipeline | Replies | In reader's language | True deadlines shown | Wrong dates raw → shown | Wrong CHF raw → shown |
|---|---|---|---|---|---|
| A: plain JSON mode | 20 | 20/20 | 7/12 | 4 → 0 | 2 → 0 |
| B: + exact output schema | 40 | 27/40 | 24/24 | 4 → 2 | 0 → 0 |
| Final: + reader language restated | 40 | 40/40 | 24/24 | 6 → 1 | 2 → 0 |
| Final, 8 held-out letters | 8 | 8/8 | 4/5 | 1 → 0 | 0 → 0 |

- **Each engineering step fixed a measured problem.** A → B: all 5 deadlines missing in run A came from replies with no `deadlines` field, and the exact schema found all 24. B → Final: only 7 of 20 Ukrainian replies were actually in Ukrainian. Restating the reader's language after the letter fixed all 20 on the first try.
- **Held-out set:** 8 letters written *after* the verifier was frozen, on new topics. No wrong date or amount was shown.
- **What got through:** "ab dem 6. Januar 2027", a start date presented as a deadline. The date really is in the letter, so a provenance check can't catch it. That needs an interpretation check, which is the next step.
- **Recall cost of strictness:** 30 of 323 points (9%) were hidden because the model paraphrased the quote too far. For deadlines and amounts, 28 of 29 deadlines and 44 of 50 amounts still reached the reader.

### Cost & resource efficiency
- About 790 prompt and 440 output tokens per letter. On a 4-vCPU machine with 4 parallel slots: 48 letters an hour at **no marginal cost**, since no API is billed. GPU latency was not measured.

### System constraints
- On a 4-core CPU, one letter takes about 5 minutes (300 s/letter measured), so it isn't interactive on CPU.
- It takes pasted text only. Scans, photos and QR-bills are next steps, not built.
- It uses a quantised community text-only build (Q4_K_M), not the official BF16 checkpoint or the 70B. Batched decoding in llama.cpp isn't bit-identical across batch sizes, so a re-run can change individual replies; re-scoring the recorded replies is exact.
- The test set is small and synthetic: 28 letters we wrote ourselves. No native speaker rated the Ukrainian.

## What the history shows (real decisions)

- **The repo started as a different entry.** It was created from the HackApertus template on Sep 22. On Oct 6, PR #1 set it up for **Track 1A red-teaming** as `wiretrap-apertus` (Wiretrap's decoy-tool method against Apertus, with the official chat template vendored). Issue #25 records the reasoning: 1A's rubric rewarded an end-to-end harness, and no video was needed around the away days.
- **The pivot (Oct 12–13):** "a safety filter stopped Claude twice on the red-teaming side", so the entry switched to Track 2B with Jannet's OK on 10-12. Klarbrief was built and evaluated on Oct 13 (backup commits from 15:19 to 17:52), merged as PR #2 on Oct 14, and the repo was renamed `klarbrief` and made public.
- **Free inference was a constraint from day one.** The CSCS API keys had run out by Oct 6 and Phoeniqs compute had closed. The Public AI gateway had $2 of free credit. That pushed the entry towards running locally on CPU, which became the product's main selling point.
- Submitted Oct 14 because Jannet was away Oct 15–18. Not placed.

## Weak spots to own before they ask
- The verifier checks **where** a fact came from, not **what it means**. A real date used as the wrong kind of date gets through.
- The dev numbers are optimistic: rule (d), the partial-match rules and the language reminder were added after inspecting dev replies. The 8 held-out letters exist for that reason.
- The summary text and translations aren't verified. One English summary renamed "Beispielwil" to "Examplewil".
- It was built with Claude Code as the coding assistant, which the hackathon FAQ allowed. I designed the check and the evaluation and directed the build.

## Sources
`README.md`, `track_2b/technical_report.md`, `track_2b/docker-compose.yml`, `track_2b/Makefile`, `track_2b/src/klarbrief/llm.py`, `server.py`; git history Sep 22–Oct 14 (PR #1 `claude/bold-newton-1ifhff` Track 1A layout, PR #2 Klarbrief); [DSProjects#25](https://github.com/JannetEkka/DSProjects/issues/25) comments of 10-06, 10-13 and 10-14.
