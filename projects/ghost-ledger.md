# Ghost Ledger: a deletion-audit agent (HackerRank Orchestrate)

**HackerRank Orchestrate, Oct 24–25, 2026.** A 24-hour solo build from the problem email (Oct 24, 18:00 IST), followed by a 30-minute AI voice interview. **Result: 75.9/100, #93 on the live board, not placed.** Score breakdown: interview 26.4/30, output 28.2/30, code 18.3/30, chat transcript 3.0/10.
**Code:** [DSProjects/hackathons/hackerrank-orchestrate-oct26](https://github.com/JannetEkka/DSProjects/tree/main/hackathons/hackerrank-orchestrate-oct26) · a deeper Q&A already exists in that folder: [`docs/INTERVIEW_PREP.md`](../hackathons/hackerrank-orchestrate-oct26/docs/INTERVIEW_PREP.md) (pitch, 2-minute walkthrough, seven topics, the questions another participant was asked, numbers to remember). Read it with this file.

## The 30-second version

The challenge, "Ghost Data Still Exists": a shop's dashboards say every GDPR deletion request is "Complete". The agent checks whether that's true. For each of 518 requests it decides whether deletion was actually asked for, finds every copy of the person's data across **94 evidence files** (SQL snapshots, JSON exports, six log dialects, PDFs, screenshots), reconstructs each record's state at the audit time, applies the deletion rules, and writes `COMPLETE` / `INCOMPLETE` / `NOT_APPLICABLE` with an ordered, evidence-cited remediation plan.

**On the 32 public samples:** status accuracy **100%**, step F1 **99.2%** (29/32 cases exact), relative step order 100%. 19/19 team-authored metamorphic and adversarial tests pass. The full 518-case run takes about 9 s, makes **0 model calls warm**, and cost about $0.02 in model calls to fill the cache.

The impact claim, stated honestly: the gold labels say the dashboards' "Complete" was often false. The agent finds those cases from evidence. There's no measured human baseline for how long a manual audit of 518 requests over 94 files would take.

## 1. Architectural reasoning

### Database / storage
- **SQL snapshots are executed in in-memory SQLite.** Primary, regional, reporting and failover replica tables are all kept, so **replication drift** shows up as a record gone from one table but present in another. That's the main reason to load them as SQL rather than parse them as text.
- Everything else becomes one normalised record type: `Observation(evidence_id, time, system, resource, fields, lookup keys)`. State at `audit_at` is "latest observation at or before `audit_at` wins". **Workflow statuses and activity results are claims, so they're never treated as state.**
- **Response cache** (`code/cache/`, keyed by content hash) for every LLM/VLM answer, so a re-run reproduces `output.csv` byte for byte with zero model calls.
- No vector DB: linking is by **exact identifier**, never by similarity. A near-miss like `g.silva76.jr@` vs `g.silva76@` must *not* link, and that was a planted decoy.

### Compute & hosting
- A batch CLI on one machine (`python3 code/main.py`). The whole run is ~9 s on CPU. No server, because the deliverable was a CSV plus code, and an auditor would run it as a scheduled job.
- A **production-monitoring design** is in the README (latency p95, cost per request vs a $0.00004 baseline, any model call on a warm run, validator failures), marked "not built yet". Say exactly that.

### Frameworks & libraries
- **LLMs only where language is genuinely ambiguous:** request intent (Gemini Flash → Groq `gpt-oss-120b`, JSON at temperature 0, 10 texts per batched call) and screenshot transcription (Gemini vision, RapidOCR offline). **Everything else** (evidence parsing, identity, linking, state, policy, ordering) is deterministic Python. Why: a deletion verdict must be reproducible and auditable, and an LLM in the decision path would make it neither.
- pdfplumber for PDFs, RapidOCR as the offline OCR, pytest. No agent framework.

## 2. Data & security pipelines

### Authentication & access control
- **Identity resolution is the access-control core** (`IdentityResolver`): the request email may be current or historical. All emails, phones and email hashes ever held by the stable `user_id` come from the identity tables and the audit log. **Names are never used to link**, because different customers share names.
- An email no identity table knows is linked on the literal address only, with no workflow attribution. If nothing matches, the only contract-valid row is `NOT_APPLICABLE` with `[]`, with the reason in the trace.
- **The console masks PII by default** on every load, and the unmask choice is never stored. Search only matches what's on screen.
- Secrets come from the environment or a git-ignored `.env`, are never logged, and the tests delete provider keys from the environment.

### Data ingestion & flows
- A one-shot batch: requests CSV + evidence folder → intent → identity → normaliser → linking → state at `audit_at` → policy (`deletion_rules.csv`: DELETE / REDACT / ANONYMIZE / RETAIN) → ordered steps → **contract validator** (exits 1 on any violation).
- **Linking without identifiers.** A scrubbed record (a 404 profile, an all-null analytics row) carries no identifier any more. The engine learned the deletion workflow's timing from evidence-owned activity: policy actions chained by exact gaps (390 s / 449 s, never seen between two different owners), and every event at a fixed phase after its account job modulo 30 s. Orphan records go only to the request whose job is in phase; **when two requests fit equally, nothing is attributed** (precision over recall), and both get a `needs_review` flag (14 records / 28 cases on the full run).

### Privacy & compliance
- **Retention is enforced, not optional:** security and legal records are always verified *present*, never planned for deletion, even when the request text asks for it (test 17).
- **Untrusted text is treated as data** (`SAFETY.md`, threats T1–T8). The LLM sees only the request text, JSON-encoded, `<`/`>` escaped, inside `<untrusted_request>` tags. Only a yes/no intent reaches the engine, so a text can't add steps, cite evidence or set a state. Evidence text never reaches a text LLM.
- Model calls go to Google and Groq with the request text only.

## 3. Reliability & failure operations

### State management
- Stateless and deterministic: the same inputs and cache give the same output. Per-subject **"eras"**: evidence older than the same subject's *previous* request belongs to that request.

### Error handling & fallbacks
The README's failure table, every row with a detector and a degraded mode:
- **Model rejected** (400/401/403/404/422) → put on a dead list for the run, next model tried. **Timeout or rate limit** → 3 retries with backoff (2 s, 4 s), then the next model. **Circuit breaker:** 3 consecutive items with no answer and the run finishes on local fallbacks, logging it once.
- **Bad JSON or a malformed batch** → per-item calls, then the rule model. **VLM fails** → RapidOCR for that file. **Unparseable evidence file** → skipped and counted (`parse errors: N`, 0 here).
- **LLM vs rule-model disagreement on intent**, resolved asymmetrically toward *not deleting*: a veto when the LLM says "deletion" but the text negates it; an override of an LLM refusal **only if the text has no negation-like token at all** (a broad list across 15+ languages). Any doubt keeps the refusal, flagged `needs_human_review`. 0 of 550 texts disagreed on this dataset.
- **The safety bug I'd tell an interviewer about:** an independent review of build `427ddc9` found that the then-symmetric override let the rule model authorize deletions the customer had refused ("Bitte löschen Sie mein Konto nicht", "削除しないでください", "Please never delete my account…") because its negation regex was narrow. The 518 graded rows weren't affected, but it was an irreversible-error path added to recover 2 sample cases from one fallback model. The fix (10-24, 20:39): override only when no negation-like token appears anywhere, plus negation-aware offline rules. The residual risk is documented in `SAFETY.md`.

### Logging & observability
- `output.trace.jsonl`: one line per case with the intent verdict, resolved identity, and every linked resource with *why* it was linked, its state, evidence and policy rule.
- `output.usage.json`: calls, tokens, cost and cache hits per run.
- **Ghost Ledger console** (`code/ui/ghost_ledger.html`, a single offline file): a claim-vs-reality matrix, findings by system, a searchable ledger, and a per-case dossier with an evidence timeline and resource map (solid = identifier match, dashed = workflow or catalog attribution).

## 4. Evaluation & optimisation metrics

### Performance benchmarking
- Samples: status 100%, step precision 100%, recall 98.4%, F1 99.2%, exact 90.6%, citation accuracy 98.7%.
- **Ablations show what each component buys** (step F1 / exact cases): full 99.2% / 90.6%; without workflow attribution 91.2% / 53.1%; without the timing model 97.4% / 71.9%; without per-subject eras 97.4% / 84.4%.
- **Held-out checks:** a leave-one-out timing model and a perturbed-dataset run (±2 s jitter gives output identical to the timing-off ablation, so the model degrades safely).
- **Error analysis:** two sample gold steps (case_18, case_20) cite records that appear in no participant-visible file, so they can't be derived. The organisers confirmed that scoring uses `deletion_requests.csv` only.
- **Sensitivity I'd volunteer:** flipping the account-job tie-break from earliest to latest changes **29 of 518** rows while the samples score identically. Those rows are the least certain part of the output.
- Tests: 108 unit tests offline plus 19/19 metamorphic, wrapped in `code/check.sh` as one quality gate.

### Cost & resource efficiency
- The cache-filling run's ledger: 30 calls, 42,662 tokens, **$0.0193**, **$0.000037 per request**. A cold-run experiment: 50 calls, $0.042. Warm re-run: **0 calls**. The whole build stayed well under $0.10 (an estimate for unlogged vision calls is marked as such in `usage_report.md`).
- Batching 10 texts per call and deduplicating texts by hash cut the calls.

### System constraints
- Free-tier quotas and retired model aliases interrupted the first runs. The model probe on 10-24: `gemini-flash-latest` 503, `gemini-3.8-flash` timeout, `gemini-3.5-flash` 503, `gemini-2.5-flash` 404 retired, `gemini-3-flash-preview` OK.
- The rule model only knows the negation forms it lists, which is the residual risk.
- It's tuned to one synthetic company's evidence formats, and a new log dialect needs a parser.

## What the history shows (real decisions)
- 10-24 15:00 accuracy pass (learned workflow timing) → 15:12 first independent review → 15:24 reviewer fixes (BOM-safe CSV, unknown email, empty request) → 17:27–17:56 a safety and engineering pass (refactor into modules, 62-test pytest suite, strict LLM schema, rule-model veto, injection tests, held-out evaluation) → 20:21 symmetric disagreement policy → 20:35 **final independent review found the override bug** → 20:39 fixed.
- **The lesson that cost the most points:** the chat transcript scored **3/10**. `log.txt` had been curated (entries removed, reordered and paraphrased; one SESSION START for six sessions), against the challenge's append-only, every-turn rule (commits at 22:48–23:12 show the curation). Next time keep the log raw. It's a good answer to "tell me about a mistake".
- The code score (18.3/30) was the weakest graded artefact. I don't have the graders' reasons, so I'd say that rather than guess.

## Weak spots to own before they ask
- The transcript curation, above.
- A rule override that could authorize a refused deletion existed in one build, and was caught by review, not by tests.
- 29 rows depend on a tie-break the samples can't discriminate.

## Sources
`README.md`, `code/audit/SAFETY.md`, `code/evaluation/evaluation_report.md`, `code/evaluation/usage_report.md`, `review/REVIEW_FINAL.md`, `docs/INTERVIEW_PREP.md` (headings), DSProjects git log for the folder (Oct 24); [DSProjects#42](https://github.com/JannetEkka/DSProjects/issues/42) (result and lesson); tracker row in `hackathons/october-2026.md`.
