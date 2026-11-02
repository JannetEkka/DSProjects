# Proof of Fix: an issue closes on production evidence, not on a merge

**GitLab "Life After Code" (Transcend) hackathon.** Path A (Start Fresh), autonomy **Supervised**, plus Most Stages Covered (all nine DevSecOps stages). Built Oct 21–26, 2026; submitted final by 00:10 IST Oct 27. Frozen after 18:30 IST Oct 27 until winners (~Nov 16).
**GitLab project (public, MIT):** [gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43596350/showcase](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43596350/showcase) · the real run: [work item #2](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43596350/showcase/-/work_items/2) · video 2:20 [youtu.be/tec52HoWT5A](https://youtu.be/tec52HoWT5A) · GitHub mirror `JannetEkka/proof-of-fix` (private)

## The 30-second version

"Closed" usually means "a merge request merged", and nobody checks that users stopped hitting the bug. Now agents write the fix, pass the tests and merge themselves, so the gap gets wider: tests check the case someone thought of, production runs every case. In Proof of Fix, a Duo triage flow reads production logs and writes a **proof contract** into the issue before anyone writes the fix: the log line that must stop, the event the fix must start emitting, and the watch window. After deploy, the pipeline judges the shipped build on its own logs. The issue closes with a receipt, or stays open with the lines that show the bug is still there, and a Duo verdict flow works out what the fix missed.

**The real run on GitLab (work item #2):** triage found the rounding failure on **two** routes (230 errors on `/split/equal`, 158 on `/split/shares`, of 1,180 requests). The first fix covered only the reported route and passed tests, the contract gate and **Duo Code Review**. Production said no: failures fell from **32% to 9%** of requests, all on the second route, so the issue stayed open. The verdict flow named the missed function, the Duo Developer flow wrote the second fix, Duo Code Review caught a real edge case in it (a weight of 0 could be charged the leftover paisa) and approved. After that deploy: **0 failures on 875 requests**, the new event seen 375 times, and the issue closed itself with a receipt and release `prod-24`.

## 1. Architectural reasoning

### Database / storage
- **Logs are the database.** The checker queries production logs (GitLab Observability through its SigNoz v5 API, or local JSON lines for tests) filtered by `service.version`, the commit that shipped. **Only the deployed build counts**, so errors from an old instance draining can't fail a good fix, and quiet hours can't pass a bad one.
- **The contract lives in the issue** (Markdown the checker parses), and the **receipt lives in the issue and in a GitLab release.** The audit trail is where engineers already look, not a separate store.
- **Deploy state is a registry tag:** deploying is retagging `:production` in the GitLab container registry (`proof/registry.py`), and rollback is retagging the previous build. The registry is the source of truth for what's live.

### Compute & hosting
- **GitLab CI does the work** (tests, gate, scans, image build, deploy, `proof-watch`, rollback, verdict, release), with a `production` environment and a `resource_group` so **only one build is ever under watch**.
- **Production is billsplit on Render's free tier.** It first ran on an Oracle Cloud VM with cloud-init and a deployer following the repo (10-21, 16:09), and moved to Render an hour later (17:16) to simplify. Render's 750 free instance hours a month are shared, so synthetic users no longer run around the clock: CI runs them inside the deploy and proof jobs, and the deploy wakes the sleeping service and measures the old build for `BASELINE_MINUTES` first, so there's a before rate to compare.
- **Duo flows run on GitLab's agent runtime** (`.gitlab/duo/agent-config.yml` sets the runtime and network policy).

### Frameworks & libraries
- **GitLab Duo Agent Platform** was mandatory (stage one of judging is pass/fail on it): two custom flows in the AI Catalog (triage on a *Work item created* trigger, verdict on mention and via the Flows API from CI), handing off to the foundational **Developer** flow, with **Code Review** on MRs and `AGENTS.md` for the rules.
- **billsplit:** FastAPI + OpenTelemetry (OTLP/HTTP exporter). **Checker:** plain Python (`proof/`), 38 tests.

## 2. Data & security pipelines

### Authentication & access control
- **Tokens:** `PROOF_GITLAB_TOKEN` (can comment on and close issues; the admin capped expiry at Nov 25), `O11Y_API_KEY` from a SigNoz **service account** given the Viewer role, `DEPLOY_HOOK_URL`, all masked CI/CD variables.
- **Least privilege showed up as real limits:** with the hackathon's "Developer + AI" role, turning off auto-close via `PUT /projects/:id` returned **403**. It was only a backstop anyway, because "Proves #N" isn't a GitLab closing keyword. And the verdict flow's own `start_flow` call failed with "Insufficient permissions to create a new pipeline" under its service account. It said so on the issue, and the session started the Developer flow through the Flows API instead. That one human step is why the entry is **Supervised**, not Hands-off.
- **Flows can't see CI/CD variables** (GitLab docs), so the triage flow can't hold the Observability key. CI publishes recent production errors to the **package registry** and the flow reads them from there: secrets stay in CI, data goes to the agent.

### Data ingestion & flows
- **Event-driven at the edges, batch in the middle:** a *Work item created* trigger → triage flow writes the contract → a fix MR "Proves #N" → the MR pipeline (tests, `proof-contract` gate, SAST, secrets, dependency and container scanning) → merge → deploy (retag + Render hook, wait until the service reports the new build) → `proof-watch` polls production logs for the window → receipt → close, or keep open → CI calls the verdict flow via the Flows API → the Developer flow.
- **No traffic, no proof:** a window under `min_requests` is *inconclusive*, so the issue stays open and nothing is rolled back. `/healthz` was being counted as traffic until that was fixed.

### Privacy & compliance
- billsplit's data is synthetic (users simulated by `tools/traffic.py`). Logs go to GitLab Observability in the group's own tenant.
- **Gaming the proof is refused:** the gate fails a bug-fix MR that deletes the code reporting the failure instead of fixing it. That's the "silence the alarm" attack an agent could take.

## 3. Reliability & failure operations

### State management
- The `resource_group` serialises deploys, so a second merge waits instead of contaminating the first build's proof window. The registry tag is the durable "what's live" state, and rollback is just another retag.
- Every receipt names its log source, so a re-read later knows where its numbers came from.

### Error handling & fallbacks
- **GitLab Observability ingestion was down (HTTP 502)** for most of the build: 0 logs and 0 traces in 7 days, not even GitLab's own pipeline export. Fallback: billsplit serves its own recent lines at `GET /logs`, and the deploy job saves the old build's lines before switching, so before/after rates still work. The pipeline kept probing OTLP on every run. **Mid-run GitLab fixed ingestion (HTTP 200)**: the first receipt read billsplit's own lines, and the pipeline switched to Observability by itself for the second. A direct SigNoz query matched the proven receipt (build `f981855`: 962 requests, 0 `LedgerError`).
- **Roll back only what got worse:** a failed proof rolls back only when the new build fails at least as often *per request* as the one it replaced. The partial fix cut failures from 32% to 9%, so it stayed live while the next fix was made, instead of reintroducing the worse build.
- **The flow image had Python but no pip,** so the triage flow's first session died in setup. It was re-run with a mention, and the reader script uses the standard library only.

### Logging & observability
- OpenTelemetry logs and traces from billsplit to GitLab Observability; the checker queries them; receipts carry before/after/needed tables plus sample log lines.
- An `observability-check` job and per-run OTLP probes (HTTP and gRPC; gRPC still returned 464, unused).

## 4. Evaluation & optimisation metrics

### Performance benchmarking
- **The core claim is the demo:** a merge request that passed every test, scan and AI review was caught by production minutes after it shipped. 32% → 9% (not proven), then 66 → 0 failures on 875 requests (proven).
- **Local rehearsal first** (10-21): the partial fix was caught as not proven within seconds; the full fix was proven (5 errors before, 0 after, on 232 requests). 28 tests then; 38 after the real run.
- **Bugs the real run found** that tests hadn't: contracts written as a single string were parsed character by character; the evidence upload needed curl, which the job image lacked; SigNoz timestamps are strings; `/healthz` counted as traffic.
- There's no measured "time to detect a bad fix" baseline against a normal workflow. The honest comparison is qualitative: normally the issue would have closed on merge of !1.

### Cost & resource efficiency
- Free: the hackathon's 500 GitLab Credits a month for Duo, Render free tier, GitLab Observability (free in beta), synthetic traffic only during deploy and proof windows (to save Render hours).

### System constraints
- Proofs need traffic, and synthetic users stand in for real ones. "Proofs that wait for real user traffic" is listed as next.
- Contracts are log-line based. Latency and error-rate targets are future work.
- Render free instances sleep, hence the baseline-measuring wake-up in CI.
- Duo flows' permissions limited full autonomy, hence Supervised.

## What the history shows (real decisions)
- **10-21:** rules read. Path A, aiming at Hands-off plus Most Stages Covered. The Google Cloud +0.2 bonus was skipped (the no-GCP rule). Built and rehearsed locally the same day, in a private interim repo until GitLab onboarding was approved.
- **10-26, 17:05 IST:** Jannet had submitted the Devpost form, but **the GitLab project was still empty**. A check found it would fail stage one. The showcase `main` had GitLab's starter commit and refused force-push, so the session merged that commit (`389c664`) so a normal push would fast-forward. By 17:30 the first pipeline passed all 11 jobs.
- **10-26 evening:** flows into the AI Catalog, triggers, the 502 fallback, then the full real loop by 22:45 IST, video at 23:55, final submission 00:10 IST Oct 27.

## Weak spots to own before they ask
- One handoff needed a person (the verdict → Developer flow permission error). That's why it's Supervised.
- The first fix (!1) was written as a deliberate partial fix for the demo story. Triage, the gate, Duo Code Review, the proof and the verdict all ran for real on it.
- Built with Claude Code as the coding assistant. I ran the GitLab setup steps (tokens, Observability service account, Render, CI variables) and made the autonomy call.

## Sources
`README.md` and the 5 commits of `JannetEkka/proof-of-fix` (Oct 21–26: Oracle → Render move, GitLab merge); [DSProjects#18](https://github.com/JannetEkka/DSProjects/issues/18) comments 10-21 to 10-27 (rules, local build, empty-project catch, setup steps, flows and 502 fallback, the real run, Devpost text, video, final submission).
