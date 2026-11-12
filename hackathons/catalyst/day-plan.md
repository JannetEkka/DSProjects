# Catalyst: Solo AI Hackathon, plan for Sunday Nov 15

**Event** (Unstop's own data, 11-13): free, online, **solo**, open to all. Run by Makers Need More (MnM), with Hack2skill ("PromptWars × Catalyst"). ₹15,000 for "Winners" (the split isn't stated); finalists also get a chance to work with the MnM core team. 3,021 registered by 11-13. Listing: https://unstop.com/hackathons/catalyst-solo-ai-hackathon-makers-need-more-mnm-1771798 · Telegram: t.me/catalyst_mnm · tracking issue: see `hackathons/november-2026.md` row #10.

| IST | What happens |
|---|---|
| 09:00–09:30 | Opening and **challenge reveal** |
| 09:30–16:30 | Build |
| 16:30–17:00 | Submission window |
| 18:00–19:30 | Finale (if shortlisted) |
| 19:30–20:00 | Winners and closing |

The problem is unknown until 09:00, so **nothing is built before then**. This plan fixes the process and the default stack, so no time goes on those choices on the day.

## Done before Sunday (Jannet)
- [x] Registered on Unstop, confirmed with MnM, verified on Hack2skill (11-13)
- [x] Joined the Telegram channel (11-13)
- [x] Gemini key from AI Studio in the environment as `GEMINI_API_KEY_CATALYST` (11-13). It reaches sessions started after it was added, so Sunday's session will have it.
- [ ] Adaption builder credits ($500, "pending within 24h" on the confirmation page): note whether claiming them asks for a card. If it does, record it in `cards.md` first, or skip them.
- [ ] NEAR submitted by Saturday evening (it closes Sun 05:29), then sleep.

## Sunday, step by step
1. **09:00** Read the challenge on Telegram/Unstop. Open a **new** Claude session in this repo and paste the first prompt below with the full challenge text.
2. **09:30–10:00 Discuss (30 min, hard stop).** The session proposes 2 ideas checked against `hackathons/lessons.md`: a quick web check for the same idea (lesson 0), a problem people recognise (1), a with-vs-without number we can measure today (2), a result a judge sees in 10 seconds (3). Jannet picks one, then the session explains the architecture in 5 bullets and Jannet says it back.
3. **10:00** Jannet creates an empty **public** GitHub repo for it and gives the session the name.
4. **10:00–12:30 Build the core path end to end** (input → model → checked output), then **deploy by 12:30**, even if rough.
5. **12:30–14:30 Make it good:** the measured comparison, error handling, then the first screen (headline of six words or fewer, the product visible immediately, one accent colour; lesson 10).
6. **14:30–15:30 Demo video** with `hackathons/tools/demo-video` (recorded in the cloud, narrated), README with the impact sentence and the number, and the write-up text for Unstop.
7. **15:30–16:15 Buffer.** Things break here; leave room.
8. **16:30 Submit** at the start of the window, not at 16:59.
9. **18:00 Finale (if shortlisted):** Jannet presents. Rehearse a 3-minute walkthrough while waiting: the problem, a live run, the number, what's implemented vs planned (lesson 11).

## Default stack (change it only if the challenge needs something else)
- One web page (HTML/CSS/JS, no build step) and, only if needed, a small Python FastAPI backend.
- Gemini through `GEMINI_API_KEY_CATALYST` (free tier). No paid APIs, no card.
- Hosting: GitHub Pages for a static page, Render's free plan if there's a backend. Deploy early, because Render's first deploy can take a few minutes.
- Every number on the page comes from a real run; no invented baselines (the impact rule in `.claude/CLAUDE.md`).

## First prompt for Sunday's session (paste at 09:00)

> Catalyst Solo AI Hackathon is live. The challenge is below. Read `hackathons/catalyst/day-plan.md` and `hackathons/lessons.md` first and follow the plan's timeline: discuss for 30 minutes (2 ideas, the web check, the measured comparison, what a judge sees first), explain the chosen architecture in 5 bullets until I can say it back, then build. Submission opens at 16:30 IST. Use `GEMINI_API_KEY_CATALYST`. Free tiers only. Tell me exactly when you need me (repo name, deploy clicks, the video check).
>
> THE CHALLENGE: <paste the full text here>
