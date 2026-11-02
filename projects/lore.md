# Lore: who knows what in an open-source project

**Graph Hacks (FalkorDB × WeMakeDevs), Oct 15–18, 2026.** Submitted Oct 18 to all three tracks (Company Brain · Agents That Act on Connected Data · Agent Memory and Coordination). Ported to the Anna app store as **Lore for Anna** on Oct 27 (in App Review).
**Live:** [lore-gh5y.onrender.com](https://lore-gh5y.onrender.com) · **Code:** [github.com/JannetEkka/lore](https://github.com/JannetEkka/lore) · demo [youtu.be/V-Ifwi_jxhg](https://youtu.be/V-Ifwi_jxhg) · [blog post](https://medium.com/@jannetaekka/i-built-a-company-brain-for-open-source-projects-on-falkordb-47f519f9ce08) · Anna port [github.com/JannetEkka/anna-lore](https://github.com/JannetEkka/anna-lore)

## The 30-second version

A newcomer or maintainer asks "who knows the query planner?" or "who should look at this issue?", and the answer usually lives in someone's head. Lore reads a project's public GitHub history into a FalkorDB graph: who wrote and reviewed which PRs, which files each one changed, which issues it fixed. A Gemini agent answers through 12 Cypher tools, cites a PR or issue for every claim, and shows each tool call and query as it runs. It was demoed on the sponsor's own org: 6 FalkorDB repos, 1,357 PRs.

**Measured:** backtested on 300 real merged FalkorDB PRs, scoring everyone as of the day each PR was opened. Lore had a real reviewer in its top 3 **90%** of the time, against 88% for "the repo's most frequent reviewer" and 63% for "the last people to touch the same files". On the single top pick the frequent-reviewer baseline wins overall (61% vs 58%). The README says so.

## 1. Architectural reasoning

### Database / storage
- **Why a graph database:** every question is a multi-hop walk. "Which areas is this issue about?" goes issue → label → other issues → the PRs that fixed them → files → areas: five hops. In SQL that's a chain of self-joins on join tables. In Cypher it's one `MATCH` path, and FalkorDB has the graph algorithms built in (`algo.labelPropagation` for teams, `algo.pageRank`, a full-text index over PR and issue text).
- **Why not a vector DB:** the questions are about relationships (who reviewed whom, what touched what), not semantic similarity. Full-text search covers "where was this discussed?", and every answer has to trace back to a specific PR, which an edge does and an embedding doesn't.
- **Computed edges live in the graph**, built in Cypher at load time: `KNOWS(person, area)` with a score (merged PR 1.0, review 0.6, comment 0.2, halving every 180 days, a PR counted once per area), `WORKS_WITH` and `WORKS_CLOSELY` (5+ reviews between two people).
- **One graph per project and one memory graph per signed-in user** (`user__<login>`), so deleting someone's memory is dropping one graph.
- **Embedded or server:** FalkorDBLite runs embedded by default (no Docker, and the tests need no setup). FalkorDB Cloud is used in production via `FALKORDB_HOST`, so memory and added projects survive restarts.
- **Snapshots:** a gzipped JSON snapshot committed to the repo every 6 hours. It loads into the graph in 0.6 s.

### Compute & hosting
- **Render free plan, Docker**, from a Blueprint (`render.yaml`). It redeploys on every snapshot commit. The image is Debian 13 because FalkorDBLite needs glibc 2.39.
- **Data collection runs in GitHub Actions**, not in the app: a scheduled workflow fetches the history every 6 hours with the workflow's own token and commits the snapshot. This came from a constraint: the build session's proxy refused GitHub's API for unattached repos, so the Action solved that and also kept Lore current, which was a Track 03 point.
- Why not serverless: the app streams agent steps over server-sent events and holds an in-process graph. A long-lived container fits, and the free plan's cold start (up to a minute) is stated on the page.

### Frameworks & libraries
- **FastAPI** for the API and SSE streaming; plain HTML/JS with **Cytoscape.js** for the proof graph. There's no front-end framework, so nothing to build.
- **Gemini function calling** for the agent, with 12 tools, each one a graph query. No agent framework: the tool loop is short, and I needed every step streamed with its Cypher for the "Under the hood" panel.
- **MCP server** (`lore/mcp_server.py`) exposing six of the same graph tools, so Claude Code or Cursor can use Lore's graph directly.
- **Fetching efficiently:** GitHub's bulk endpoints (100 items a call) plus a **blobless `git clone`**. FalkorDB squash-merges, so each commit subject ends in `(#123)`, and `git log --name-only` gives each merged PR's files without spending API calls. Approvals are fetched only for the 150 most recent merged PRs per repo, to fit Actions' 1,000 calls an hour.

## 2. Data & security pipelines

### Authentication & access control
- **Sign in with GitHub, OAuth with no scopes**, so the token can only read public data. The session lives in the server process behind a signed cookie.
- **Per-user isolation is structural:** each person's memory is its own graph, which one click deletes.
- **"Add a project" spends the signed-in user's own GitHub allowance** (12 months, 3 repos, 300 PRs each), not mine. Anonymous visitors use the ready-made projects.
- **Keys:** `GEMINI_API_KEY` is entered in Render's dashboard, never in the repo. Visitors can use their own Gemini key, kept in the browser tab only.

### Data ingestion & flows
- **Scheduled batch:** the Action fetches every 6 hours, commits the snapshot, Render redeploys, and the app loads it at startup. When the loader code changes, the app stores a loader version with each graph and rebuilds the graph (not only when the snapshot changes).
- **On demand:** a signed-in user's project is fetched in the background with live progress.
- **Per question:** the agent picks tools, each runs Cypher, and the steps stream over SSE. Then `/api/proof` returns the evidence subgraph.

### Privacy & compliance
- Public GitHub data only. Lore keeps GitHub logins, **never emails or names**, and skips bots.
- **Triage drafts are never posted.** It's a dry run with a copy button, because an agent posting on someone's issue tracker is a different trust level.
- A `Decision` node (a reason the agent worked out) is **never stored without `SOURCE` edges** to the PRs and issues it came from.
- Gemini is a third-party API: question text and graph snippets go to Google. The data is public, but I'd name it if asked.

## 3. Reliability & failure operations

### State management
- The snapshot in git is the durable state for the ready-made projects, so a restart reloads it.
- With embedded FalkorDB on a free host, user memory and added projects last only until the next restart. With `FALKORDB_HOST` (FalkorDB Cloud) they persist, and a registry graph lists user-added projects after a restart.
- "Since your last visit" originally showed nothing, because each question reset "last seen" to now. It was fixed on 10-18: a visit starts after a 2-hour gap, and memory compares with the start of the previous visit.

### Error handling & fallbacks
- **Model fallback ladder:** when a model is busy, retired or out of free quota, the next one takes over. The model list is read from the key, never hard-coded. A model that just failed goes to the back of the line for a while: retired a day, out of quota 10 minutes, busy 2 minutes. The demo video shows a fallback happening on camera.
- **Suggested questions save their answer** and replay it if every free model is busy.
- **FalkorDB server unreachable → embedded FalkorDB** instead of failing to start, logged, and `/api/me` reports whether graphs are really on a server (added 10-18).
- **Fetch errors:** a repo GitHub refuses is reported by name, and no empty snapshot is written (day 1).
- **Concurrent Action runs:** two runs committing the binary snapshot broke the rebase. Each run now keeps its file aside, resets to the latest main and commits there.

### Logging & observability
- The "Under the hood" panel is user-facing observability: every tool choice and Cypher query streams as it runs, then the Proof graph shows the cited evidence. CLI `--trace` prints the Cypher behind any answer.
- CI runs the tests, builds the image, starts it and checks that the API answers with the snapshot loaded.

## 4. Evaluation & optimisation metrics

### Performance benchmarking
- **Backtest** (`python -m lore backtest FalkorDB`), 300 merged PRs with reviewers, no leakage (scores as of the day the PR was opened, computed in the graph):

| Method | Top pick is a real reviewer | Real reviewer in top 3 |
|---|---|---|
| Lore | 58% | **90%** |
| Most frequent reviewer so far | **61%** | 88% |
| Last people to touch the same files | 42% | 63% |

- **Split by time:** on the newer 150 PRs Lore leads 78% vs 71% on the top pick (97% vs 97% top 3). On the older 150, with little history behind each, the baseline wins the top pick 51% vs 37%. **Lore needs history to know who knows what.**
- **I didn't overfit the weights:** weights tuned on the older half did no better on the newer half, so the original weights stayed.
- **Adaptive areas** came from a quality problem I measured: a fixed two-level directory lumped FalkorDB's `graph/src` into one area of 173 files. Areas now split any directory holding more than 6% of a repo's files, down to four levels, and the copied-in `build/graphblas` (262 files) is ignored.
- 22 tests on embedded FalkorDB; the scoring math in the day-1 tests was checked by hand.

### Cost & resource efficiency
- **₹0 to host:** Render free plan, FalkorDB Cloud free plan, the Gemini free tier, and free GitHub Actions minutes.
- API budget: a blobless clone instead of per-PR file calls; approvals capped at the 150 most recent PRs.
- The Anna port pushes costs further down: the model runs on the *user's* Anna quota, and GitHub calls come from the user's browser (about 40 per repo, cached for 24 h in `anna.storage`).

### System constraints
- Free hosting: the first load after a quiet spell takes up to a minute.
- Without a token there are no approvals (only review comments); GitHub allows 60 unauthenticated calls an hour.
- PRs need a `(#123)` subject or a merge commit to be tied to files; direct pushes are ignored. History is limited to 12 months by default.
- Finding an issue's areas from its words is rough. The agent and the graph signals check each other.

## Lore for Anna (port, Oct 27)
- **Why port Lore and not Wiretrap:** it works on any public repo for any developer, needs no keys of ours, and "nothing in it reads as attack tooling to a reviewer" (DSProjects#46).
- **What changed:** FalkorDB + Cypher became the same graph and scores in plain JS (`bundle/lore.js`). Gemini on our key became `anna.llm.complete` on the user's Anna model with a JSON tool-call loop. The FastAPI server is gone (a static bundle that Anna hosts). Snapshots became `anna.storage`.
- **Tested:** 11/11 engine tests on a real falkordb-py snapshot, 9/9 Chromium smoke tests with a mock Anna SDK, then a real-model run in `anna-app dev`. That found a bug: grouped citations like `[repo#1, repo#2]` weren't linked (fixed in anna-lore PR #1). Jannet loaded `pallets/flask` inside Anna's sandbox (207 people, 195 PRs, 50 issues) and Triage worked.
- **Status:** app 733 `pending_review` since Oct 27; BUIDL submitted on DoraHacks Oct 29. Grants need 200 qualified monthly users, which is a distribution problem, not a build problem.

## What the history shows (real decisions)
- **The rules shaped the build:** "The main coding and design work must begin after the hackathon starts", so prep was notes only and the first commit landed at 00:10 IST on Oct 15. "If the product still works with FalkorDB taken out, it doesn't qualify", so FalkorDB does the scoring and the algorithms, not just storage.
- **The disclosure rules shaped the docs:** a project "entirely generated using AI without meaningful participant contribution" may be rejected, so `EXPLAIN.md` was written for me to read and explain the model, the scoring rule (with a worked example) and every query.
- Day 1 (Oct 14–15): core plus 12 tests → snapshot Action → agent → web app → deploy and CI → backtest → adaptive areas → sign-in, memory, Teams and MCP, all inside ~8 hours of commits.
- Oct 18: the project-overview tool ("How many repos are there?" had no tool to answer from), the embedded fallback, and a less cluttered Proof graph. The cited-evidence-only graph replaced a hairball.
- The snapshot Action is still running (latest commit Nov 1, 06:29 UTC).

## Weak spots to own before they ask
- The top-1 pick loses to a trivial baseline overall. Lore's edge only appears with enough history.
- Built with Claude Code as the coding assistant. I chose the problem, the graph model, the scoring rule and the product, set the requirements and reviewed the code, tests and results (README "Built with AI").
- No result announced yet for Graph Hacks that I have on record.

## Sources
`README.md`, `EXPLAIN.md`, `render.yaml`, `tests/`; commit bodies Oct 14–18 (non-snapshot commits) and the snapshot series to Nov 1; [DSProjects#24](https://github.com/JannetEkka/DSProjects/issues/24) (rules 10-06; night and morning reports 10-14/15); anna-lore README and commits; [DSProjects#46](https://github.com/JannetEkka/DSProjects/issues/46) comments 10-20 to 10-29.
