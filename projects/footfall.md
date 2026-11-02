# Footfall: a taste agent for small local shops

**One build, two hackathons:** the **Qloo Agentic Hackathon** and the **Nebius × NVIDIA Global AI Hackathon** (Best Apps & Agents). Built Oct 26–29, 2026, submitted to both Oct 29. Qloo winners ~Nov 6; Nebius judging Dec 1–15.
**Live:** [footfall-zz9v.onrender.com](https://footfall-zz9v.onrender.com) · **Code:** [github.com/JannetEkka/footfall](https://github.com/JannetEkka/footfall) (MIT) · videos: [Qloo 1:54](https://youtu.be/Smw3hQl3CB0) · [Nebius 1:51](https://youtu.be/duLrpsNtTRo) · private store `JannetEkka/footfall-private` (spend ledger + replay packs)

## The 30-second version

Chains run audience research before they pick a playlist or a product line. The independent café on the corner guesses. Footfall takes a shop's address and what it sells, asks **Qloo** what the people who go to the places within a walk of the door like (music, books, brands, dishes), compares that with the wider area and with the shop itself, and an **NVIDIA Nemotron** agent on **Nebius Token Factory** turns it into a playlist, things to stock or add to the menu, and one weekend event. **Every suggestion cites the Qloo results it rests on, and a checker deletes anything Qloo didn't actually return.**

**Measured:** a run takes 20–30 s, makes ~18 Qloo calls (8 chosen by the agent) and costs about **$0.013** (9 LLM calls, ~80k input tokens). The two recorded demo runs: 18 and 19 Qloo calls, 0 suggestions cut by the checker, $0.0109 for the Nebius run. **Total LLM spend across all testing and runs: $0.45** (private ledger, 10-27), against a $15 hard cap.

What I can't claim: no café owner has used it yet. "Ask a few real café owners which suggestions they'd actually try" is listed as next.

## 1. Architectural reasoning

### Database / storage
- **No application database.** Each run is computed live. Two things need durability, and both live in a **private GitHub repo written through the Contents API** (`footfall/store.py`): the spend ledger (`budget/spend.json`) and the demo shops' saved Qloo answers (`replay/*.json`).
- **Why a git repo as a store:** Render's free disk is wiped on every restart, and a database service would be another account and another bill. A private repo with a fine-grained token (Contents read/write on that one repo only) is free, durable, versioned (every reserve and settle is a commit), and auditable.
- **Why private:** Qloo's terms allow private caching but keep their data out of public repos. The public repo's test fixtures are **made up**, shaped like docs.qloo.com's examples.
- **The evidence ledger** (`footfall/evidence.py`) is an in-memory record of every Qloo call and everything it returned, for the run. The checker validates against it.

### Compute & hosting
- **FastAPI on Render's free plan** (Blueprint `render.yaml`), sleeping after 15 idle minutes, so the first visit takes about a minute. Free hours are shared with Lore and Proof of Fix (750 h/month per account).
- **LLM on Nebius Token Factory** (OpenAI-compatible API), which the Nebius hackathon required. A provider switch (`LLM_PROVIDER=nebius|openai`) keeps it portable.

### Frameworks & libraries
- **No agent framework:** locate → survey → investigate (Nemotron tool calls, up to 8) → write → check, in `footfall/agent.py`. Five Qloo tools are exposed as function definitions.
- **Two models, chosen by measurement:**
  - *Tool calls:* the cheapest Nemotrons with tool support were Nano 30B-A3B and 3.5 Lightning (both $0.06/M in, $0.24/M out). Both made correct parallel tool calls. **Lightning took 1.6 s and 118 tokens; Nano took 7.4 s and 483**, so Lightning.
  - *Writing:* on identical replayed Qloo data, Lightning kept 2 of 5 Brooklyn suggestions (it listed tags as books to stock) and misread the Shoreditch gap. **Super 120B kept 4/4, 5/5 and 6/6.** Ultra 550B wrote the most detail but put IDs into the text, at 2–3× Super's cost.
- Vanilla JS + Leaflet, no build step; Nominatim for geocoding.

## 2. Data & security pipelines

### Authentication & access control
- **No user accounts. Abuse control is rate limiting:** 4 runs an hour and 12 a day per visitor, 2 concurrent, 20 a day in total.
- **Keys:** `QLOO_HACK_API_KEY`, `NEBIUS_HACK_API_KEY` and `FOOTFALL_STORE_TOKEN` (fine-grained, one repo, Contents read/write, 90-day expiry past judging) live only in Render's environment. Jannet created them and never pasted them in chat.
- **Qloo's quirk is a correctness risk I treated like a security one:** Qloo silently ignores invalid parameters, so a typo returns plausible but unfiltered results. `footfall/params.py` holds the Entity Type Parameter Guide as a table, and the client **refuses any request with a parameter not documented for its `filter.type`**. Undocumented parameters are allowed only in probe mode until `scripts/probe_location.py` shows they change results.

### Data ingestion & flows
- **Request/response per run, streamed as a live agent log.** The method relies on a gap in Qloo: `/v2/insights` filters by location only for places. So:
  1. `/search` finds the shop and re-centres on Qloo's pin (the geocoder had one shop 1.3 km off).
  2. Places within a walk, with hotels, city halls, churches and clinics excluded (popular but tasteless signal).
  3. **Those place IDs become `signal.interests.entities` for artists, books and brands.** That's the cross-domain bridge: what do people who go to *these* places listen to, read and buy?
  4. `signal.location` gives the wider-area baseline. It isn't in the parameter guide, so it was probed first: London and Bengaluru shared none of their top 10 artists, and it works at neighbourhood scale. **Adding a radius made results *less* local** (10/10 shared at 1.2 km), so it's never sent.
  5. Tag taste per domain, giving the taste gap.
  6. Nemotron's own calls.
  7. Write, then the checker.
- Geocoding: Nominatim within its usage policy (one request a second, cached, one retry), then a fallback to Qloo `/search` with an address check on a 429.

### Privacy & compliance
- No personal data: a shop's public address and category.
- Qloo data never enters the public repo (terms). Cached bodies keep only the fields the parsers read (~10× smaller).
- Map data © OpenStreetMap; the landing photo is Unsplash-licensed.

## 3. Reliability & failure operations

### State management
- **Reserve, then settle:** each run reserves a $0.05 ceiling in the ledger *before* its first LLM call, then swaps it for the actual cost. **If the server dies mid-run, the whole reservation stays counted**, so a crash can only over-count spend, never under-count it.
- **Fail closed:** on Render, a ledger that isn't durable means **no LLM calls at all**. Checked "like Render" with no token: the page loads and runs are refused.

### Error handling & fallbacks
- **Spend cap as a safety system:** the Token Factory account has a card on file and no spending limit, and the demo is public for weeks. So every call is checked *before* it's sent (worst case = prompt bytes ÷ 2 as tokens + `max_tokens` must fit what's left of the run's reservation) and priced from reported usage with a 25% margin. Prices come from Token Factory's own `/v1/models?verbose=true`, and a model with no known price is refused. At ~$0.015 a run and 20 runs a day, $15 can't run out before Dec 15.
- **Replay mode, for when the Qloo key dies** (hackathon keys are switched off afterwards, but Nebius judges test until mid-December): the three demo shops keep their Qloo answers in the private store. After a 401/403, demo shops replay and custom addresses pause with an explanation on the page. **Nemotron still runs live**, as Nebius requires. Temperature 0 did *not* make Nemotron repeat its tool calls (a second Brooklyn run made 8 new ones), so in replay it's shown the saved calls and told only those can be answered. Six offline runs: every answer from the pack, no misses.
- **Qloo warnings:** `warnings: not_found` was being ignored, so 1–3 of 8 place IDs were silently dropped. They're now read, logged and replaced with the next places.
- **Model quirk:** with thinking on, Nemotron spent its whole token allowance reasoning and wrote no JSON, so `enable_thinking: false` is set for the write step only.

### Logging & observability
- `/api/health` shows both models, whether the ledger is durable, and spend so far. Every reserve, settle and replay-pack update is a commit in `footfall-private` ("settle a run: $0.01114"), so the ledger is its own audit log.
- The page shows the live agent log, why the agent made each call, and what the checker cut and why.

## 4. Evaluation & optimisation metrics

### Performance benchmarking
- **The checker is the quality metric:** suggestions kept vs cut on identical replayed data was how the writer model was chosen (Super 4/4, 5/5, 6/6 vs Lightning 2/5 on Brooklyn).
- **Real-data fixes** came from the first live runs on three shops (Brooklyn bookshop, Shoreditch café, Koramangala café): wrong-shop lookup, geocoder 429s, ignored signal IDs, credit cards and hotel ratings in unfiltered tags, Bengaluru places with no music tags.
- **Prompt fix measured honestly:** after asking for owner-facing text without IDs, two replay runs had no IDs left but still one field name and one shared-tag pick. The commit says "better, not solved".
- Tests: 13 → 25 → 45 → 53 → 55, all on synthetic fixtures.
- **No owner study** (see above).

### Cost & resource efficiency
- Per run ~$0.013. Prompt tokens per run cut from **165k to ~80k** by slimming the brief (no coordinates, addresses or duplicated tags). Heatmaps trimmed from ~850 cells to the 50 used. Lightning for the 8 cheap tool rounds, Super only for the one write.
- Total spend $0.45 of the free $25–26 Token Factory credit (Builder Program).

### System constraints
- Hard limits by design: $15 total, 20 runs a day, $0.05 a run.
- The Qloo hackathon key only works on `hackathon.api.qloo.com` and stops after the event.
- Free Render: cold starts; a disk wiped on restart (hence the git store).

## What the history shows (real decisions)
- **10-26:** the idea was checked against Qloo's docs *before* any key existed, and the place bridge was chosen because it didn't depend on an undocumented parameter. Built 13 tests on synthetic fixtures while waiting for keys.
- **10-27:** the key arrived. Probe verdicts → survey fixes → spend cap built *before* the first public LLM call → replay mode → writer model upgraded → live on Render at 22:30 IST. Jannet created the private repo and the token from step-by-step instructions.
- **10-27 23:12:** both videos made from real runs, narrated by Kokoro (AI voice, disclosed on the end card), checked with a Whisper transcript against the script.
- **10-29:** submitted to both.

## Weak spots to own before they ask
- One project entered in two hackathons. Both rule sets allowed it, and the Qloo rules were read to confirm.
- A card is on file at Nebius Token Factory with no platform spend limit. The app's own cap is the control, and it's logged in `hackathons/cards.md`.
- Built with Claude Code as the coding assistant. I set the brief (a taste agent for small local businesses), created the keys and infrastructure, and approved the model choices on the numbers.

## Sources
`README.md`, `footfall-private/README.md` and `budget/spend.json` (committed $0.45, updated 2026-10-27T23:03Z), git log Oct 27–29 (PRs #1–#5, commit bodies); [DSProjects#55](https://github.com/JannetEkka/DSProjects/issues/55) comments 10-26 to 10-29; tracker rows for Qloo and Nebius in `hackathons/october-2026.md`.
