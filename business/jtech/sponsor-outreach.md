# Paid work: writing to the companies whose tools we've built on

**Why these companies first:** each one has already seen a working project of ours built on its own product, so the email isn't cold. Developer-relations teams need example apps, starter templates, integrations and demos, and they often have more ideas than hands. Goal: one paid, fixed-price job (plan, part 2; Jannet works 3–4 days a week on paid work, decided 11-16).

**How to send:** reply on the email or chat thread we already have with each company where there is one (a reply on a known thread beats a new email to a stranger). Where we have no named person, Jannet looks for the hackathon's developer-relations contact in her inbox or the hackathon's Discord. Claude doesn't guess names or addresses.

**Wait for results first** where a judgement is still pending (marked ⏳), so the email doesn't land in the middle of judging.

## Who, what we built, and the one result to quote

| # | Company and product | Our project | The result to quote (from `projects/`) | Demo | Channel | When |
|---|---|---|---|---|---|---|
| 1 | FalkorDB (graph database, GraphRAG-SDK) | Lore | A real reviewer in Lore's top 3 on 90% of 300 FalkorDB PRs, vs 88% for "the repo's most frequent reviewer" | [lore-gh5y.onrender.com](https://lore-gh5y.onrender.com) | FalkorDB community Discord or the Graph Hacks organisers | Now (Graph Hacks results are out) |
| 2 | Qloo (taste API) | Footfall | A run makes ~18 Qloo calls and costs about $0.013 in model calls; all testing cost $0.45 against a $15 cap | [footfall-zz9v.onrender.com](https://footfall-zz9v.onrender.com) | The thread where Qloo issued our API key | Now (results out 11-08) |
| 3 | JigJoy (Mozaik runtime) | Spona | All 489 challenges answered in 5 min 48 s, up to 19 agent loops at once, about $1.52 of credit | [jannetekka.github.io/spona](https://jannetekka.github.io/spona/) | JigJoy's Discord; we're also entering their Nov 26–27 finance hackathon | Now |
| 4 | Nous Research (Hermes agent) | Lights Out | Merged into the Hermes plugin catalog by Nous on 11-12 | [github.com/JannetEkka/lights-out](https://github.com/JannetEkka/lights-out) | Nous Discord (each entry gets a thread after judging) | ⏳ after the result |
| 5 | Zetaris (data platform) | SQL Noir | Every verdict is a result-set comparison on live Zetaris data, with the rows that prove it; 50 tests | [video](https://youtu.be/oX4KvIMfIbE) | The organisers' email thread from the Demo Challenge | ⏳ after the Demo Challenge result |
| 6 | Perfect Corp (YouCam API) | Beauty Within | Calibrated YouCam's lip render to stay within ~2 L* of the person's own lip depth (the default made lips ~5 L* darker) | [beauty-within.pages.dev](https://beauty-within.pages.dev) | The YouCam API team's email (the redeem-code thread) | ⏳ winners ~Nov 24 |
| 7 | Nebius (Token Factory) | Footfall | Same build as Qloo's, on Nemotron through Token Factory | [footfall-zz9v.onrender.com](https://footfall-zz9v.onrender.com) | Builder Program email thread | ⏳ judging Dec 1–15 |
| 8 | GitLab (Duo Agent Platform) | Proof of Fix | A fix that passed tests and Duo Code Review was caught by production (32% → 9% of requests failing), then proven (0 of 875) | [GitLab project](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43596350/showcase) | Hackathon team | ⏳ results today |
| 9 | Anna (AI app store) | Lore for Anna | Their reviewers called the concept "fantastic" | store page after release | Dora on Discord (already talking) | Ask about paid app-building in the same chat |
| 10 | Monad, Solana | SMT Receipts, SMT World: Clock In | — | — | Their **ecosystem grant** programs, not developer relations | Later, with a separate note |

Left out on purpose: Meta and Amazon (too large for a cold contract email; Amazon's result is still pending), Google (no live project after the GCP move).

## The email (template)

Plain text, under 200 words. Fill the brackets from the table; keep the one measured result.

> **Subject:** Paid build work on [product]
>
> Hi [name],
>
> I'm Jannet. In [month] I built [project] on [product] for [hackathon]: [one line on what it does]. [The result to quote]. Demo: [link]. Code: [link].
>
> I'm now taking paid build work three to four days a week, and I'd like to do more with [product]. For your team that could be a reference app or starter template, an integration with a tool your users ask about, or a working demo for a sales call. I write the README and tests too, and I say plainly what the numbers do and don't show.
>
> If there's an example or integration on your list that nobody has had time for, I'd be glad to quote a fixed price for it. A 20-minute call works, or just reply with the one you'd want first.
>
> Jannet Ekka
> [portfolio link]

## Two filled in

**FalkorDB**

> **Subject:** Paid build work on FalkorDB
>
> Hi [name],
>
> I'm Jannet. In October I built Lore on FalkorDB for Graph Hacks: it reads a project's GitHub history into a graph and answers "who knows this part of the code?", citing a PR for every claim. On 300 of your own merged PRs, a real reviewer was in Lore's top 3 picks 90% of the time, against 88% for "the repo's most frequent reviewer". Demo: https://lore-gh5y.onrender.com. Code: https://github.com/JannetEkka/lore.
>
> I'm now taking paid build work three to four days a week, and I'd like to do more with FalkorDB and GraphRAG-SDK. For your team that could be a reference app or starter template, an integration your users ask about, or a working demo for a sales call. I write the README and tests too, and I say plainly what the numbers do and don't show.
>
> If there's an example or integration on your list that nobody has had time for, I'd be glad to quote a fixed price for it. A 20-minute call works, or just reply with the one you'd want first.
>
> Jannet Ekka
> [portfolio link]

**Qloo**

> **Subject:** Paid build work on the Qloo API
>
> Hi [name],
>
> I'm Jannet. In October I built Footfall on Qloo for your Agentic Hackathon: a small café gives its address and what it sells, and an agent asks Qloo what people within a walk of the door like, then suggests a playlist, things to stock and one weekend event. A run makes about 18 Qloo calls and costs about $0.013 in model calls. Demo: https://footfall-zz9v.onrender.com. Code: https://github.com/JannetEkka/footfall.
>
> I'm now taking paid build work three to four days a week, and I'd like to do more with Qloo. For your team that could be a reference app or starter template, an integration your users ask about, or a working demo for a sales call. I write the README and tests too, and I say plainly what the numbers do and don't show.
>
> If there's an example or integration on your list that nobody has had time for, I'd be glad to quote a fixed price for it. A 20-minute call works, or just reply with the one you'd want first.
>
> Jannet Ekka
> [portfolio link]

## Before the first send (Jannet)

- **Price:** decide a day rate or a fixed price per job before the first call, so the answer is ready. We have no measured market rate for this work; one comparison site lists $40–$100 an hour as the usual range for freelance AI engineers ([Second Talent](https://www.secondtalent.com/resources/7-best-freelance-platforms-ai-developers/)), which is a vendor's listing, not a quote.
- **Getting paid from abroad:** the CA question from the plan (invoice as an individual, how foreign payments are received and reported).
- **Portfolio link:** use the live portfolio until the company site exists.

## Send log

| Date | Company | Channel | Reply? | Call? | Job offered? | Notes |
|---|---|---|---|---|---|---|
