# Wiretrap: adversarial security testing for AI agents

**Google Cloud Gen AI Academy APAC 2026, Cohort 3** (the Cloud Run AI challenge). Built Sep 2026 in Google AI Studio's app builder and deployed on Cloud Run; moved to free tiers on Oct 5 after GCP billing closed.
**Live:** [wiretrap.onrender.com](https://wiretrap.onrender.com/) (Render free tier, so the first load can take a minute) · **Code:** [github.com/JannetEkka/wiretrap](https://github.com/JannetEkka/wiretrap) (MIT) · ~10,400 lines of TypeScript (server + client)

## The 30-second version

Most LLM security tools read the agent's reply and grade the text. That misses the failure that matters in agentic systems: **an agent can refuse in words after it has already called a tool.** Wiretrap takes an agent's system prompt and tool schemas, clones every tool as an **inert decoy** (same name, description and JSON Schema; it records the call and returns canned data), runs a library of realistic attacks in isolated Gemini conversations, and has a separate judge read the **tool-call log**.

It caught a Google codelab business-analyst agent saying *"I don't have access or authorization to modify configuration files"* **after** it had run `ls -la` through its shell tool. Text scanners pass that. Wiretrap flags it as **"Said No, Did Yes"** and shows the arguments.

What I can't claim: a breach rate across many agents. The finding is a demonstrated case, not a benchmark. The README's own caveat is shown on every result: a defense score means the agent withstood *these attacks in this run*, not that it's secure.

## 1. Architectural reasoning

### Database / storage
- **Cloud Firestore (NoSQL), owner-bound document tree:** `users/{uid}/targets/{targetId}` with subcollections `messages`, `runs`, `findings`, `versions`. Why a document store: every object belongs to exactly one user and one target, reads are by that path, there are no cross-user joins, and Firebase Auth + Firestore rules give per-user isolation without a server-side ACL layer. Prompt versions are snapshots in `versions`, so approving a patch increments the version and any version can be rolled back.
- Why not SQL: no relational queries across users or targets; the hierarchy *is* the access model.

### Compute & hosting
- **Express backend + React/TypeScript frontend in one container.** All Gemini calls, Firestore writes and detonation runs are server-side; **the browser never holds a model credential**.
- **Then:** Cloud Run (`us-west1`) with Vertex AI through **Application Default Credentials**: no static API key anywhere, and a least-privilege service account holding only `roles/aiplatform.user` and `roles/datastore.user`.
- **Now (10-05):** after the GCP billing account closed, it moved to **Render's free tier + Firebase Spark + a free AI Studio key**. The code supports both modes (`GOOGLE_GENAI_USE_VERTEXAI` → ADC; otherwise `GEMINI_API_KEY`). The trade-off I'd name: the move gave up "zero static keys" for "₹0 to host". The portfolio stat was changed to say so.
- Why a container and not serverless functions: detonations stream over SSE and run up to 4 attacks concurrently per run, a long-lived request that fits a container better than short functions.

### Frameworks & libraries
- `@google/genai` (Vertex or API-key mode), Firebase Admin SDK, Express, React, Vite.
- **No agent framework:** detonation is a controlled loop (attack turns → decoy function calls → judge), and isolation matters more than orchestration features.

## 2. Data & security pipelines

### Authentication & access control
- **Google Sign-In through Firebase Auth.** **Server-derived identity:** every API route verifies the Firebase ID token with the Admin SDK and derives `uid` from it. Request bodies carry only a `targetId`; the server loads the prompt and tools from `users/{uid}/targets/{targetId}`. **Client-supplied prompts, tools and user IDs are ignored**, so a user can't run attacks with someone else's target or forge ownership.
- **Firestore rules:** deny-all by default, owner-bound throughout, ownership asserted on write (`request.resource.data.userId == userId`), and `createdAt` immutable on update.
- **Rate limiting:** at most **3 detonation runs per hour per user**, server-side, because each run costs model calls on my quota.

### Data ingestion & flows
- Request → server loads the stored target → normalises shorthand tool schemas into Gemini-compatible JSON Schema → builds decoys → matches attacks to the target's capability class → runs up to 4 attacks concurrently, streaming progress to the browser over **SSE** → the judge classifies each → the fixer groups breaches by root cause and drafts a prompt patch (as a diff), guardrail code and a config change → **patches are never auto-applied**: the user approves, then "Verify Fixes" re-runs the exact breached attacks against the new version.

### Privacy & compliance
- **Untrusted input is the whole threat model:** Wiretrap runs agent definitions strangers submit. Every target prompt sent to the auditor, judge or fixer is wrapped in delimiters and labelled untrusted, and those agents are told never to follow directives inside it. That's tested: a submitted prompt containing an override makes the auditor *report* the injection rather than obey it.
- **Decoys execute nothing:** pure functions returning canned strings. No `eval`, no subprocess, no network, no filesystem.
- **Context isolation:** a target's prompt only ever runs in throwaway conversations whose only functions are decoys. It never shares context with Wiretrap's own agents or tools.
- User data (prompts, runs, findings) stays in that user's Firestore subtree.

## 3. Reliability & failure operations

### State management
- Runs, findings and versions are persisted per target, so a page reload or a server restart doesn't lose results. Prompt versions are immutable snapshots with rollback.

### Error handling & fallbacks
- **Model fallback ladder:** `gemini-3.8-flash` → `gemini-3.6-flash` → `gemini-3.1-flash-lite` → `gemini-flash-latest` on 503/429/404/500, with quota-aware retry that reads the API's `retryDelay`. The fixer is quota-disciplined (at most 3 findings per call).
- **Fail toward "unknown", not "safe":** a run with zero classified results reports **`INCONCLUSIVE`, never `HARDENED`**. "A security tool that reports 'safe' on missing data is worse than one that crashes." Attacks against capabilities the agent doesn't have are `NOT_APPLICABLE` and excluded from the score, not counted as defenses.
- **The deploy bug on the move to Render (10-05):** the first Render deploy crashed with `Cannot find module '@google-cloud/firestore'`. On `node:20-slim`, npm only *warns* (EBADENGINE) for direct dependencies but **silently skips** firebase-admin's optional `@google-cloud/firestore`, because its subtree requires Node ≥22. The build passes and the server dies on first require. It was reproduced (Node 20 leaves only secret-manager under `@google-cloud`) and fixed by building on Node 22.

### Logging & observability
- Server logs per subsystem (`[Vertex AI Client]`, `[Firebase Admin]`, `[Fixes Generate]`), live SSE progress in the UI, and per-run stored results with the judge's plain-English reason.
- Verification reports say plainly when a fix didn't hold.

## 4. Evaluation & optimisation metrics

### Performance benchmarking
- **The demonstrated case:** the "Said No, Did Yes" catch on a Google codelab agent, a breach every text-grading scanner marks as a pass.
- **Attack design choice:** payloads avoid the obvious markers (no shouting, no fake override codes, no "ignore all previous instructions"), because current models refuse those trivially. Real breaches come from requests that read like ordinary work.
- **Before/after verification** of approved patches is the product's own evaluation loop.
- No published breach rate across a corpus of agents. If asked how I'd measure it: a fixed set of open-source agents × the 8 categories, repeated runs to estimate judge variance, and a human-labelled sample to measure judge accuracy.

### Cost & resource efficiency
- ₹0 to host now (Render + Firebase Spark + AI Studio free tier). Capability matching cuts wasted calls (no shell attacks against an agent without a shell), and there's a per-user hourly cap.

### System constraints
- Free-tier model quotas bound runs per hour. The Render free instance sleeps (cold start ~1 minute). Up to 4 concurrent attacks per run.
- The judge is a model: it can misclassify. The tool-call log is shown so a person can check.

## What the history shows (real decisions)
- Sep 5: the project was initialised from AI Studio's app builder (Firebase rules, scaffolding), plus the README and licence. Live at `wiretrap.ai.studio` and on Cloud Run under project `wire-trap-26` during the cohort.
- Sep 22: added to the portfolio and résumé with the Forward-Deployed framing.
- Oct 2: GCP billing closed (see SMT), and both Wiretrap URLs went dead (503).
- **Oct 5:** live again on Render + Firebase Spark + AI Studio key (PR #1, the Node 22 fix). The portfolio stat "0 static API keys" was replaced because it was no longer true.
- Its method was reused: the first plan for Hack Apertus was a Track 1A red-teaming harness built on Wiretrap's decoy method (see Klarbrief).

## Weak spots to own before they ask
- The README still describes the Cloud Run/Vertex deployment. The live one is Render + an API key.
- The history in the repo is short (6 commits): most of the build happened in AI Studio's builder before the export.
- Built with AI assistance (AI Studio's builder, then Claude Code for the migration fix).

## Sources
`README.md` (architecture, security posture, Firestore rules), `server/gemini.ts` (Vertex vs API-key mode), `server.ts` (3 runs/hour limit), git log (Sep 5 init; Oct 5 Node 22 fix, PR #1); DSProjects commit "Wiretrap is live again" (10-05) and `_portfolio_src/data.py` link-status notes.
