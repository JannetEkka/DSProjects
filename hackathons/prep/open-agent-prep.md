# Open Agent Hackathon 2026 (GenAI Works): prep

Build window: **Oct 22, 05:30 IST → Oct 28, 05:15 IST** (Oct 22 00:00 UTC → Oct 27 23:45 UTC). Submit on HackOS. Progress: [#23](https://github.com/JannetEkka/DSProjects/issues/23). Event page: [hackathon.genai.works](https://hackathon.genai.works/event/open-agent-hackathon-2026) · submit: [HackOS dashboard](https://hackathon.genai.works/dashboard) · help desk: [HackOS messages](https://hackathon.genai.works/messages) · rules questions: hackathons@genai.works.

This is the brief for the build session. It comes from the course material Jannet pasted on 10-20 (Start Here, How the Week Runs, Welcome Guide, Journey Map, Overview, the APPROACH guide, Event Calendar, FAQ, and the Participant Setup Guide dated 20 October), plus a read of [zetaris/getting-started](https://github.com/zetaris/getting-started) and [Meterless/Meterless](https://github.com/Meterless/Meterless) the same day. There are no workshop videos; the only live session is the onboarding call on Oct 21.

**No project code before the window opens.** "Work committed before the build window opens is not eligible, except for clearly declared pre-existing components." Setting up the laptop (Zetaris, Nightshift, Cursor) is setup, not project code, and should happen before Oct 22. The repo is created and gets its first commit after **Oct 22, 05:30 IST**.

## Go / no-go: Jannet's laptop (10-20): go

The laptop (details in [.claude/CLAUDE.md](../../.claude/CLAUDE.md)) against what the stack needs:

| Need | Laptop | Verdict |
|---|---|---|
| Nightshift, Windows edition (its docs ask for "a dedicated graphics card") | AMD Radeon 610M, integrated | **Passed 10-20.** It installed, ran on the 610M ("Runs Llama 3.2 3B locally") and serves `http://127.0.0.1:8088/v1` |
| Docker: 8 GB memory | 16 GB RAM, **13.8 GB usable** | Tight: about 6 GB left for Windows, Cursor, a browser, Nightshift and screen recording. Restart first, cap WSL at 7 GB, turn off Nightshift's local lanes while using NVIDIA's, and stop Zetaris when not using it |
| Docker: 4 CPUs | Ryzen 5 7520U, 4 cores / 8 logical processors, virtualization on | OK |
| 15 GB free disk | C: about 17–21 GB free after Nightshift, D: about 137 GB free | OK if Docker's disk image and Ubuntu go on D: |

**Hard stop:** if the setup isn't working by Oct 22 midday IST, drop the entry.

## Dates (IST)

| When (IST) | UTC | What |
|---|---|---|
| Oct 21, 17:30–19:00 | Oct 21, 12:00–13:30 | Onboarding call (YouTube live, recording on HackOS). "Additional challenges and prizes" are announced here |
| Oct 22, 05:30 | Oct 22, 00:00 | Build window opens; repo created |
| Oct 23, 05:15 | Oct 22, 23:45 | Registration closes (Jannet registered 10-20) |
| Oct 24 | — | Suggested mid-build check: "if the deadline were tomorrow, what would fail?" |
| **Oct 28, 05:15** | **Oct 27, 23:45** | **Submissions close. Hard deadline; no edits after** |
| Nov 6, 21:30 | Nov 6, 16:00 | Results call on HackOS |

Ties are broken on the Impact score, then on **submission time**, so submit early. Aim for the evening of Oct 27 IST.

The same week: RSNA Knee final (Oct 22/23), Amazon Fire TV (Oct 24, 00:30), IEEE ClimateChain (Oct 25), Build With AI (Oct 27, 02:30), GitLab (Oct 27).

## Rules that shape the entry

- **Required:** Zetaris integrated, Meterless integrated, Cursor used for development. NVIDIA "wherever it contributes"; in practice the product runs on Nemotron through Meterless.
- **Meterless means two things** (setup guide of 20 October):
  - **Build:** at least one **Meterless Engine** (H-MEM, World Model, Markovian, Scout Intent) working in a real feature. "Simply mentioning an engine in your submission, copying a prompt, or adding an unused dependency does not satisfy the Build rule." Show the feature and a passing conformance suite or test.
  - **Power:** the app supports **Meterless Nightshift** as its primary AI provider (OpenAI-compatible, local runtime). NVIDIA's API key goes in Nightshift's Providers tab, never in the app.
- **One primary track** per submission, changeable until the deadline in the team workspace. Cross-track relevance "is not scored twice".
- **Solo is fine**; same pool as teams. Team locks when the first submission is created.
- **Any language, framework or model.** Open-source libraries are fine. AI-generated code is "allowed and expected"; we own it and must be able to explain it.
- **Data:** open, legal, small. No real personal or confidential data. Small synthetic samples are fine. Keep the repo light, add a `SAMPLE_MODE=true` fallback, bound every API call with a timeout.
- **Secrets:** `.env` in `.gitignore`, a `.env.example` with placeholders only, no keys in README, notebooks, screenshots or logs.
- **IP:** we keep all rights; the organiser and sponsors get a licence to show the demo.

### Why Cursor (Jannet asked: "why not you?")

Because the rules require it: "teams must use Cursor as their development environment". Cursor is a sponsor (with SpaceX AI), and the submission has to explain how Cursor was used. Claude still writes most of the code in cloud sessions. Cursor is where Jannet opens, runs and fixes it on the laptop, with Cursor's own agent (Composer or Grok) on the sponsor's free credit. That also saves Claude usage, which ran out once on 10-20. The submission says plainly which parts were Cursor and which were Claude Code. **Ask on the call that this mix is acceptable.** If it isn't, Jannet does the main coding in Cursor and Claude only advises.

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

## Ideas

Jannet wants something fun, and floated two ideas: SMT in Track 02, or a coding teacher that sets tasks, asks you to explain why, and uses games. **Decided 10-20: A, the SQL detective game** (Jannet: "yeah i like the sql learning game too"). It is the coding teacher, pointed at the one kind of coding where Zetaris is the playground instead of a bolt-on. The name is still to be picked. B and C stay below for reference.

| | Idea | Track | In one line |
|---|---|---|---|
| **A** | SQL detective game (chosen) | 02 | Learn to query data by cracking cases; the game master checks every answer against the real data and remembers you |
| B | Why did SMT do that? | 02 | Explains any SMT decision from its own log plus market data, with the evidence |
| C | Supplier renewal check | 01 | Safe and enterprise-y, but not fun |

Dropped: taxi "why did demand move" (depends on the sample's dates, weak user), Retraction Radar (no internal data for Zetaris to serve), Lore as a Wildcard ($1,000 top prize).

### A. SQL detective game (recommended; working names: Case Files, Query Quest, SQL Noir)

**One line:** a detective game that teaches you to query data. The game master gives you a case ("which supplier quietly raised prices after the contract renewed?"). You write SQL to crack it. It runs your query through Zetaris, checks the answer against the data, gives hints, and asks you to explain why your query proves it. It remembers what you got stuck on and builds the next case around it.

**User and problem.** People learning SQL and data analysis: students, bootcamp learners, junior analysts, and new users of a data platform such as Zetaris itself. What they need is fast, correct feedback on real data, and to be made to explain their reasoning. A tutor that is only an LLM can't reliably tell whether your answer is right; this one checks against the data.

**Why it fits the hackathon:**

- **Zetaris does real work:** it is the game board. Cases run on Zetaris's seeded sample data (**confirmed 10-21: `NY_TAXI` and `TPCDS_DB`, the TPC-DS retail benchmark; 39 tables across the two**) and on public sources with verified Zetaris recipes (PokéAPI, SEC EDGAR). Later levels need a join across two sources, which teaches exactly what Zetaris is for. No private data and no file-loading problem.
- **The model proposes, Zetaris proves.** No case is shown until its answer has been checked against live data (exactly one answer, not empty). Every grade comes from comparing result sets, not from the model's opinion.
- **Track: 02 or 03, decided by Oct 26.** The track can be changed in the team workspace until the deadline, and the build is the same either way.
  - **Track 02 (The Agent That Can Explain Why):** every verdict comes with evidence from the data ("your query missed these 3 rows, because…"). Cross-source cases make the agent investigate across sources, and the player has to explain why too. Jannet's own idea was "explain why".
  - **Track 03 (Reasoning Architecture):** memory plus validated data drive the game master's decisions (which case, which hint).
  - On 10-21, during the onboarding call, Jannet said Track 03's prize is low. Both documents already put Track 03 slightly below 01 and 02 ($1,300 vs $1,350 second, or $1,500 vs $1,600 first). **Decided 10-21: Track 02.** The call added nothing new; Jannet confirmed the written material is the latest. Build the evidence panel as a first-class feature.
- **Fun to watch:** case file, clue board, escalating hints, XP and badges, and a trace panel that shows the agents arguing.

**Agents (a loop, not a chain):**

- **Case Designer** (deep lane): writes a case from the schema and the learner's memory, aimed at a weak skill.
- **Validator:** writes the reference query, runs it on Zetaris, and checks the answer is unique and non-empty. If not, it sends the case back with the reason. A case is never posed until it passes.
- **Game Master:** runs the play. Scout Intent sorts each learner message (SQL to run, hint request, explanation, chat) and keeps SQL read-only.
- **Grader:** runs the learner's SQL on Zetaris, compares the result with the reference, and produces the evidence (missing rows, extra rows, wrong column).
- **Coach** (fast lane): hints that escalate (nudge → concept → partial query), then the "why" question. It grades the explanation against the evidence and follows up when it's vague.
- **Memory:** after each case, H-MEM records skills mastered and misconceptions (for example "filters an aggregate with WHERE instead of HAVING"), with the trust ledger showing where each came from.

**Engines:** **H-MEM (must)**: the learner model across sessions; in the demo, the player comes back the next day and the first case targets yesterday's weak spot. **World Model (should)**: the shared case state (case, clues found, hints used, score) that the agents read and write. **Scout Intent (should)**: message routing and the read-only guard, visible in play ("that DROP TABLE won't run here, detective"). **Markovian (could)**: a long campaign in bounded steps.

**Nemotron:** fast lane (`nemotron-3.5-lightning-30b-a3b`) for the Game Master and Coach; deep lane (`nemotron-3-super-120b-a12b`) for the Case Designer and Validator; both pinned so Nightshift's run details show Nemotron did the work.

**Demo (about 3 minutes):** a new player opens case 1 → a wrong answer → a hint built from the evidence → solved → "why does your query prove it?" → the next day it remembers → a cross-source case where Zetaris joins two sources → the trace panel showing the Validator rejecting a broken case.

**Risks.** Generated cases can be bad, which is what the Validator is for. Zetaris queries can be slow, so cache the REST tables. Zetaris speaks Lightning SQL (Spark-like), so the Coach has to translate its error messages.

### B. Why did SMT do that? (Track 02)

An agent that explains any SMT decision ("why did it buy SOL at 14:00?", "why did it sit out yesterday?"). It investigates SMT's own decision log alongside public market data (prices, volume, funding rates) and shows the evidence for each step; a critic checks every claim against the data. Real data, Jannet's own bot, and a clean Track 02 fit. Two things decide it:

1. Where SMT's decision logs live, and whether a local Zetaris can read them. An HTTP endpoint SMT already serves would work as a REST table; files on the laptop would not.
2. Our earlier rule that SMT shows no PnL in public. Explaining trades in a public demo and repo may cross it.

SMT itself would be declared as pre-existing; the explainer is new work.

### C. Supplier renewal check (Track 01)

Before a supplier contract renews, an agent pulls together what every system knows about the supplier: synthetic internal ERP, ticket and contract data plus SEC EDGAR and SIC codes, on Zetaris's verified recipes and its USL data-quality rules. It finds where the systems disagree and recommends renew, renegotiate or escalate, with every fact traced to its query. A safe entry with a strong sponsor-tech story, but it's the guide's own Track 01 example and not fun.

## The stack, as it actually works (checked 10-20)

### Data: Zetaris, local in Docker

- Get `zetaris-platform.zip` and the registry sign-in from Zetaris Cloud's [Run locally page](https://cloud.enterprise.zetaris.com/dashboard/download). Needs **8 GB of memory and 4 CPUs given to Docker, 15 GB free disk**. First pull and start take 30–45 minutes.
- Set `ZETARIS_ADMIN_EMAIL`, `ZETARIS_ADMIN_PASSWORD` and `ZETARIS_ADMIN_ORG` in the bundle's own `.env` **before the first start**; changing them later doesn't reset the account. Keep `ZETARIS_SEED_TPCH=true` for the supplied sample data.
- Web UI and SQL Editor on `localhost:3000`. REST on `http://localhost:8888/api/v1.0`. JDBC on port 10000. Never call 8889.
- **REST call:** `POST /sql-editor/sqls/run` with `Authorization: Bearer <ZETARIS_API_KEY>`, `X-Org-ID: 1` (local), and a fresh UUID `X-Request-ID`. Body: `{"queryId": <uuid>, "sql": "...", "source": "SqlEditor", "limit": N}`. Rows come back in `data`. 401 = bad key; 400 = bad org ID or non-UUID request ID. The API reference is served at `localhost:8888/redoc/index.html`.
- **SQL is Lightning SQL**, not Spark or Hive SQL: one statement per call, no trailing semicolon, qualified names.
- **A REST table is one fixed URL.** `CREATE LIGHTNING REST TABLE ... REQUEST(endpoint "...")`, then a `CREATE SCHEMASTORE VIEW` with `LATERAL VIEW explode(...)` to flatten it. It **re-fetches the source on every query** unless you `CACHE TABLE` it (one test went from 49.7 s to 1.2 s). Per-entity lookups need one table per entity; the EDGAR recipe makes one table per company.
- **Files:** only from S3 or S3-compatible storage. "Zetaris can't read a file sitting on your laptop."
- **Verified recipes** in the getting-started repo: PokéAPI, SEC EDGAR company facts and submissions, `company_dns` SIC / NACE / Japan codes, Eurostat, ABS, StatCan, Open Food Facts, NASA NeoWs, NOAA GHCN (S3), AWS public blockchain (S3), and a USL model joining EDGAR to SIC with a foreign-key data-quality rule. Known to fail: PUDL, Foursquare, Overture, Ookla, GBIF, Singapore PM2.5, NASA DONKI.
- The repo's `AGENTS.md` is written for coding agents (Cursor, Claude Code, Codex): preflight first, read-only first, dry-run before any create, never print keys.

### Build: Cursor and the Meterless Engines

- Cursor with its own models (Composer for speed, Grok for longer work) on the Cursor credit. Keep every Meterless and NVIDIA key out of Cursor's settings. How to claim the credit is still "[Organisers: add ...]" in the guide.
- **Engines are implementation specs, not npm packages:** each folder in `engines/` has an `AGENTS.md` contract, a runnable **TypeScript** reference (H-MEM, World Model, Markovian), examples and a conformance suite, run as `HMEM_IMPL=/abs/path/index.ts npx tsx conformance/runner.ts`. Scout Intent is spec plus an eval harness.
- `templates/agentathon-starter` is a TypeScript CLI that vendors the H-MEM reference and maps each command to a named engine service, which is what judges look for.
- **So the build is TypeScript (Node).** Python would mean re-implementing an engine to pass a TypeScript conformance runner.
- The prompts at [meterless.ai/engines.html](https://meterless.ai/engines.html) (Ideate, Implement, Combine, Harden, Power) are written for Cursor or Claude Code.

### Power: Nightshift, with Nemotron behind it

- Nightshift is a desktop app: Windows, Mac (free M1+ edition for M1–M4; the M5+ edition is a $199 preorder), or DGX Spark. No Linux edition, so it can't run in a cloud session. Its docs ask for a dedicated GPU on Windows, but **it installed and runs on Jannet's integrated Radeon 610M** (10-20, free). On first launch it downloads about 3.8 GB of local models (Llama 3.2 3B, a memory index, voice) into `%LOCALAPPDATA%` on C:.
- **One NVIDIA key covers every model** on [build.nvidia.com](https://build.nvidia.com/models) (free endpoints, rate-limited). It goes in Nightshift **Setup → Providers → NVIDIA**.
- **Free-endpoint Nemotron models listed on 10-20:**
  - `nemotron-3.5-lightning-30b-a3b`: fast agentic MoE.
  - `nemotron-3.5-super-vl-120b-a12b`: early access, 5 days old; reasoning, tool calling, multimodal.
  - `nemotron-3-ultra-550b-a55b`: 1M context; big and slow.
  - `nemotron-3-nano-omni-30b-a3b-reasoning`.
  - `nemotron-3-embed-1b`: embeddings.
  - `nemotron-3.5-content-safety`.
- **Lanes:**
  - Lane 1, fast: `nemotron-3.5-lightning-30b-a3b`, for the Game Master, Coach and intent routing.
  - Lane 2, deep: `nemotron-3-super-120b-a12b` (the guide's pick) if Nightshift lists it, otherwise `nemotron-3.5-super-vl-120b-a12b`, for the Case Designer and Validator.
  - Use the exact names Nightshift shows. Turn the local lanes off while working, to save memory.
- The app gets the **Runtime URL and token from Nightshift's Console** (top right), e.g. `METERLESS_BASE_URL=http://127.0.0.1:8088/v1`, `METERLESS_RUNTIME_TOKEN=...`, `METERLESS_MODEL=meterless/auto`.
- **Provider contract** (the "Add Meterless as a provider" prompt, Runtime 1.4): `Authorization: Bearer <token>` on every call; `meterless-app: <app id>` on every call; `meterless-scope: user` on chat; `GET /v1/models` decides online / unauthorized / offline (`/healthz` only proves the process is up); `POST /v1/chat/completions`; 180 s timeout; model ids are routing modes (`meterless/auto|fast|deep|cheap|local|fusion`, `meterless/<class>.<disposition>`).
- **Tool calling:** Nightshift's setup screen advertises the endpoint as "OpenAI-compatible · streaming · tool calls" (10-20). Confirm with a real `tools` request on day 1, and keep a JSON-output fallback.
- **Jannet's Nightshift (v1.2.1), 10-20:** two cloud lanes, both "ready" with "nvidia accepted the key", both on the Race duty: `nemotron-3-super-120b-a12b` and `nemotron-3.5-lightning-30b-a3b`. No local lanes.
  - Nightshift warns that no lane has the Judge or Verify duty, which its own judging needs; its suggested fix is Verify on the Super lane.
  - A red banner said the runtime endpoint was offline to external apps ("Fix endpoint"). Jannet fixed it 10-20.
- **Power test passed 10-20.** From PowerShell with the Console token, `POST /v1/chat/completions` on `meterless/auto` answered "The connection is working perfectly." Nightshift's Monitor showed "via providers 100%, answered locally 0%, cloud · nvidia".
  - `GET /v1/models` also lists dozens of `local-runtime/*` models (Qwen, DeepSeek, Nemotron Nano and others). Most are far too big for this laptop; never route to them.
  - During the test the laptop showed cpu 96%, mem 94% and "thermal hot". Quit Nightshift when it isn't needed, and restart Windows before installing Docker.

## Setup on Jannet's laptop (Windows), step by step

Do these in order and send back **PASS or the exact error text** after each step. Never send keys, passwords or the registry sign-in command. Everything heavy goes on **D:**, because C: has about 10 GB free.

**Step 0: check the CPU and GPU.** Done 10-20: Ryzen 5 7520U (8 logical processors), Radeon 610M only.

**Step 1: Nightshift, then NVIDIA (20 min).** **Done 10-20:** wizard finished, NVIDIA key accepted, two Nemotron lanes ready, endpoint fixed, and a PowerShell test answered through NVIDIA. The steps, for the record:

1. Finish Nightshift's 5-step setup wizard. Don't press "Skip setup".
2. **NVIDIA key, one for all models:** on [build.nvidia.com](https://build.nvidia.com/models), open `nemotron-3.5-lightning-30b-a3b` and click **Get API Key** → Generate → copy the key (it starts with `nvapi-`). If it asks for a card or payment, stop and tell me. Paste the key only into Nightshift, never into Cursor, a file in the project, or chat.
3. In Nightshift: **Setup → Providers → NVIDIA**, paste the key and save. Refresh the model list if needed.
4. **NIGHT → LANES:**
   - Lane 1: `nemotron-3.5-lightning-30b-a3b`.
   - Lane 2: `nemotron-3-super-120b-a12b` if it's listed, otherwise `nemotron-3.5-super-vl-120b-a12b`.
   - Turn off the local Llama and voice lanes while working, to save memory.
5. Run a short test inside Nightshift. Send a screenshot that shows which model answered, with the key hidden.
6. If Nightshift's settings let you move its models folder to D:, do it; it holds about 3.8 GB on C: now.

**Step 2 — free space on C: (10–20 min).** Aim for 20 GB free. Settings → System → Storage → Cleanup recommendations and Temporary files. Move the Downloads folder to D: (right-click Downloads → Properties → Location → `D:\Downloads` → Move).

**Step 3 — WSL with Ubuntu on D: (15 min).** In PowerShell as administrator:

```powershell
wsl --install --no-distribution
# restart Windows, then:
wsl --update
wsl --install Ubuntu --location D:\WSL\Ubuntu
```

If `--location` isn't recognised, run `wsl --install Ubuntu` and then `wsl --manage Ubuntu --move D:\WSL\Ubuntu`. When Ubuntu opens, create a Linux username and password.

**Step 4 — cap WSL's memory and keep its swap on D: (2 min).** Restart Windows first; on 10-20, 12.1 of 13.8 GB was in use after 5 days without a restart. Then create `C:\Users\<you>\.wslconfig` containing:

```ini
[wsl2]
memory=7GB
swap=6GB
swapFile=D:\\WSL\\swap.vhdx
```

Then run `wsl --shutdown` in PowerShell. 7 GB is under the guide's 8 GB but over the 6 GB where preflight fails, and it leaves about 6.8 GB for Windows. If Zetaris containers keep restarting, raise it to 8 GB and close other apps.

**Step 5 — Docker Desktop (20 min).**

1. Install Docker Desktop. The program goes on C:, which is why Step 2 comes first.
2. Before pulling anything, open Settings → Resources → Advanced → **Disk image location** → `D:\Docker` → Apply & restart.
3. Settings → Resources → WSL integration → turn on **Ubuntu**.
4. In Ubuntu, check that `docker version` and `docker compose version` both answer.

**Step 6 — Zetaris (about 1 hour, mostly waiting).**

1. From the [Run locally page](https://cloud.enterprise.zetaris.com/dashboard/download), download `zetaris-platform.zip` and copy the registry sign-in command it shows.
2. In Ubuntu:

   ```bash
   sudo apt update && sudo apt install -y unzip
   cp /mnt/d/Downloads/zetaris-platform.zip ~/ && cd ~ && unzip zetaris-platform.zip && cd zetaris-platform
   # paste the registry sign-in command from the Run locally page here
   ./preflight.sh
   nano .env
   ```

   In `.env`, set:
   - `ZETARIS_ADMIN_EMAIL` and `ZETARIS_ADMIN_ORG`.
   - `ZETARIS_ADMIN_PASSWORD`: 8+ characters, with an uppercase letter, a lowercase letter, a digit and one of `$ @ ! % * ? &` (no other punctuation).
   - The laptop values: `ZSPARK_DRIVER_MEM=2g`, `ZSPARK_DRIVER_CORES=2`, `ZSPARK_MASTER_URL=local[2]`, `ZETARIS_API_MAX_HEAP=1g`, `UI_PORT=3000`, `ALLOWED_ORIGINS` and `GUI_URL` both `http://localhost:3000`, `COMPOSE_PROFILES` empty, `ZETARIS_SEED_TPCH=true`.

   Save with Ctrl+O, Enter, Ctrl+X. Then:

   ```bash
   chmod 600 .env && docker compose config --quiet
   docker compose pull && docker compose up -d
   docker compose ps --all     # wait until init and bootstrap show Exited (0)
   ./verify.sh                 # all 9 checks should pass
   ```

3. Open `http://localhost:3000`, sign in, open the SQL Editor and run `SELECT 1 AS one`.
4. Create an API key in the web UI and keep it in a password manager. It goes into the project's `.env` on Oct 22.
5. When you're not using Zetaris, run `docker compose stop` to free memory, and `docker compose start` to resume. Never run `docker compose down -v`: it deletes everything.

**Step 7 — Cursor (10 min).** Install and sign in. Claim the credit once the organisers say how (expected on the call). Then ask Cursor's agent, on Composer or Grok, to create and run a Python file that prints `hello`.

**Step 8 — smoke test:** on Oct 22, as the first thing in the new project.

## How we build it (who does what)

**The constraint:** Zetaris and Nightshift run on Jannet's laptop. A cloud session can't reach that laptop's `localhost`, and Nightshift has no Linux edition. So:

- **Claude (cloud session):** creates the repo after 05:30 IST on Oct 22 and writes the app in TypeScript: engines vendored from the Meterless references with their conformance suites, the agent loop, the Zetaris and Meterless clients, a small web UI with the trace, and tests against **recorded Zetaris responses and a mock Meterless server**. Also `SAMPLE_MODE` for when a source is down. The demo itself always runs live.
- **Jannet (laptop, in Cursor):** keeps Zetaris and Nightshift running, pulls each push, runs the app end to end, uses Cursor's agent for the local wiring and fixes, and pastes back errors and outputs (never keys). Records the demo on the laptop.
- **Jannet's time:** about 2–3 hours of setup before Oct 22, then roughly an hour a day to run, test and send results, plus about 2 hours on Oct 26 for the demo video.
- **Optional, to cut round trips:** a real Zetaris inside the cloud session for testing. The container has Docker, 4 CPUs, 15 GB of memory and 30 GB of free disk. It needs the platform bundle and registry sign-in as environment secrets, never pasted in chat; the credentials are Jannet's own, so check Zetaris's terms first.

## Day plan (IST)

| Day | Goal |
|---|---|
| **Oct 20–21** | Jannet: setup steps 1–7 (Nightshift installed 10-20). Onboarding call Oct 21 at 17:30 with the questions below. Pick the game's name |
| **Oct 22** (from 05:30) | Repo created. Engines vendored and their conformance suites passing. Zetaris + Nightshift end to end: one question → one SQL → one answer. **Hard stop at midday if the setup still isn't working** |
| **Oct 23–24** | The full agent loop with the critic, World Model and H-MEM; the trace in the UI. Oct 24: the "what would fail tomorrow?" check |
| **Oct 25** | Retries and fallbacks, `SAMPLE_MODE`; several sample cases working |
| **Oct 26** | Feature freeze. README, `data/README.md`, deck, sponsor-tech text; demo video recorded on the laptop; clean-setup test |
| **Oct 27** | Final checks (secrets, declared components, track selected) and **submit by evening IST** |

## Paused 10-22, resume Mon Oct 26 after 17:30 IST

Jannet's Claude usage was at 84% on 10-22, and it resets Mondays at 17:30 IST. The Amazon, Orchestrate and GitLab entries come first. From the reset to the deadline (**Wed Oct 28, 05:15 IST**) is about 36 hours, and GitLab is also due Oct 27 at 18:30 IST.

**Done:**
- Laptop: Zetaris, Nightshift with two NVIDIA lanes, Docker, WSL, Node, Git and Cursor, with the repo cloned at `D:\code\sql-noir`.
- [sql-noir](https://github.com/JannetEkka/sql-noir), 6 commits, 36 tests passing, H-MEM conformance 13/13:
  - the Zetaris client and read-only SQL guard;
  - the Meterless provider;
  - the evidence-based grader;
  - the case validator and six seed cases;
  - the smoke test, schema recorder and case validation scripts.

**Restart order on the laptop:**
1. Docker Desktop.
2. Ubuntu: `cd ~/zetaris-platform && docker compose start`.
3. Nightshift.
4. Cursor, opening sql-noir, then `git pull`.
5. Fill in the two keys with `notepad .env`.
6. `npm run smoke`, `npm run record:schema`, `npm run validate:cases`, and send the output to Claude.

**What's left, smallest version that can win:**
- the coach on Nemotron (hints and the "why" question, built from the grader's evidence);
- H-MEM player memory;
- a single-page web UI with the evidence panel and agent trace;
- a case designer only if time allows (seed cases are enough to play);
- a README a judge can follow from scratch, the deck, and a 2–3 minute video.

**Cut first if short of time:** the case designer, then Scout Intent and World Model.

## Organisers' answers (Israel Hosana, help desk, 10-22)

1. **Claude Code alongside Cursor:** yes, it's okay.
2. **One Meterless Engine (H-MEM) enough for the Build rule:** yes.
3. **NVIDIA DGX Spark award:** anyone using Nemotron through Nightshift is considered.
4. **Judges run the project themselves,** and the video helps too. So the README's setup must work for someone starting from scratch: Zetaris, Nightshift with an NVIDIA lane, Node and `.env`, step by step.
5. **The SQL game fits Track 02:** yes.
6. **Video:** an unlisted YouTube link is fine, or Google Drive with access granted.

## Questions for the onboarding call (Oct 21, 17:30 IST)

1. Is Claude Code acceptable alongside Cursor, as long as Cursor is genuinely used for development?
2. Our Zetaris runs with 7 GB on a 16 GB laptop (13.8 GB usable). Is that enough with the laptop settings, or will it fall over?
3. Which prize table is right ($2,000 or $1,600 for first)? What are the "additional challenges and prizes"? How do we enter the NVIDIA DGX Spark award?
4. How do we get our own small dataset into a **local** Zetaris? Can a local install read a mounted folder, or a REST endpoint served from the host (`host.docker.internal`)?
5. Does tool calling (`tools` / `tool_calls`) pass through Nightshift to Nemotron?
6. Do judges run submissions themselves, given the stack needs a local Zetaris and Nightshift? Is a video plus a reproducible README enough?
7. Is one Meterless Engine with its conformance suite passing enough for the Build rule?

## Waiting on Jannet

1. ~~Step 1~~: done 10-20.
2. Restart Windows, then steps 2–7 (WSL and Docker on D:, Zetaris, Cursor).
3. The onboarding call, Oct 21 at 17:30 IST, with the questions above.
4. A name for the game.

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
