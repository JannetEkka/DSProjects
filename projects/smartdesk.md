# SmartDesk: a multi-agent assistant with measured RAG

**Google Cloud Gen AI Academy APAC 2026, Cohort 1 hackathon (Multi-Agent Productivity Assistant): shortlisted top 101 of 1,500+ teams.** Built Apr 3–8, 2026; the retrieval evaluation was added Aug 11–14, 2026 (PRs #1–#8).
**Code:** [github.com/JannetEkka/smartdesk](https://github.com/JannetEkka/smartdesk) · [eval results](https://github.com/JannetEkka/smartdesk/blob/main/evals/RESULTS.md) · was deployed on Cloud Run (GCP project `smartdesk-505315`). The ROADMAP records that the last deployed revision fails at import, and the GCP billing account closed on 10-02, so **there's no live link**. Say so.

## The 30-second version

One chat interface over three agents (email, calendar, a personal knowledge base), so "what's on my plate today?" spans all three. A root **Google ADK** orchestrator routes to `inbox_agent` (Gmail), `planner_agent` (Calendar) and `data_agent` (retrieval over Postgres/pgvector). Gmail and Calendar are reached through **MCP servers I wrote** against the protocol SDK over stdio, not off-the-shelf toolsets.

**The point is the evaluation.** 40 labelled questions over 120 notes, recall@k and MRR@k, significance by **paired bootstrap at 10,000 resamples**. A cross-encoder reranker looked like the one significant win on the development embedder (MiniLM: MRR@10 **+0.094**, p = 0.04) and **collapsed on the production embedder** (text-embedding-005: +0.028, CI [−0.041, +0.101], p = 0.44). Shipping it would have taken search from **29 ms to 2,382 ms (82×)** and added ~190 MB of PyTorch to an image deliberately cut from **1.8 GB to 340 MB** to fix cold starts. **The plain baseline ships, on evidence** (R@5 0.963).

## 1. Architectural reasoning

### Database / storage
- **Postgres + pgvector** (`VECTOR(768)`, cosine `<=>`), AlloyDB in production and plain Postgres 16 + pgvector in development: **the same schema and operator on both**. Why relational + vector in one place: notes and tasks are structured rows (titles, due dates) *and* need similarity search, so one database does both, and the agent's other tools (`add_task`, `update_task`) are plain SQL.
- **Embeddings computed client-side** and bound as a query parameter, not through AlloyDB's in-database `embedding()`. That's what lets identical code run on AlloyDB and plain pgvector.
- **Two indexes:** `notes.content_embedding` (whole note) and `note_chunks.content_embedding`, through an **additive, reversible migration** (`001_note_chunks.sql`). `add_note` keeps both current, so retrieval modes can switch freely by env var.
- **Neon** (serverless Postgres, free tier, scales to zero) became the hosted DB for the deployment, because pgvector works the same and AlloyDB costs money.
- Why not a dedicated vector DB: 120 notes. Postgres handles it in ~29 ms, and a separate store would add a sync problem.

### Compute & hosting
- **Cloud Run, scaling to zero**, so an idle deployment costs nothing and the first request after quiet takes ~1.4 s. The image was cut from 1.8 GB to 340 MB to fix cold starts, which is why a 190 MB PyTorch dependency was a real cost, not a footnote.
- The UI is ADK's own dev UI (`adk web`, or `/dev-ui` on the service). There's no custom frontend.

### Frameworks & libraries
- **Google ADK 1.14** for orchestration (root agent + sub-agents via `transfer_to_agent`; state via `tool_context.state` and `output_key`). It was the hackathon's framework, and its callbacks turned out to be the fix for the auth bug below.
- **MCP servers written from scratch** (`gmail_server.py`, `calendar_server.py`: `Server()`, `stdio_server()`), consumed with `MCPToolset(StdioServerParameters(...))`. Why my own: I needed control of the OAuth flow, and it's vendor-neutral.
- **No retrieval framework:** plain SQL, ~20 lines of BM25, reciprocal rank fusion written out. "The mechanics stay legible so a moving number can be explained."

## 2. Data & security pipelines

### Authentication & access control
- **Per-user Google OAuth 2.0 through the chat:** each user signs in with their own Google account and sees only their own email and calendar. The token is session-scoped. The OAuth app is **unverified**, so only Google accounts on the consent screen's **test users** list can sign in (others get a 403), and judges had to send their email to be added.
- **The OAuth + LLM integration bug (Apr 6–8), the best FDE story here:** about 25 commits fighting one problem. The model kept **duplicating or re-calling the login URL** (calling `login_google` repeatedly, printing two links, the root agent re-processing after a sub-agent returned). Attempts in order: state guards, module-level dedup, `skip_summarization`, `after_model_callback` stripping URLs, invocation-id scoping. The fix that held: a **`before_model_callback` injects the auth URL so the model never sees it**, plus a simple `_transferred` flag. Lesson: **keep secrets and links out of the model's context entirely** rather than asking it not to repeat them.
- OAuth flow variants found along the way: Desktop OAuth, then a manual copy-paste flow for Cloud Shell, then localhost redirect allowances. OAuth clients are per-project, so `client_secret.json` doesn't move between GCP projects. That's documented as the step "that catches people out".
- Secrets: `client_secret.json` and `token.json` are git-ignored; the setup script masks secrets when it echoes them.

### Data ingestion & flows
- Request/response: chat → root agent checks auth → routes → the sub-agent calls an MCP server (stdio subprocess, a 60 s timeout, API service objects cached) or SQL → the sub-agent formats its own reply.
- The eval is a batch harness: `ingest.py` (build both indexes, ~9 s on CPU) → `harness.py` (all strategies, deltas, bootstrap, latency) → `--save` writes per-question JSON so runs can be diffed.

### Privacy & compliance
- A single-user design: OAuth and session state assume one user, and the README says so.
- **The eval corpus is synthetic about real threads:** the notes and 40 labels were written for the eval, not kept at the time, and every question is flagged `reviewed: false`. The harness warns until that changes. Real Gmail and Calendar data is never in the repo.

## 3. Reliability & failure operations

### State management
- ADK session state carries the request and sub-agent outputs (`output_key="inbox_data"`), and the auth state is guarded so re-login and account switches don't loop (`switch_account` replaced a separate logout tool).

### Error handling & fallbacks
- An MCP timeout raised to 60 s; date and datetime serialised to ISO strings in query results (a real crash early on); `due_date` default changed from `None` to an empty string.
- **The deploy failure documented as the top blocker:** `adk deploy cloud_run ./smartdesk_app` copies only the agent directory and generates its own Dockerfile, so the root `requirements.txt` never reached the image: `No module named 'google_auth_oauthlib'`. The fix (a requirements file inside the app directory) is committed but wasn't redeployed. The env-var gotcha is recorded too: the `^|^` delimiter is needed because the Neon URL contains `@` and `:`.

### Logging & observability
- The harness prints per-query latency and the significance table; results are committed (`evals/results/*.json`) so regressions can be diffed.

## 4. Evaluation & optimisation metrics

### Performance benchmarking (production embedder, text-embedding-005)

| strategy | R@1 | R@5 | MRR@10 | latency |
|---|---|---|---|---|
| **baseline (shipped)** | 0.800 | **0.963** | 0.886 | **29 ms** |
| chunked | 0.800 | 0.963 | 0.885 | 24 ms |
| hybrid (RRF) | 0.775 | 0.950 | 0.870 | 52 ms |
| chunked + RRF | 0.750 | 0.975 | 0.859 | 37 ms |
| rerank (cross-encoder) | 0.838 | 0.950 | 0.914 | 2,382 ms |

- **Nothing is significant.** The four free strategies are all negative (p 0.37–0.64). The cross-encoder: +0.028 MRR@10, CI spans zero, 5 better / 4 worse.
- **Every reranker flipped from helping to hurting** when the embedder got better (chunked+RRF +0.047 on MiniLM → −0.027). The mechanism was predicted before the run: a stronger embedder leaves less for a reranker to fix and more for it to break. With the top 5 already right 96% of the time, reordering has more to lose.
- **Chunking alone didn't help** (−0.003): only 6 of 120 notes were long enough to split. A title prefix on later chunks measurably beat plain chunking.
- **Statistical honesty:** at 40 questions one question is worth 0.025 of R@1. The MiniLM p = 0.04 was uncorrected across six strategies.
- 54 tests (chunking overlap and termination, metrics, rerankers, a DB integration test skipped without a DB).

### Cost & resource efficiency
- Scale-to-zero Cloud Run, Neon free tier, the dev loop on local Postgres (₹0), CPU-only eval wheels. A full harness run with the Gemini reranker is about $0.05 on Vertex. The **latency and image-size cost** is what killed the reranker.

### System constraints
- Single user; an unverified OAuth app (test users only); 120 notes and 40 unreviewed labels; cold start ~1.4 s.

## What the history shows (real decisions)
- **Apr 3–8 (hackathon):** scaffolding matched to the codelab patterns, then MCP servers, then three days on the OAuth-in-chat flow, then the PPT and demo script. Shortlisted top 101 of 1,500+.
- **Aug 11–14 (after the hackathon):** the eval harness first, *then* chunking and rerankers, *then* significance testing, then the corpus rebuilt around the actual single user. The production-embedder re-run reversed the conclusion, and RESULTS.md §0 was written to say so first.

## Weak spots to own before they ask
- Not live now (the deploy blocker plus GCP billing closed).
- The labels aren't human-reviewed; I'd say the numbers are relative comparisons on one corpus, not ground truth.
- Built with Claude Code as the coding assistant; I ran the OAuth and deployment steps and made the ship/don't-ship call.

## Sources
`README.md` (architecture, auth, deployment, eval), `evals/RESULTS.md` §0, `ROADMAP.md` (deploy blocker), git log Apr 3–11 and Aug 11–14 (PRs #1–#8); `interview-prep/01-inventory.md` (MCP evidence).
