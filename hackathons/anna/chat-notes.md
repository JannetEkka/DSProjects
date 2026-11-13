# Chat with Anna (Dora): talking points

For the Discord chat Anna's developer team asked for in their App Review email of Oct 28 (found in spam on 11-13). They asked three things: how I plan to update and improve the app after launch, my ideas for growing its monthly active users, and anything I need from them. Tracking: [DSProjects#46](https://github.com/JannetEkka/DSProjects/issues/46). Fix: [anna-lore PR #2](https://github.com/JannetEkka/anna-lore/pull/2).

Everything here comes from what Lore does today and from our own test runs. There are no user numbers yet, because the app isn't live, so none are claimed.

## 1. What I did with their review (say this first)

Their point: when GitHub's rate limit leaves the data incomplete, a small red note at the top was the only sign, while Knowledge risk said "only @eps1lon knows it well" as fact.

- **They were right, and I could reproduce it.** On my test repo (FalkorDB/falkordb-py), a load stopped by the rate limit after 14 of 34 merged PRs lists two areas as known by one person. With 30 read, it lists none. So partial data doesn't just blur the picture; it can invent a bus-factor problem. This is now a test in the repo.
- **v0.1.1 does what they suggested:** a "Based on partial data" banner inside every result view (Experts, Knowledge risk, Triage, Ask answers), with the numbers ("files read for 14 of 34 merged PRs") and when GitHub's limit resets. Every Experts and Knowledge-risk row has a "partial data" badge and the lists have a watermark. Knowledge risk says "Based on fetched data, only X knows it well".
- **Two things I added beyond the review:**
  - The model is told the data is partial, and its answer is checked. If it still writes "only X knows" as fact, Lore quotes that sentence in a "Read with care" note above the answer.
  - Without a GitHub token Lore reads files for the 30 most recent merged PRs, to fit GitHub's 60 calls an hour. On a big repo that is partial data too, even when the limit never hits. v0.1.0 said this in one grey line; v0.1.1 treats it exactly like the rate-limit case.
- **Tested:** 18 engine tests and 24 browser checks with a simulated rate-limited load. Not yet tested: a real rate-limited load of `facebook/react` inside Anna, which needs the published build. I'll run that one myself once v0.1.1 is up.
- **Apology for the delay:** the review email went to spam, so I saw it 16 days late.

## 2. How I plan to update and improve Lore after launch

In order. Each one comes from a limit the app has today.

1. **Read more of each repo.** The biggest weakness is coverage: 30 merged PRs' files per repo without a token. With a GitHub token the limit is 5,000 calls an hour instead of 60, and Lore's code already has a larger budget for that case (files for 200 merged PRs, plus review approvals, which the no-token run can't read at all). What's missing is a safe way for a user to connect GitHub inside an Anna app. That is my first ask in section 4.
2. **Continue a load that was cut short.** Today a rate-limited load starts over on Refresh. It should keep what it has and fetch only the rest, so the second try finishes the job.
3. **Show confidence per area, not only per page.** The banner says how much of the repo was read. The next step is per area: "3 of this area's PRs read" next to each ranking, so a thin area looks thin.
4. **Measure how often Lore is right.** The original Lore has a backtest (hide a PR, ask who should review it, compare with who did). Its honest result: Lore's top pick doesn't beat a simple baseline overall and only pulls ahead on areas with enough history. I want that backtest in the Anna version, and the result shown in the app.
5. **Make results leave the app.** Copy the Experts list as Markdown, and draft a CODEOWNERS file from it. Today the only thing a user can copy is the triage draft.
6. **Housekeeping:** move the manifest to schema 4 (the CLI warns that `ui.host_api` fields are retired).

What I won't promise: private repos. Lore reads public data only, and that is part of why it is safe to review. Private repos would need the token work first and a fresh look at privacy.

## 3. Ideas for growing monthly active users

The first target is the program's first tier: 200 qualified users in a calendar month. I have no usage data yet, so these are plans to test, not forecasts.

**Who Lore is for** (each maps to a tab that exists):
- **New contributors** to an open-source project: "I'm new, where should I start?" and who to ask (Ask, Experts).
- **Maintainers** with an issue backlog: related past work, who knows the area, a drafted first reply (Triage).
- **People choosing a dependency** or leading a team: which areas rest on few people (Knowledge risk, now with honest wording).

**How they'd find it:**
- **From Anna's chat.** Lore's manifest already tells Anna's assistant to open Lore when a user mentions a GitHub repo or asks who knows a codebase. This is the cheapest path because the user is already signed in to Anna. I'd like to know from Anna how often this trigger fires (ask below).
- **Worked examples on well-known repos.** Short posts that show one real question and Lore's answer with its PR links, on repos people already care about (flask, httpx, typer are the app's built-in examples). Posted where contributors look for a way in: dev.to, Reddit's open-source and language communities, LinkedIn, X. Each post states how much of the repo Lore read.
- **Maintainers as a channel.** A maintainer who finds Triage useful can point newcomers to Lore from CONTRIBUTING.md ("see who knows this part of the code"). One maintainer brings their contributors. This needs a link that opens Lore on a given repo (ask below).
- **Anna's own community:** the forum, the Discord, and the Founding Builder Challenge on Unstop.

