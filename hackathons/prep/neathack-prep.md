# neatHack: prep

Coding starts at the **Oct 10, 12:30 IST** kickoff. Submissions are open **Oct 12, 19:00–23:55 IST** only, as a quote post on X. Winners are announced Oct 16. Progress: [#28](https://github.com/JannetEkka/DSProjects/issues/28). Official page: [neatlogs.com/hackathon/1](https://neatlogs.com/hackathon/1). Luma's times are out of date.

## The rules (published 2026-10-08)

- **One track: "Build an Agent That Works (Literally)."** An agent, or a team of agents, that completes a substantial task from start to finish. The focus areas are planning, tool use, state, context, execution, recovery, verification and iteration.
- **Before the start:** "You can plan your idea in advance, but all code must be written between the start on October 10 and the deadline on October 12." Judges check that commits are dated inside the window.
- **Required tools:** both **neatlogs** and **[Entire](https://entire.io)**, each with a clear role in the agent or in how it's built. The demo has to cover both. **cfo.ai** (pricing, costs and runway for the agent as a product) earns bonus points.
- **Judging:**
  - the agent 30%
  - use of neatlogs + Entire 25%
  - demo video 20%
  - building in public 15% (posts tagged #neatHack during the event)
  - usefulness and originality 10%
- **Evidence in the repo:**
  - before/after runs (two neatlogs traces with the numbers compared)
  - neatlogs trace links
  - Entire checkpoints or entire-graph output
  - a run where an action failed and the agent recovered
  - the #neatHack posts
- **Submission:** a quote post on X of the official neatlogs submission post, with team, name, project, public repo and demo link. The video is 3 minutes or less and covers the architecture, implementation, runtime, reasoning and result for each of the two tools.
- **Prizes:** $2,000 / $1,000 / $500 cash, plus $5K / $3K / $1K in Dodo Payments credits; a $500 Community Winner prize; 3 months of neatlogs PRO for every winner. Crustdata gives 5,000 credits to everyone. The AWS credits need an AWS account, so we skip them.

## Entire, and why the build gets its own session

Entire is an open-source CLI (MIT). It turns every commit a coding agent makes into a "checkpoint" that holds the prompt, transcript and tool calls. The checkpoint is stored in the repo as a git ref, and Claude Code is supported. In a public repo those transcripts are public. So the code is written in a **fresh session holding only project context**, and the first checkpoint is inspected before anything is pushed. The core CLI works locally. An Entire account is only needed for hosted features (search, mirrors).

## The entry: Fixloop

**An agent that fixes another agent's failed run, and proves the fix with neatlogs traces.**

1. It reads the failing run from neatlogs.
2. It reproduces the failure as a test case.
3. It changes the target agent (prompt or tool handling).
4. It re-runs the failing case and the cases that already passed.
5. It proposes the change as a PR only when the new trace shows the failure gone and nothing else broken. A failed attempt is recorded with its reason, and the loop tries again.

**The failure it hunts:** agents that say they did something their tool calls show they didn't, or the reverse. "I've sent the email" with no send call in the trace. "I didn't change anything" after a write. Wiretrap documented the second kind in a real agent.

**How it scores:**

| Criterion | Where it comes from |
|---|---|
| The agent (30%) | A full task: find, reproduce, fix, verify, propose. The example tasks "fix a GitHub issue" and "watch a running system" |
| neatlogs + Entire (25%) | neatlogs is Fixloop's input and its proof. Entire records how it was built, and `entire why` explains lines in the demo |
| Demo (20%) | One failure, start to finish, with the before and after traces side by side |
| Building in public (15%) | 2–3 short X posts from Jannet tagged #neatHack, drafted in #28 |
| Usefulness (10%) | Every team shipping agents has this failure, and a fix that's proven beats one that's only plausible |

**Stack (free only):** Python; Gemini on the free AI Studio tier; the neatlogs free plan (100k spans a month); the Entire CLI; a small target agent with tools that are dead copies (they record the call and return fake data). **To check at kickoff:** reading traces back from neatlogs (MCP or API) on the free plan. If that isn't possible, Fixloop takes the trace from the SDK hook while still sending everything to neatlogs.

**Runner-up:** Rulebook, a research agent with sources (another of their example tasks), if Fixloop is vetoed.

## Plan (IST)

| When | Claude | Jannet (minutes, phone OK) |
|---|---|---|
| Oct 8, night | — | Web check-in ([link](https://neatlogs.com/hackathon/check-in)), join the [Discord](https://neatlogs.com/discord), reply "ok" to Fixloop in #28 |
| Oct 10, before 12:30 | — | Say **"go"** in S5 |
| Oct 10, 12:30 → night | Fresh build session; public repo; neatlogs tracing and Entire checkpoints checked; target agent and its failing cases; first X post drafted | Night: post the first #neatHack update |
| Oct 11 | Fixloop's full loop; recovery run; before/after evidence; second post drafted | Night: post it; read the "how it works" note |
| Oct 12 | Demo video, README evidence, cfo.ai model, submission text in #28 by 17:00 | 19:00–23:55: watch the video, post the submission quote on X. The Solana entry is due 17:29 the same day |

Video: recorded by Claude in a headless browser, narrated with a synthetic voice ([tools/demo-video](../tools/demo-video/)), 3 minutes or less.
