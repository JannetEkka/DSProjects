# neatHack: prep

Window: **Oct 10, 00:00 IST → Oct 11, 23:59 IST** (48 h, from the Luma event data). Tracks are published **Oct 8**. Progress: [#28](https://github.com/JannetEkka/DSProjects/issues/28). Page: [luma.com/s5blr882](https://luma.com/s5blr882).

## What's known (read 2026-10-06)

- **Organiser:** [neatlogs](https://neatlogs.com), a tool that traces agent runs, detects failures, investigates why they happened and runs evals ("the fastest path from failure to fix"). The judges will be people who spend their days on broken agents.
- **Brief:** "Build an AI agent, ship something you're excited about." Up to $10K in prizes, plus engineering roles and internships.
- **Format:** online, solo or a team. Team members each register with the same team name; solo needs nothing extra.
- **Partners** give free credits and API access (names come with the tracks).
- **Not published yet:** tracks, judging, the submission format, and whether anything can be prepared in advance. Until the rules say otherwise, **no project code is written before Oct 10, 00:00 IST.** What's prepared here is ideas, accounts and tooling.
- **neatlogs free plan:** 100k spans a month (hard cap), 3 investigations, 5 detectors, 14-day retention. That covers a 48-hour build. Python SDK: `pip install neatlogs`.

## Three candidate ideas (matched to the tracks on Oct 8)

1. **Claimcheck: catch agents that say they did something they didn't, or the reverse.** It reads an agent's trace and compares what the agent *said* ("I've emailed Bob", "I didn't change any files") with what its tool calls *show*. Each mismatch is flagged with the spans as evidence: done but never claimed, claimed but never done, denied but done. A suggested fix is re-run against the failing case to confirm it holds. Wiretrap found the third kind in a Google codelab agent, so the failure is real and documented. It's a failure neatlogs' own examples don't name, which makes it a natural fit for their platform. **Default if the tracks are open-ended or about reliability, evals or observability.**
2. **Fixloop: from a failing trace to a fix that's proven.** It takes one failed run, turns it into a regression case, proposes a prompt or tool change, and keeps the change only if the failure is gone *and* the passing cases still pass. The same rule Wiretrap uses for approved fixes. **Pick if a track is about developer tools or fixing agents.**
3. **Rulebook: a hackathon-rules agent.** Paste event links and get each deadline in your own timezone, what's allowed before the window, a submission checklist, cost red flags (funded wallets, paid credits, KYC) and clashes between events. It's what this file was made by hand to do. **Pick if a track wants a consumer or productivity agent.**

Whichever is picked, the agent itself is instrumented with neatlogs, so its own traces are part of the demo.

## Build plan (Jannet away Oct 8–10; IonQ runs the same weekend)

| When (IST) | Claude | Jannet (minutes, phone OK) |
|---|---|---|
| Oct 8 | Read the tracks and rules; pick a track and idea; post the pick and the rules summary in #28 (scheduled check-in) | Night: reply "ok" or change the pick |
| Oct 9, night | — | Say **"go"** (the window opens at midnight). Check the free Gemini and neatlogs keys are in the environment (#28) |
| Oct 10 | Public repo; the core agent and detector on recorded traces; tests; neatlogs instrumentation | Night: read the "how it works" note |
| Oct 11 | UI or report; small labelled benchmark; demo video; submission text in #28 by **18:00 IST** | Night: watch the video, then submit before **23:59 IST**. The IonQ entry is due the same night (04:30 IST Oct 12) |

## Demo and submission

- Video recorded by Claude in a headless browser, narrated with a synthetic voice ([tools/demo-video](../tools/demo-video/)), under 3 minutes unless the rules say otherwise.
- Submission text, the AI-use disclosure and the links are drafted in #28 so you can paste them as they are.
- Free only: Gemini's free AI Studio tier, the neatlogs free plan and partner credits. No paid top-ups.