**Why they'd come back:**
- A repo loaded before opens from storage, and the start page lists recent repos. That exists today.
- A "what changed since you last looked" view for a repo the user follows. This is new work and the main retention idea.

**How I'll know what works:** I can't see any usage today. With per-app numbers from Anna (ask below) I'd compare which entry point brings users who finish a run.

## 4. What I need from Anna

1. **A way for users to connect GitHub inside an app** (OAuth or a per-user secret the app can use without seeing it). This takes Lore from 60 to 5,000 GitHub calls an hour per user and removes most partial-data cases at the source. If that exists already, a pointer to the docs.
2. **Review feedback where builders will see it.** The review email went to spam and cost 16 days. A status and the reviewer's notes in My Apps, or a Discord ping, would prevent that.
3. **A link that opens an app with a payload**, for example the store link plus `?repo=pallets/flask`, so a post or a CONTRIBUTING file can send someone straight to a result. `open_app_view` does this from chat; I don't know of a public URL that does.
4. **Per-app numbers for builders:** qualified users this month, runs, failed runs, and how often the assistant opened the app from chat.
5. **What exactly counts as a "real run" for Lore:** loading a repo, or a model call (Ask or Triage)? Experts and Knowledge risk need no model call.
6. **Re-review timing** for v0.1.1, and whether a version bump after approval needs a full review each time.
7. **If they feature apps:** a slot for Lore under developer tools once it is live.

## 5. Questions to ask them

- When they loaded `facebook/react`, how far did it get before the limit hit? (It tells me whether their network shares GitHub's 60-call allowance with other users, which would make rate limits much more common inside Anna than in my tests.)
- Do Anna apps run their GitHub calls from the user's browser IP in every client, or through a shared address anywhere?
- Is there a server-side fetch or cache planned that apps could use for public APIs?

## 6. Weak spots to own if they come up

- **Coverage is thin on big repos** until users can connect GitHub: 30 merged PRs' files, and 300 PRs listed at most.
- **The ranking is a heuristic** (merged PR 1.0, review 0.6, comment 0.2, halving every 180 days). It finds who worked on an area, which is not always who understands it best.
- **Built with Claude Code as the coding assistant.** I chose the problem, the graph model, the scoring rule and the product, and I review the code, tests and results.
- **No users yet.** Everything about growth is a plan.

## Discord message (send after v0.1.1 is resubmitted)

> Hi Dora, I'm Jannet, the builder of Lore (@jannetekka/lore). Thank you for the review, and sorry for the slow reply: your Oct 28 email landed in spam and I only found it on Nov 13.
>
> **What I changed (v0.1.1, resubmitted for review):**
> You were right about partial data, and I could reproduce it. On my test repo, a load cut short by GitHub's rate limit after 14 of 34 merged PRs showed two areas as "only one person knows it"; with 30 read, it showed none. So I did what you suggested, and a bit more:
> • A "Based on partial data" banner inside every result view (Experts, Knowledge risk, Triage, Ask), with the numbers and when GitHub's limit resets
> • A "partial data" badge on every Experts and Knowledge-risk row, plus a watermark on the lists
> • Wording: "Based on fetched data, only X knows it well"
> • The AI is told the data is partial, and its answer is checked: if it still states "only X knows" as fact, Lore flags that sentence
> • Lore's own 30-PR reading cap (to fit GitHub's 60 calls an hour) is now shown as partial data too
> Before/after screenshots: https://github.com/JannetEkka/anna-lore/pull/2
>
> **After launch:** my first priority is reading more of each repo, since coverage is Lore's real limit today. Then: resuming a load that was cut short, showing confidence per area, a backtest that shows how often Lore's picks are right, and exporting results (Markdown, a CODEOWNERS draft).
>
> **Growing MAU:** Lore serves three groups: new open-source contributors, maintainers triaging issues, and people checking how many people a dependency rests on. I plan to reach them through Anna's chat (Lore already opens when someone mentions a GitHub repo), worked examples on well-known repos posted in developer communities, and maintainers linking Lore from their CONTRIBUTING files. For repeat use I want a "what changed since you last looked" view.
>
> **What would help from you:**
> 1. A way for users to connect GitHub inside an app (OAuth or a per-user secret). It lifts the limit from 60 to 5,000 calls an hour and removes most partial data at the source
> 2. A link that opens an app with a payload (like ?repo=owner/name) so posts can lead straight to a result
> 3. Per-app numbers for builders: qualified users, runs, and how often chat opens the app
> 4. Review feedback visible in My Apps or on Discord, so it can't get lost in spam again
>
> Happy to go through any of this whenever suits you.
