# SQL Noir: a detective game that teaches SQL on live data

**Open Agent Hackathon 2026 (genai.works), Track 02: The Agent That Can Explain Why.** Built Oct 22–27, 2026 (paused Oct 22–26 for Claude usage limits), submitted Oct 27 as team SmarTies. Results Nov 6. Re-entered in the **Zetaris Demo Challenge** with a new recording (closes Nov 3).
**Code:** [github.com/JannetEkka/sql-noir](https://github.com/JannetEkka/sql-noir) · video 3:43 [youtu.be/oX4KvIMfIbE](https://youtu.be/oX4KvIMfIbE) · deck PDF (submitted with the form)

## The 30-second version

A game master gives you a case ("which store sold at a loss?"). You write SQL to crack it. The game runs your query on real data in **Zetaris** and compares your rows with the reference answer's rows **by value**. When you're wrong it shows the evidence: the rows you shouldn't have, the rows you're missing, the column that doesn't line up. Your partner **Nemo**, a 1940s detective running on **NVIDIA Nemotron** through **Meterless Nightshift**, turns that evidence into a hint for a price in points, and a critic makes sure the hint never gives the answer away. Once solved, you explain *why* your query proves it. **Meterless H-MEM** remembers what you got stuck on and aims the next case at it.

**No verdict comes from the model's opinion.** Every verdict is a comparison of two result sets on live data, with the rows that prove it. That's the Track 02 "explain why" core.

Played on the real stack on Jannet's laptop (10-26): the validator, grader, Nemo's hints, the critic, explanation judging and H-MEM memory all worked. 50 tests.

## 1. Architectural reasoning

### Database / storage
- **Zetaris (Lightning SQL over REST) holds the data every case is built on:** `TPCDS_DB` (39 tables, the TPC-DS retail benchmark) and `NY_TAXI`. Why a relational engine: the whole game *is* SQL. The answer is a result set, and correctness is set comparison. Zetaris was also mandatory for the hackathon.
- **H-MEM is the player's memory**, not a database I designed: mistakes and solved cases are written as H-MEM records with a source and confidence, recalled before each case, and a note that helped gets `feedback("helpful")`, which raises its confidence (the trust ledger). Why a memory engine instead of a table of mistakes: retrieval by relatedness ("you struggled with HAVING") and confidence that changes with use.
- **Local JSON files** in `.data/`: `trace.jsonl` (every agent step), `score.json`, `answers.json` (checked case answers, so a case opens instantly after its first check), `tables.json` (columns). Delete `.data` for a fresh detective. It's single-player and local by design.

### Compute & hosting
- **Runs on the player's own machine, next to Zetaris and Nightshift.** The hackathon required local Zetaris (Docker) and Nightshift as the AI provider. On Jannet's laptop (Windows, 16 GB, integrated GPU) that meant Zetaris under WSL with Docker's data on D:, WSL capped at 7 GB, and Nightshift routing to **NVIDIA's cloud lanes** (Nemotron 3.5 Lightning 30B and Nemotron 3 Super 120B) because there's no dedicated GPU. During the first Nightshift test the laptop hit 96% CPU, 94% memory and "thermal hot".
- **Node 22 with a built-in http server**, no framework, no runtime dependencies. The only installs are dev tools (tsx, TypeScript, Node types). Why: judges ran the project themselves, so fewer moving parts meant fewer setup failures.

### Frameworks & libraries
- **TypeScript, no framework.** Vendored, unmodified: the **H-MEM engine and its conformance suite** (Apache-2.0), 13/13 passing.
- The **Meterless Runtime provider** was written to the "Power prompt" contract: bearer token, `meterless-app` and `meterless-scope` headers, status from `GET /v1/models`, tool calls, 429 retries.
- **Cursor** was required. It's where the game met the real stack: on the laptop each change was pulled, tested (`npm test`, `npm run smoke`, `npm run validate:cases`), started and played.

## 2. Data & security pipelines

### Authentication & access control
- **Read-only SQL guard** (`src/zetaris/`): SELECT, WITH, SHOW, DESCRIBE and EXPLAIN pass; anything that writes is refused, **including a write hidden inside a WITH**. The player types arbitrary SQL against a real database, so this is the security boundary.
- Zetaris REST calls carry the bearer key, `X-Org-ID` and a fresh UUID `X-Request-ID`, one statement per call.
- Secrets live in `.env` (`ZETARIS_API_KEY`, `METERLESS_RUNTIME_TOKEN`). `npm run smoke` records the services' replies to `fixtures/recorded` but **never secrets**.
- It's one player per machine with no accounts, so per-user access control isn't in scope.

### Data ingestion & flows
- **Request/response per action:** open case → the validator runs the reference query on Zetaris (cached after the first check) → player query → guard → Zetaris → grader → coach → critic → hint.
- **Agent loops, not a chain:** designer ↔ validator until a generated case is fair (up to 3 tries); coach ↔ critic until a hint is safe (one rewrite, then the case's own hint); memory decides which case comes next.
- **The validator's six checks before any case is posed:** read-only; returns rows; small enough to be a clue; same answer twice; has an ORDER BY when order matters; **no tie at a LIMIT cut-off**.

### Privacy & compliance
- All data is Zetaris's sample data (TPC-DS and NYC taxi zones), so there's no personal data. Model calls go through Nightshift to NVIDIA's cloud with the case, the evidence and the player's query.

## 3. Reliability & failure operations

### State management
- Player memory and score persist across sessions in H-MEM and `.data/`. A test covers memory surviving across sessions, recalling a past mistake for a related case, and raising a note's confidence after it helped.

### Error handling & fallbacks
- **If Nightshift is down, the game keeps going on the cases' own hints.** That path was rehearsed in Chromium.
- **Critic failure → fixed hint:** if the rewrite still leaks, the case's own hint is used.
- **Zetaris errors are the user's errors:** "Show Zetaris's own message when a query can't run" (10-26). A query past Zetaris's **2-minute limit** now says it was too slow, instead of asking whether Zetaris is running.
- **Case designer failure:** "Design a case" failed on camera ("the model could not be reached": Nemotron's reply had no usable case). It was cut from the video, then fixed: the designer leaves room for the reply and retries instead of giving up. **Not re-run on the laptop yet.** Say so.

### Logging & observability
- **Every agent step goes to `.data/trace.jsonl`** and to a live trace panel at the bottom of the page, showing which model answered each call. For a Track 02 "explain why" agent, the trace is part of the product.

## 4. Evaluation & optimisation metrics

### Performance benchmarking
- **The validator caught real problems on real data** that the stand-ins couldn't: 'Whose turf' had two boroughs tied at 207 zones, so `LIMIT 1` had no single answer (now it asks for every borough's count), and 'Selling at a loss' ran a three-table join over all store sales past Zetaris's 2-minute limit (replaced by the same HAVING lesson on the small store table).
- **Jannet's test run found a case bug:** the two return-reason cases asked for "the reason's id" but the answers used `r_reason_sk`, not `r_reason_id` (fixed in `c701347`).
- **A browser rehearsal found two UI bugs:** hidden panels showing (a `hidden` attribute losing to a display rule), and columns shown as "no match" when the player only had extra rows (column matching now uses containment).
- Tests: 18 → 36 → 42 → 48 → **50** over the build; H-MEM conformance 13/13.
- **No learning-outcome measurement.** I can't claim players learn SQL faster than with a tutorial. That would need a study.

### Cost & resource efficiency
- Free: the NVIDIA key on build.nvidia.com behind Nightshift, local Zetaris, no hosting. Checked answers and table schemas are cached in `.data`, so Zetaris runs each reference query once.

### System constraints
- Hardware: Zetaris wants 8 GB and 4 CPUs for Docker; the laptop has 13.8 GB usable, so Zetaris is stopped when not in use. The first image pull (~4 GB) took **~3.5 hours** on home internet, so `docker compose down -v` is never run.
- Answers are compared by value: rounding beyond 6 decimals, or an equivalent date written differently, counts as different.
- The critic catches answer values and quoted reference SQL, not a hint that *paraphrases* the answer.
- One player at a time.

## What the history shows (real decisions)
- **Idea and track:** first recommended a supplier-renewal check (Track 01). The SQL detective game came from Jannet's coding-teacher idea, where Zetaris does real work, and moved from Track 03 to **Track 02** after the onboarding call, because Track 03 paid less and the evidence panel *is* "explain why".
- **Go/no-go was the laptop:** Nightshift's Windows edition says it needs a dedicated GPU. It worked by routing to NVIDIA's cloud lanes.
- **Organisers' answers (10-22):** Claude Code alongside Cursor is OK; one Meterless engine is enough; **judges run the project themselves**, so a from-scratch README became a must.
- **10-22:** paused at 84% of the weekly Claude limit until Oct 26 17:30 IST, behind Amazon, Orchestrate and GitLab. Then 36 hours of work; submitted Oct 27, ahead of the deadline, since ties go to the earlier submission.
- A competing Track 02 entry was seen on the ideas board (Causa: explains why revenue moved, on the same stack).

## Weak spots to own before they ask
- The case designer fix wasn't re-verified on the real stack.
- Claude Code wrote most of the code in cloud sessions against stand-ins. Jannet ran and checked it on the real Zetaris and Nightshift in Cursor, and found the real bugs above.

## Sources
`README.md`, git log Oct 22–27 (21 commits; bodies of `a9a3177`, `fcf74e9`), `src/zetaris/client.ts`; [DSProjects#23](https://github.com/JannetEkka/DSProjects/issues/23) comments 10-14 to 10-27; [DSProjects#67](https://github.com/JannetEkka/DSProjects/issues/67) (Zetaris Demo Challenge); `.claude/CLAUDE.md` (laptop facts).
