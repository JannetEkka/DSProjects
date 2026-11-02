# Spona: concurrent agents that match researchers with companies

**NTP Novi Sad Hackathon 2026 (JigJoy × Mozaik), Track 02 EINSTEIN.** Kickoff Oct 30, built Oct 30–31, 2026, submitted Oct 31 online as team SmarTies. Winners Nov 7.
**Live:** [jannetekka.github.io/spona](https://jannetekka.github.io/spona/) (the recorded run as an app: Replay, Matchmaker, Proposals, Critic, Gaps) · **Code:** [github.com/JannetEkka/spona](https://github.com/JannetEkka/spona) · showcase run [`runs/2026-10-31-full/`](https://github.com/JannetEkka/spona/tree/main/runs/2026-10-31-full)

## The 30-second version

The track brief: the University of Novi Sad "has thousands of researchers, NTP Novi Sad hundreds of companies, yet they rarely work together." Spona is a team of 12 agents on **Mozaik** (JigJoy's TypeScript runtime for concurrent agents) that reads the whole synthetic EINSTEIN dataset (1,047 researchers, 10,779 papers, 153 companies with 489 challenges, ~7M tokens, in English, Serbian Latin and Cyrillic) and gives **every company challenge an outcome with its reason**: a written proposal, a close match, no close match at the university, or not a research problem. For the best pairs it drafts an industrial PhD topic or a one-page joint project, and every fact about a person or company cites the record it came from. A critic agent checks claims *while the other agents are still working*.

**The recorded run:** all 489 challenges in **5 min 48 s**, 84 agent loops with **up to 19 at once**, 84 model requests, 4 proposals for 4 companies. The critic sent back 13 evidence claims (11 rewritten, 2 dropped) and 20 draft statements that went beyond their sources. It found **64 research challenges with no close match** in the university's own published work, listed by sector. Cost: about **$1.52** of JigJoy's Claude credit plus the Gemini free tier.

**What's not measured,** and the README says so: whether these pairs would meet. Neither the brief nor the dataset says how matching is done today, so there's no "faster" or "better" claim. The way to measure it (record per pair whether they met and started a project, against EINSTEIN's earlier count) is written down.

## 1. Architectural reasoning

### Database / storage
- **Shared state is one board in Mozaik's `RuntimeState`**: challenge cards, pairs and their fit, evidence cards and claims, proposals and critic interventions. There's no external DB. It's a single-run batch over a fixed dataset, and the board is written out (`board.json`) at the end.
- **Search index instead of a vector DB:** the library indexes every paper and profile with **BM25** at start (~7 s, no model). Latin and Cyrillic are folded to one form, so `Јелена Марковић` matches `Jelena Marković`. Why BM25 over embeddings: the matching question is "how much of this challenge's vocabulary appears in this person's own work", which is lexical and explainable (`ranking.md` shows the matched words). It's free, needs no embedding calls against a 20-requests-a-day quota, and handles the script mix with a simple fold.
- **Run artefacts as files:** `trace.jsonl` (raw bus events), `loops.json`, `ledger.json` (every model call with model, tokens and time), `board.json`. `npm run report` rebuilds every Markdown report with no model call.
- An answer cache keyed by prompt (`.cache/llm/`) and a quota memo (`.cache/quota.json`).

### Compute & hosting
- **A local Node 20 process** runs the whole team; the live page is static on GitHub Pages replaying the recorded run. No server, because the deliverable is a run's output plus a way to inspect it, and judges read the repo.
- Every agent loop can stream live to **Mozaik cloud** (`MOZAIK_API_KEY`).

### Frameworks & libraries
- **Mozaik was required, and the judges weighed genuine concurrency.** Participants don't call each other: each registers situation handlers for events it cares about and publishes new events. The runtime delivers every event to every participant without waiting. Each model question is its own `runLoop` with a fresh context, so two loops of one agent never share memory. An `InterceptionHandler` routes each answer back to the agent that asked.
- **Model split by job:** many small jobs (3 analysts, 3 profilers) on `gemini-3.5-flash-lite`, which took 100+ requests a day without a 429. The few judgement calls (critic, writer) on **Claude Sonnet 4.6 through JigJoy's gateway credit**, with Gemini flash as the fallback.
- **A custom `InferenceRunner`** (`src/llm/runner.ts`) paces each model, retries on rate limits, moves to the next free model when one is out of quota, overloaded or silent for 2 minutes, and logs every call.

## 2. Data & security pipelines

### Authentication & access control
- **Key isolation was a real incident:** the JigJoy credit page says to set `ANTHROPIC_BASE_URL` and `ANTHROPIC_API_KEY`. Those are the names Claude Code itself reads, so in the cloud environment they pointed the coding session at JigJoy's gateway and sign-in broke. The fix: Spona reads `JIGJOY_ANTHROPIC_*` and passes them to Mozaik explicitly, never the plain names. The same for Gemini: it reads `GEMINI_API_KEY_NTP` and **deletes `GEMINI_API_KEY` from its own process at start**, so nothing can fall back to another project's key.
- The JigJoy credit needed no card (recorded in DSProjects; the impact rule PR #74 noted it).

### Data ingestion & flows
- **Event-driven, concurrent:** `run.requested` → the coordinator assigns shards → 3 analysts read a third of the companies each, two batches at a time → as each batch lands, the critic checks the cards → the matchmaker searches and re-ranks immediately → profilers start evidence cards for the best pairs **while analysts are still reading** → the critic reviews evidence as it arrives and sends unsupported claims back → the writer drafts all selected pairs at once → the critic reviews each draft as it lands.
- **The evidence budget opens as analysis progresses**, so early results can't use it all. A profiler may only take a pair inside the unlocked budget across the whole board.
- **Batching for quota:** 10 companies per analyst call, 4 pairs per profiler call, up to 8 evidence cards per critic call, and revisions collected for a few seconds and sent together.

### Privacy & compliance ("pairs, not people")
- **Fit is a property of a pair**: vocabulary overlap with the person's *own* work, stated openness (`open_to`), availability, and how much evidence survived the critic. **Title, seniority, publication counts, citations, venues, age, gender, nationality and record language are not inputs**, and a test checks that fit doesn't move with title or publication count. Only the 3 best-matching papers count, so a long list doesn't win alone.
- **Messy records are handled, not guessed:** someone who left (R0068) is never proposed; retired and emeritus researchers are consulting-only; two duplicate people are merged; two namesake pairs are kept apart; **90 unlinked papers that only share a common name are never attributed**; notes that open with someone else's name aren't used.
- Only work-related data goes to the models, and only for pairs that need it. The dataset is synthetic.

## 3. Reliability & failure operations

### State management
- The answer cache means a rerun after a crash only pays for what didn't finish. The recorded run used `--fresh`.
- Reports are reproducible from saved artefacts with no model calls.

### Error handling & fallbacks
- **Critic rules first, model second.** Rules cost nothing and "can't be talked round": the quote is verbatim from the company's own text (any script); every cited ID exists and belongs to this person (listed on their profile or carrying their researcher ID, **never a name match alone**); years match. Then a batched model check grades each claim supported, overstated or unsupported. One revision, then dropped. A pair needs two surviving claims to be proposed.
- **A hard cap:** `--max-calls` (default 120). When it's hit, agents get an error answer, and claims that can't be checked don't pass. Fail closed.
- **The stall (10-31 night):** every flash model in the analysts' chain answered 503, the last one was out of daily quota, and saving that to `.cache/quota.json` threw inside the retry handler because `--fresh` on a new checkout had never created `.cache/`. The call's promise never resolved and the run hung. Fix: create the folder, and only log a failed save.
- **Critic false positives fixed:** a name rule read a capitalised sentence-start word as part of a name ("If BrzaPošta"); the model listed statements it *agreed* with as problems, so points now carry a verdict and supported ones are dropped; a point whose quote isn't in the draft is discarded.

### Logging & observability
- `trace.md`: a Gantt chart of every loop, a table of every critic intervention with its outcome, one pair followed end to end, and the full event timeline. The live page's Replay shows the overlap.
- **A cost bug I'd tell an interviewer about:** the first take's trace said Claude read only 979 input tokens (~$0.71). The gateway caches long prompts on its own, and Anthropic reports cache writes and reads *outside* `input_tokens`, so the run was underpriced. The runner now reads them from raw usage and prices them (1.25× write, 0.1× read).

## 4. Evaluation & optimisation metrics

### Performance benchmarking
- Counts from the run: 489/489 challenges with an outcome; 125 (26%) not research problems, each with a reason; 276 with a named close match that wasn't profiled (the evidence budget went to closer pairs); 64 of 364 research and engineering challenges with no researcher whose own work covers ≥40% of the challenge's terms.
- Critic: 96 claims on 24 evidence cards checked before writing, 13 sent back; 20 draft statements sent back; 6 points left open printed under their proposals for the people to settle.
- Tests run the rule checks against the **real dataset** (namesakes, duplicates, departures, quote matching, fit invariance to title and publication count).
- **No ground truth for match quality.** It's a synthetic dataset with no labelled "good pairs", so quality is argued from evidence checks, not accuracy.

### Cost & resource efficiency
- 84 requests: 47 on flash-lite (free) and 37 on Claude, ~556,000 input tokens in all, **under a tenth of the ~7M-token dataset**. Search and rules did the rest. About $1.52 of the $20 credit for the recorded run; about $5.50 across all takes.
- The design followed from a measured constraint (`docs/free-tier.md`): flash models allow **20 requests per day each** (quota id `GenerateRequestsPerDayPerProjectPerModel-FreeTier`), failed attempts seem to count, and several models were 503, 404 or silent on 10-30.

### System constraints
- The free-tier quotas set the evidence budget (24 cards), which is why 276 good matches weren't profiled.
- The model check is a model: it can miss an overstatement or flag a fair paraphrase. "Treat a proposal as a well-sourced first draft for a meeting, not as a verified fact sheet."
- Synthetic data only, and there's no feedback loop yet.

## What the history shows (real decisions)
- **10-30:** the whole system in one push after kickoff (data layer, BM25, people rules, critic, runner), then critic tightening the same day.
- **10-31, 03:10 IST:** the Claude gateway credit wired in under `JIGJOY_` names after the session-breaking env-var collision.
- **Three takes for the recorded run:** take 1 underpriced (cache tokens), take 2 stalled (503s + the quota-memo bug), take 3 recorded. Then re-recorded with charts and the critic fix (297 s → 348 s, 76 → 84 requests, 30 → 49 interventions).
- **A process slip I'd own:** PR #1 was merged before the final run and charts were pushed, and the session kept pushing to the merged branch. That follow-up work went into a fresh PR #2, and PR #1's description was corrected.
- **Why the page became an app (PR #3):** 15 points were for "potential for real use in EINSTEIN", and a long page to read didn't show it. The Matchmaker screen lets you pick any of the 489 problems.
- The impact rule (state measured impact only, never an invented baseline) was written into DSProjects during this build (PR #74).

## Weak spots to own before they ask
- No evidence yet that the matches are good in the real world. It's synthetic data with no outcome labels.
- Built with Claude Code as the coding assistant on Jannet's own JigJoy account. I set the impact framing, chose to submit online, and reviewed and merged the PRs.

## Sources
`README.md`, `docs/free-tier.md`, git log Oct 30–31 (PRs #1–#3, commit bodies); [DSProjects#54](https://github.com/JannetEkka/DSProjects/issues/54) comments 10-31 (03:10, 03:36, 04:34, 04:52, 05:58, submitted); tracker row in `hackathons/october-2026.md`.
