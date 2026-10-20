# Open Agent Hackathon 2026 (GenAI Works): prep

Build window: **Oct 22, 05:30 IST → Oct 28, 05:15 IST** (Oct 22 00:00 UTC → Oct 27 23:45 UTC). Submit on HackOS. Progress: [#23](https://github.com/JannetEkka/DSProjects/issues/23). Event page: [hackathon.genai.works](https://hackathon.genai.works/event/open-agent-hackathon-2026) · submit: [HackOS dashboard](https://hackathon.genai.works/dashboard) · help desk: [HackOS messages](https://hackathon.genai.works/messages) · rules questions: hackathons@genai.works.

This is the brief for the build session. It comes from the course material Jannet pasted on 10-20 (Start Here, How the Week Runs, Welcome Guide, Journey Map, Overview, the APPROACH guide, Event Calendar, FAQ, and the Participant Setup Guide dated 20 October), plus a read of [zetaris/getting-started](https://github.com/zetaris/getting-started) and [Meterless/Meterless](https://github.com/Meterless/Meterless) the same day. The workshop videos (Data Day, Build Day, Power Day) were not watched.

**No project code before the window opens.** "Work committed before the build window opens is not eligible, except for clearly declared pre-existing components." Installing Zetaris, Nightshift and Cursor and running the smoke test is setup, not project code, and should happen before Oct 22. The repo's first commit lands inside the window.

## Dates (IST)

| When (IST) | UTC | What |
|---|---|---|
| Oct 21, 17:30–19:00 | Oct 21, 12:00–13:30 | Onboarding call (YouTube live, recording on HackOS). "Additional challenges and prizes" are announced here |
| Oct 22, 05:30 | Oct 22, 00:00 | Build window opens |
| Oct 23, 05:15 | Oct 22, 23:45 | Registration closes (Jannet registered 10-20) |
| Oct 24 | — | Suggested mid-build check: "if the deadline were tomorrow, what would fail?" |
| **Oct 28, 05:15** | **Oct 27, 23:45** | **Submissions close. Hard deadline; no edits after** |
| Nov 6, 21:30 | Nov 6, 16:00 | Results call on HackOS |

Ties are broken on the Impact score, then on **submission time**, so submit early. Aim for the evening of Oct 27 IST.

The same week: RSNA Knee final (Oct 22/23), Amazon Fire TV (Oct 24, 00:30), IEEE ClimateChain (Oct 25), Build With AI (Oct 27, 02:30), GitLab (Oct 27).

## Rules that shape the entry

- **Required:** Zetaris integrated, Meterless integrated, Cursor used for development. NVIDIA "wherever it contributes"; in practice the product runs on Nemotron through Meterless.
- **Meterless means two things** (setup guide of 20 October):
  - **Build:** at least one **Meterless Engine** (H-MEM, Markovian, World Model, Scout Intent) working in a real feature. "Simply mentioning an engine in your submission, copying a prompt, or adding an unused dependency does not satisfy the Build rule." Show the feature and a passing conformance suite or test.
  - **Power:** the app supports **Meterless Nightshift** as its primary AI provider (OpenAI-compatible, local runtime). NVIDIA's API key goes in Nightshift's Providers tab, never in the app.
- **One primary track** per submission, changeable until the deadline in the team workspace. Cross-track relevance "is not scored twice".
- **Solo is fine**; same pool as teams. Team locks when the first submission is created.
- **Any language, framework or model.** Open-source libraries are fine. AI-generated code is "allowed and expected"; we own it and must be able to explain it.
- **Data:** open, legal, small. No real personal or confidential data. Small synthetic samples are fine. Keep the repo light, add a `SAMPLE_MODE=true` fallback, bound every API call with a timeout.
- **Secrets:** `.env` in `.gitignore`, a `.env.example` with placeholders only, no keys in README, notebooks, screenshots or logs.
- **IP:** we keep all rights; the organiser and sponsors get a licence to show the demo.

## Tracks and prizes

| # | Track | What it asks | Prizes (1st / 2nd / 3rd) |
|---|---|---|---|
| 01 | Solving Fragmented Intelligence | "Discover and work across fragmented data sources" | $2,000 / $1,350 / $1,000 |
| 02 | The Agent That Can Explain Why | Investigate across sources, connect findings, evidence-backed answers | $2,000 / $1,350 / $1,000 |
| 03 | Reasoning Architecture | Data, knowledge, memory and reasoning → reliable decisions and actions | $2,000 / $1,300 / $1,000 |
| 04 | Wildcard (Tinkerer) | Extend an existing project with Zetaris and Meterless; only the new work is scored | $1,000 / $600 / $400 |

- **The prize numbers disagree between documents.** The Overview, FAQ and Welcome Guide give the table above. The "How the Week Runs" lesson gives $1,600 / $1,200 / $900 (Track 03: $1,500 / $1,200 / $900). Ask on the call.
- **NVIDIA Nemotron Award: a DGX Spark.** For using at least one Nemotron model through Nightshift in a working feature. Judged on technical depth, usefulness and polish. `meterless/auto` can route to a non-NVIDIA model, so pin a Nemotron lane and show it in Nightshift's run details.
- Pool: up to $20,000 ($15,000 cash, $5,000 in kind). Cash by bank transfer within 30 days.

## Judging (out of 100, at least three judges each)

| Criterion | Points | What it means for us |
|---|---|---|
| Impact | 30 | A named user with a real problem and a decision that gets better. Also the first tie-breaker |
| Technical | 20 | Works end to end, reliably; sound architecture |
| Innovation | 15 | An agent pattern that isn't the familiar workflow |
| Demo | 15 | 1–4 minutes, main workflow end to end. Budget real time for the video |
| Product & UX | 10 | The output is usable by its user. A polished UI over a weak system scores badly |
| Sponsor tech | 10 | Zetaris, Meterless, Cursor and NVIDIA visibly doing work, in the demo, the deck and the README |

**What judges reward** (repeated in every document): agents that delegate, critique and revise, not a fixed pipeline; Planner ↔ Executor ↔ Evaluator loops; shared memory or state; branching, retries, escalation and recovery; logs or traces that show how the answer was reached; outputs someone could use. **What they discount:** single-agent systems dressed as multi-agent, linear chains (A → B → C), hardcoded demo paths, broad ideas built thinly, sponsor tech bolted on at the end.

## What we hand in

1. **Demo video, 1–4 minutes:** the main workflow end to end, how the agent solves the track, key features, and how Zetaris and Meterless fit in, including what was unusual about our use of them.
2. **Slide deck:** problem and users; solution; architecture diagram; stack; how Zetaris and Meterless were used and what was unusual about it; screenshots; future work.
3. **GitHub repo:** all code, README with setup, usage and dependencies that someone outside the team can follow. Also sample inputs and outputs, and logs or traces from real runs.
4. **Sponsor-tech explanation:** how Zetaris was integrated, how Meterless was integrated (engine + provider), how Cursor was used, where NVIDIA contributes.
5. **In the form:** the primary track, and any pre-existing components declared.

## The stack, as it actually works (checked 10-20)

### Data: Zetaris, local in Docker

- Get `zetaris-platform.zip` and the registry sign-in from Zetaris Cloud's [Run locally page](https://cloud.enterprise.zetaris.com/dashboard/download). Needs **8 GB of memory and 4 CPUs given to Docker, 15 GB free disk** (a 16 GB laptop). First pull and start take 30–45 minutes.
- Set `ZETARIS_ADMIN_EMAIL`, `ZETARIS_ADMIN_PASSWORD` and `ZETARIS_ADMIN_ORG` in the bundle's own `.env` **before the first start**; changing them later doesn't reset the account. Keep `ZETARIS_SEED_TPCH=true` for the supplied sample data.
- Web UI and SQL Editor on `localhost:3000`. REST on `http://localhost:8888/api/v1.0`. JDBC on port 10000. Never call 8889.
- **REST call:** `POST /sql-editor/sqls/run` with `Authorization: Bearer <ZETARIS_API_KEY>`, `X-Org-ID: 1` (local), and a fresh UUID `X-Request-ID`. Body: `{"queryId": <uuid>, "sql": "...", "source": "SqlEditor", "limit": N}`. Rows come back in `data`. 401 = bad key; 400 = bad org ID or non-UUID request ID. The API reference is served at `localhost:8888/redoc/index.html`.
- **SQL is Lightning SQL**, not Spark or Hive SQL: one statement per call, no trailing semicolon, qualified names.
- **A REST table is one fixed URL.** `CREATE LIGHTNING REST TABLE ... REQUEST(endpoint "...")`, then a `CREATE SCHEMASTORE VIEW` with `LATERAL VIEW explode(...)` to flatten it. It **re-fetches the source on every query** unless you `CACHE TABLE` it (one test went from 49.7 s to 1.2 s). Per-entity lookups need one table per entity; the EDGAR recipe makes one table per company.
- **Files:** only from S3 or S3-compatible storage. "Zetaris can't read a file sitting on your laptop." How to get our own small dataset into a local install is a question for the call.
- **Verified recipes** in the getting-started repo: PokéAPI, SEC EDGAR company facts and submissions, `company_dns` SIC / NACE / Japan codes, Eurostat, ABS, StatCan, Open Food Facts, NASA NeoWs, NOAA GHCN (S3), AWS public blockchain (S3), and a **USL model joining EDGAR to SIC with a foreign-key data-quality rule** (it found IBM's SIC code `3570` missing from the reference list). Known to fail: PUDL, Foursquare, Overture, Ookla, GBIF, Singapore PM2.5, NASA DONKI.
- The repo's `AGENTS.md` is written for coding agents (Cursor, Claude Code, Codex): preflight first, read-only first, dry-run before any create, never print keys.

### Build: Cursor and the Meterless Engines

- Cursor with its own models (Composer for speed, Grok for longer work) on the Cursor credit. Keep every Meterless and NVIDIA key out of Cursor's settings. How to claim the credit is still "[Organisers: add ...]" in the guide.
- **Engines are implementation specs, not npm packages:** each folder in `engines/` has an `AGENTS.md` contract, a runnable **TypeScript** reference (H-MEM, World Model, Markovian), examples and a conformance suite, run as `HMEM_IMPL=/abs/path/index.ts npx tsx conformance/runner.ts`. Scout Intent is spec plus an eval harness.
- `templates/agentathon-starter` is a TypeScript CLI that vendors the H-MEM reference. It shows how to map each feature to a named engine service, which is what the engine-usage judging looks for.
- **So the build is TypeScript (Node).** Python would mean re-implementing an engine to pass a TypeScript conformance runner.
- The prompts at [meterless.ai/engines.html](https://meterless.ai/engines.html) (Ideate, Implement, Combine, Harden, Power) are written for Cursor or Claude Code.

### Power: Nightshift, with Nemotron behind it

- Nightshift is a desktop app: **Windows (for PCs with a dedicated GPU), Mac (free M1+ edition for M1–M4; the M5+ edition looks paid), or DGX Spark.** No Linux edition, so it can't run in a cloud session.
- NVIDIA key from [build.nvidia.com](https://build.nvidia.com/models) (free endpoints, rate-limited) → Nightshift **Setup → Providers → NVIDIA**. Then lanes: Lane 1 fast `nvidia/nemotron-3.5-lightning-30b-a3b`, Lane 2 deep `nvidia/nemotron-3-super-120b-a12b`, optional judge lane. Use the exact names Nightshift shows.
- The app gets the **Runtime URL and token from Nightshift's Console** (top right), e.g. `METERLESS_BASE_URL=http://127.0.0.1:8088/v1`, `METERLESS_RUNTIME_TOKEN=...`, `METERLESS_MODEL=meterless/auto`.
- **Provider contract** (the "Add Meterless as a provider" prompt, Runtime 1.4): `Authorization: Bearer <token>` on every call; `meterless-app: <app id>` on every call; `meterless-scope: user` on chat; `GET /v1/models` decides online / unauthorized / offline (`/healthz` only proves the process is up); `POST /v1/chat/completions`; 180 s timeout; model ids are routing modes (`meterless/auto|fast|deep|cheap|local|fusion`, `meterless/<class>.<disposition>`).
- Not yet known: whether OpenAI-style tool calling (`tools` / `tool_calls`) passes through Nightshift to Nemotron. Plan for a JSON-output fallback.

## Ideas

Three new ideas plus the Wildcard fallback, roughly scored with the guide's 0–2 self-check (10 questions, 20 max; 16+ is "strong", 11–15 "feasible, reduce scope"). Jannet picks and names it.

| | Idea | Track | Self-score |
|---|---|---|---|
| **A** | Supplier renewal check (recommended) | 01 | 17 |
| B | Why did demand move? | 02 | 15 |
| C | Retraction Radar | 01 or 02 | 12 |
| D | Lore + Zetaris (Wildcard) | 04 | not recommended |

### A. Supplier renewal check (recommended)

**One line:** before a supplier contract renews, an agent pulls together what every system knows about that supplier, finds where the systems disagree, and recommends renew, renegotiate or escalate, with every fact traced to the query that produced it.

**User and problem.** A procurement or vendor manager at a mid-size company, a few weeks before a renewal. The facts are in the ERP (spend, invoices), the ticket system (late deliveries, quality issues), the contract store (terms, renewal date) and outside sources (the supplier's SEC filings, its industry). The systems name the supplier differently ("Dell", "DELL INC", "Dell Technologies"), keep different IDs, and sometimes contradict each other. So people either spend a day reconciling or renew on autopilot.

**Data, all landing in Zetaris:**

- **Internal (synthetic, small):** ERP vendor master, purchase orders and invoices; service tickets; contracts. About 15–25 suppliers, each a real US-listed company so EDGAR has it, with realistic mess: abbreviations, old names after a rename, a subsidiary billed under the parent's name, a tax ID typo. How it gets into Zetaris is a day-1 check: served as small internal REST endpoints (the way SaaS ERPs expose data) and registered as Zetaris REST tables, or whatever local route the Zetaris mentors confirm.
- **External, on verified recipes:** SEC EDGAR submissions (profile, SIC code, former names) and company facts (revenue, net income, liabilities); `company_dns` SIC reference; SEC's `company_tickers.json` for name → CIK matching.
- **Zetaris USL** over internal vendor ↔ EDGAR company ↔ SIC code, with foreign-key data-quality rules, so the agent can ask Zetaris which records are invalid instead of guessing. This is the Zetaris team's own EDGAR/SIC showcase, taken one step further: the agent finds and explains such mismatches itself.

**Agents (a loop, not a chain):**

- **Planner:** splits the question into sub-questions and picks sources from what Zetaris lists.
- **Resolver:** matches the supplier across systems (names, tax IDs, former names, tickers) and writes candidate matches with confidence to shared state. Below a threshold, it asks the user instead of guessing.
- **Analyst:** writes read-only Lightning SQL, one statement at a time, runs it through Zetaris, and records each finding with its query and rows.
- **Critic:** rejects claims without a query behind them, flags conflicts between sources, sends revision requests ("that revenue is FY2021; get the latest filing"), escalates identity conflicts.
- **Reporter:** the renewal brief, with confidence and limits stated.
- **Source onboarding (the Track 01 "discovery" part):** when a supplier has no EDGAR tables yet, the agent drafts the `CREATE LIGHTNING REST TABLE` and `CACHE TABLE` statements for its CIK, shows the dry run, and creates them only after the user approves.

**Engines:**

- **H-MEM (must):** remembers confirmed identity matches, user corrections ("the 2025 ticket spike was our warehouse move, not the supplier") and past renewal decisions, with the trust ledger showing why each fact is believed. Demo: the second check on the same supplier starts from memory and asks nothing it already knows.
- **World Model (must):** the shared state (supplier entity, findings, open conflicts) that Resolver, Analyst and Critic read and write.
- **Scout Intent (should):** a guard that lets model-written SQL be read-only; anything that creates goes through the approval path.
- **Markovian (could):** "check all renewals due next quarter" as a long run in bounded steps.

**Nemotron:** the fast lane for Resolver and Analyst, the deep lane for Planner and Critic, both pinned so Nightshift's run details show Nemotron did the work.

**Why it can win.** Impact: renewals are real money and a real job. Sponsor tech: Zetaris joins internal and external data in one SQL query, the agent onboards a source at runtime, and USL data-quality rules feed the critic. Demo: one question, a sourced brief, a conflict the agent escalates, then the "it remembered" second run.

**Risks.** Supplier risk is the guide's own Track 01 example, so others will build near it; the edge is entity resolution, runtime source onboarding and USL checks. The internal data is synthetic; say so. EDGAR covers US-listed companies only; scope to them. Per-supplier REST tables are slow to create, so cache them and pre-onboard the demo suppliers.

### B. Why did demand move? (Track 02)

A city mobility analyst or a fleet dispatcher asks "why did taxi trips from JFK drop on this date?" The agent tests hypotheses against the seeded NY Taxi sample, NOAA GHCN weather (a verified S3 recipe), NYC 311 requests and public holidays, refutes the weak ones with counter-queries (same weekday in earlier weeks), and reports the explanation with evidence and what it ruled out. H-MEM keeps known events and analyst feedback.

Real data, a clear "why" and an easy demo. But the user is weaker, the data is historic, and it depends on which months the NY Taxi sample covers (unknown until Zetaris is installed).

### C. Retraction Radar (Track 01 or 02)

Saved from the Graph Hacks shortlist. "Which references in this manuscript are retracted, why, and which of my references lean on retracted work?" Sources: OpenAlex, Crossref and the Retraction Watch database, which disagree on retraction status.

A real problem with good data. But Zetaris REST tables are fixed URLs, so every reference list needs new tables at runtime, and there is no internal-data side for Zetaris to serve, which is Zetaris's whole pitch.

### D. Wildcard: Lore with Zetaris and Meterless

Allowed (pre-existing code declared, only the extension scored), but the top prize is $1,000 against $2,000, and Lore is still being judged at Graph Hacks. Fallback only.

## How we build it (who does what)

**The constraint:** Zetaris and Nightshift run on Jannet's laptop. A cloud session can't reach that laptop's `localhost`, and Nightshift has no Linux edition. So:

- **Claude (cloud session):** writes the app in TypeScript: engines vendored from the Meterless references with their conformance suites, the agent loop, the Zetaris and Meterless clients, a small web UI with the trace, and tests against **recorded Zetaris responses and a mock Meterless server**. Also `SAMPLE_MODE` for when a source is down. The demo itself always runs live.
- **Jannet (laptop, in Cursor):** keeps Zetaris and Nightshift running, pulls each push, runs the Zetaris source onboarding with Cursor's agent following Zetaris's `AGENTS.md` (dry run first), runs the app end to end, and pastes back errors and outputs (never keys). Records the demo on the laptop.
- This is real Cursor use, and the submission says plainly which parts were Cursor and which were Claude Code. **Confirm on the onboarding call that this mix is acceptable.** The Power prompt itself names Claude Code as one of the assistants it works with, but the Build rule says "you must use Cursor". If the answer is no, Jannet has to do the main coding in Cursor, which changes the plan.

**Two options that cut the round trips (Jannet's call):**

1. **A real Zetaris in the cloud session for testing.** This container has Docker, 4 CPUs, 15 GB of memory and 30 GB of free disk, which meets Zetaris's minimum. It needs the platform bundle and the registry sign-in, added as environment secrets, never pasted in chat. About 30–45 minutes per new container. The credentials are Jannet's own, so check Zetaris's terms first. The demo still runs on the laptop.
2. **Claude Code on the laptop** (in Cursor's terminal), which can reach `localhost` directly.

## Day plan (IST)

| Day | Goal |
|---|---|
| **Oct 21** | Jannet: laptop check, installs, smoke test (3 × PASS). Onboarding call 17:30, with the questions below. Pick the idea |
| **Oct 22** (from 05:30) | Repo created. Engines vendored and their conformance suites passing. Zetaris + Nightshift end to end: one question → one SQL → one answer. Internal sample data designed and loaded |
| **Oct 23–24** | The full loop with the critic, World Model and H-MEM; source onboarding; trace in the UI. Oct 24: the "what would fail tomorrow?" check |
| **Oct 25** | Conflicts, retries, fallbacks, `SAMPLE_MODE`; more than one sample case working |
| **Oct 26** | Feature freeze. README, `data/README.md`, deck, sponsor-tech text; demo video recorded on the laptop; clean-setup test |
| **Oct 27** | Final checks (secrets, declared components, track selected) and **submit by evening IST** |

## Questions for the onboarding call (Oct 21, 17:30 IST)

1. Is Claude Code acceptable alongside Cursor, as long as Cursor is genuinely used for development?
2. Which prize table is right ($2,000 or $1,600 for first)? What are the "additional challenges and prizes"? How do we enter the NVIDIA DGX Spark award: a form field, or automatic?
3. How do we load our own small dataset into a **local** Zetaris: a mounted folder, a JDBC database on the Docker network, or only S3? Can a local Zetaris register a REST endpoint served from the host (`host.docker.internal`)?
4. Does Nightshift on Windows need a dedicated GPU when every lane is an NVIDIA cloud model? Does tool calling (`tools` / `tool_calls`) pass through to Nemotron?
5. Do judges run submissions themselves? The stack needs a local Zetaris (8 GB) and Nightshift. Is a video plus a reproducible README enough?
6. Is one Meterless Engine with its conformance suite passing enough evidence for the Build rule?

## Waiting on Jannet

1. **Laptop check (go / no-go):** OS, total RAM, free disk, GPU. Zetaris needs 8 GB and 4 CPUs given to Docker plus 15 GB free; Nightshift needs Windows with a dedicated GPU or an M1–M4 Mac. If the laptop can't run both, the only other route the guide offers is Zetaris on AWS (about US$1 per 8 hours, on an account with a card), which breaks our no-own-money rule. Then we stop here.
2. **Zetaris:** download the bundle, `docker login`, set the admin email, password and org in its `.env` before the first start, `docker compose pull` and `up -d`, then `./verify.sh` (9 checks), `SELECT 1`, and the Pikachu query. Create a Zetaris API key yourself.
3. **Nightshift:** install, verify the email, add the NVIDIA key in Providers, set up a Nemotron lane, copy the Runtime URL and token from the Console into the project's `.env`.
4. **Cursor:** install, sign in, claim the credit when the organisers post how; check 2 (Composer or Grok creates and runs a hello file).
5. **Smoke test** from the 20 October guide: three PASS lines.
6. **Onboarding call** Oct 21, 17:30 IST, with the questions above.
7. **Pick the idea** (A, B or C) and name it.
8. Optional: decide on either option for cutting round trips.

Keys and passwords go in `.env` files and Nightshift's settings, never in chat or in an issue.

## Where the course material contradicts itself

The "Start Here" lesson (Module 1) is older than the Participant Setup Guide (updated 20 October). **Follow the 20 October guide.**

| Topic | Start Here (old) | Setup Guide, 20 Oct (current) |
|---|---|---|
| Zetaris install | `git clone zetaris/Freemium`, `docker-compose up` of four containers | `zetaris-platform.zip` from Zetaris Cloud, `preflight.sh`, `verify.sh` |
| Zetaris web UI | `localhost:9001`, login `dev@account.com` | `localhost:3000`, the admin you set in `.env` |
| Own files | "anything in `Freemium/customer_data` is visible" | "Zetaris can't read a file sitting on your laptop" |
| Meterless | A credit-funded cloud provider, `METERLESS_API_KEY` | Nightshift runs locally; Runtime token from its Console |
| Engines | Prompt library optional | At least one engine required, working |
| Event dates | — | The Meterless repo's own hackathon guide still says Oct 15–20 and shows a different rubric (Meterless's own); the official dates and rubric are the GenAI Works ones above |
