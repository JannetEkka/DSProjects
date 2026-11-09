# Design brief: <entry name>

**Process (Jannet, 11-08):** every entry starts with a **discussion session** that ends with this brief, not with code. Jannet reads it, explains the architecture back in her own words, and signs it off. Then a **separate build session** starts from the build prompt in section 10. The goal is that Jannet understands everything we build, can prompt better, and can defend it in a judge interview. Check the idea against [../lessons.md](../lessons.md) before writing section 1.

Copy this file to `hackathons/<entry>/design.md` and fill it in during the discussion session. Write in plain language and explain any term on first use.

## 0. The hackathon, in one screen
- Link, deadline (IST), last day to register, team rules.
- What the rules force: required tech, deliverables (repo, video length, live URL, form fields), anything banned.
- How it's judged: each criterion and its weight, quoted from the rules.
- Money: confirm entering needs none of our own (no mainnet gas, no paid credits, no card); see [../cards.md](../cards.md).

## 1. The idea
- One sentence: who it's for and what changes for them.
- Why it's **not the obvious** use of the sponsor's tech (lessons 1).
- The other 2–3 ideas we considered, and why we didn't pick them.

## 2. The measured comparison (decide before building)
- The same task with and without our system: what we run, on what data, and which number we report (lessons 2).
- What a good result looks like, and what we'll say honestly if it isn't good.

## 3. What a judge sees in the first 10 seconds
- The one screen or moment that shows the result, sketched in words (lessons 3, 10).
- Six-word headline. The look that fits the subject.

## 4. Architecture
- The parts and how they connect, as a small diagram (boxes and arrows in text is fine).
- **Model judgment vs fixed rules:** which decisions the model makes, which the code makes, and why (lessons 4).
- If there are several agents: each role, what it reads, what it writes, and how they act on each other (lessons 7).
- Hosting, storage and services, each with why it was chosen and what it costs (free tier only).

## 5. The flow, step by step
- From the user's input to the output, one numbered step per line.
- Where evidence is checked, what blocks a "done" claim, and what happens on bad input (lessons 8, 9).

## 6. Decisions settled now
- Open questions in the rules or the data, and the answer we chose.
- Keys and accounts Jannet must create: where to click, what to name it, the exact environment-variable name.

## 7. Acceptance conditions
- A checklist the build must pass, each one testable. Include the UI (headline, first screen, accent colour, motion) and the demo, not only the code (lessons 5).

## 8. Demo plan
- Length limit from the rules; storyboard scene by scene; where the animations go; what's recorded live vs replayed.
- UI step: 2–3 directions on a Claude Design canvas before any UI code.

## 9. Jannet's check
- Questions Jannet answers in her own words before sign-off. For example: what does each part do; why is this a rule and not a model call; what's implemented vs only proposed; walk through one case end to end (lessons 11).
- Gaps found and how they were fixed.
- **Signed off:** Jannet, date.

## 10. The build prompt
- The exact first message for the build session: the architecture, the responsibilities (model vs rules), the acceptance conditions, and "keep the chat log raw from this message on". Written here so it can be reviewed before it's sent.
