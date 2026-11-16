# JTech: from projects to paying users

**Status: draft for discussion. Nothing in it is decided until Jannet signs it off.** Written 2026-11-16 by a Claude discussion session, from the repo (`projects/`, `hackathons/`, the open `hackathon` issues, SMT's `docs/business/`) and web searches the same day. Nothing has been bought, registered or signed, and no card has been used.

How to use it: we go through it one part at a time, in order (1 → 6). For each part Jannet says back the decision in her own words, and we mark it **Decided (Jannet, date)**. Anything still open is in [Waiting on Jannet](#waiting-on-jannet) at the end.

## The short version

- **The gap is users and money, not code.** Across the write-ups in `projects/`, the products that say anything about users say "no users yet" (Footfall, Chithi, Spona, Recourse, SMT World: Clock In) or have a handful of early testers (SMT World's builder night). Building a 30th project won't change that. Talking to 30 possible users will.
- **Take two things to market, not twenty:** **Lore** (who knows what in a GitHub project), sold to open-source maintainers and small software teams abroad, and **SMT as a business-to-business pilot with an exchange** that already knows us (WEEX, Bitunix). Reasons in part 1.
- **Don't incorporate yet.** Selling, invoicing a first pilot from abroad and entering the Buildathon don't need a company. Incorporate an Indian Private Limited company when one of four triggers happens (part 3). That saves the yearly audit and filing costs until there's something to pay for them.
- **"JTech Solutions" is a weak legal and web name:** every obvious domain is taken, Indian companies with near-identical names exist, and there are live US trademarks for "JTECH" and "JT TECH". Pick a distinctive name before anything is registered (part 3).
- **One website, free:** this repo's portfolio generator already holds every project; a company page built from it goes on Cloudflare Pages or GitHub Pages for ₹0. Only the domain costs money (part 4).
- **Funding:** non-dilutive first (Buildathon cash, Anna grants, hackathon prizes, cloud credits that don't need a card). Angels and pre-seed only after we can show paying pilots or steady usage. No one will fund a list of projects (part 5).
- **Hiring:** no hire until revenue or a grant pays for it. The first paid help is a freelance designer for one fixed job (part 6).

---

## 1. Inventory: what's built and what to sell first

### What we have

From the write-ups in `projects/` (measured results are the ones those files record; "users" means people outside us).

| Product | Readiness | Who it's for | Evidence of demand | Verdict |
|---|---|---|---|---|
| **Lore** (+ Lore for Anna) | Live on Render free tier; Anna port v0.1.1 in App Review (11-13). Backtest: a real reviewer in the top 3 **90%** of the time vs 88% for the frequent-reviewer baseline, on 300 FalkorDB PRs | Open-source maintainers, new contributors, team leads choosing dependencies | Anna's developer team called the concept "fantastic" and the Experts and Knowledge-risk features "incredibly useful" ([#46](https://github.com/JannetEkka/DSProjects/issues/46)) and asked to talk about growth. A paid competitor (CodeScene) sells knowledge-risk features, which says companies pay for this kind of answer | **Take to market (first)** |
| **SMT** (+ SMT World) | Runs 24/7 on WEEX's simulated account on ₹0 infrastructure; 3,152 tests; patent pending (IN 202631090789). **Not profitable**: SMT Receipts shows both graded records net negative after fees (11-01) | Crypto exchanges (business customer); their retail traders (end users) | WEEX gave a $10K simulated account, an affiliate manager and an API change after our feedback; a Bitunix partnerships contact approached us; 16VC asked for follow-up details on 10-19; about 10 students joined as early users after a builder night (all from `16VC_APPLICATION.md`) | **Take to market (second), as a pilot with an exchange, not to retail** |
| Lights Out (Hermes plugin) | Merged into the Hermes plugin catalog by Nous (11-12, [#93](https://github.com/JannetEkka/DSProjects/issues/93)) | Hermes users who let the agent touch a cloud account | Accepted into the catalog; no install numbers yet | Keep listed, watch installs; not a business on its own |
| Chithi / Klarbrief | Chithi live (Render); Klarbrief runs offline. Chithi: 114 dates and amounts shown, 0 wrong, on synthetic letters | People who can't read official letters (India: Bengali/Hindi; Switzerland: DE/FR/IT) | None from users. Not a finalist at Meta (11-09); not placed at Hack Apertus | Park. The space is crowded (below) and consumers rarely pay for it |
| Wiretrap | Live (Render) | Teams shipping AI agents | One demonstrated case ("Said No, Did Yes"); no users | Park. Crowded, and big security vendors have been buying the leaders |
| Proof of Fix | GitLab project, public | Engineering teams | Hackathon result pending (~11-16) | Park; revisit if it places |
| Footfall, Beauty Within, Aside, Afterburn, Recourse, Spona, Ghost Ledger, SQL Noir, SmartDesk, Location Intelligence Agent, SMT Receipts, SMT World: Clock In | Built for hackathons; several live on free tiers | Various | None from users | Keep as portfolio proof on the website; don't sell |

### Why Lore and SMT

**Lore first:**
- It's the only product where a third party judged the product itself (not a hackathon pitch) and liked it.
- Its users are reachable for free: they work in public, on GitHub, and every project lists its maintainers.
- It needs no regulator, no partner contract and no card. Customers abroad come naturally, which Jannet prefers.
- There's a money path in steps: Anna's grants start at 200 qualified monthly users ($50/month at that tier, rising by tier, from the program rules in #46), then a paid tier for teams.

**SMT second, as a business deal:**
- It's where the most work, the patent and the only warm business contacts are.
- Selling to retail traders isn't honest while the record is net negative, and Jannet doesn't want to launch it in India. Selling **SMT World as an "AI that shows its work" page an exchange embeds for its own users** doesn't depend on SMT being profitable; it depends on the exchange wanting engaged users. That's a question two people can answer for us this month.
- The risk: crypto rules differ by country, and the exchange carries the user relationship. We say plainly that SMT isn't profitable yet.

**Not chosen, and why:** Chithi and Klarbrief compete with many new apps that explain official letters from a photo, for example Postera for German letters, [BriefAI](https://apps.apple.com/us/app/-/id6757674090) for US IRS, USCIS and court letters, [Myndio](https://apps.apple.com/app/id6779995564) for Swedish ones, [Tax Panic](https://play.google.com/store/apps/details?id=com.taxpanic.app) for US tax notices and [NKEMBA](https://www.producthunt.com/products/nkemba/launches) (all found 11-16). Our checked-quote verification is better engineering, but a consumer won't pay for the difference without a lot of marketing. Wiretrap's space has funded and acquired players.

### Closest competitors (lesson 0)

**Lore**
- [CodeScene](https://codescene.com/knowledge-distribution): knowledge distribution, "knowledge islands" and an off-boarding (bus factor) simulation. Paid per active author per month (third-party listings show €18 / €27 tiers and a free community tier; not checked on CodeScene's own pricing page). It's the closest thing and proves companies pay. **Lore is different in three ways:** it answers questions in plain words with a cited PR or issue for every claim; it reads public GitHub history with no install; and it triages new issues to people who know the area.
- GitHub's own CODEOWNERS file and reviewer suggestions: free, built in, but they say who *should* review, not who actually knows an area or where knowledge rests on one person.
- Command-line tools such as [git_sme](https://github.com/sjaveed/git_sme) and git-who: free, local, for developers comfortable in a terminal; no questions, no triage.

**SMT World for exchanges**
- Exchanges' own assistants: Bybit launched Bybit AI in September 2026 ([Finance Magnates](https://www.financemagnates.com/cryptocurrency/bybit-adds-chat-to-its-ai-stack-pointing-to-a-broader-shift/)); WhiteBIT has [AI Hub](https://coingape.com/whitebit-launches-ai-hub-trade-monitor-and-automate-through-your-favourite-ai-assistant/).
- White-label exchange vendors adding AI bots (Antier, AlphaPoint, CryptoRobotics, Shift Markets).
- Open-source LLM traders such as TradingAgents.
- **SMT's difference** (from the 16VC application): rules with tested records open trades; the AI explains and is graded; a reason is shown only if flipping it would change the decision. The smaller exchanges without a flagship AI product of their own are the opening.

**Decision for Jannet:** Lore + SMT pilot, or a different pair? (Waiting on Jannet, item 1.)

---

## 2. First customers: a 30-day plan (Nov 17 – Dec 16)

The goal by Dec 16: **10 people outside us using Lore on their own project, and 1–3 conversations with exchanges that end in a yes, a no, or a written pilot offer.** We count, we don't guess.

### Lore: who, where, offer, price

**Who exactly:** maintainers of active open-source projects with 5–50 regular contributors (big enough that "who knows this?" is a real question, small enough that a maintainer answers their own email). Second group: engineering leads at small companies who publish their code.

**Where to find them (all free):**
1. Anna's own marketplace, once v0.1.1 is approved and released ([#46](https://github.com/JannetEkka/DSProjects/issues/46)), and Anna's Discord, where their team offered to help with growth.
2. **FalkorDB's community.** Lore was demoed on FalkorDB's own repos (6 repos, 1,357 PRs). Ask them to share it.
3. **CHAOSS** (the open-source community that defines project-health metrics, bus factor among them): its community calls and chat.
4. Projects that tag "good first issue" and "help wanted": Lore's Experts and Triage tabs answer the questions newcomers ask there.
5. One public post per week on X, LinkedIn and dev.to showing a real answer on a well-known project, and one "Show HN" when the hosted version no longer has a cold start.

**The offer (concierge first):** "I'll run Lore on your project and send you who knows each area, where knowledge rests on one person, and three issues it would route, free. In return: 20 minutes of honest feedback." Do it by hand for the first 10. It teaches us what people value before we build a paid tier.

**Price:** free for open-source projects. For companies, offer a **paid pilot** after the first five feedback calls, at a founding price we set and test (for example a flat monthly fee for one organisation). We have no measured willingness to pay yet, so the first price is a test, not a forecast; CodeScene's per-author pricing (above) is the only outside reference.

**What we measure** (weekly, in the tracking issue):
- Messages sent → replies → Lore runs on their project → feedback calls → asked for more (repeat use) → said they'd pay → paid.
- Anna: qualified monthly users from the Developer Console (the program's own count).
- The one product question to answer: is it **Experts**, **Knowledge risk** or **Triage** that people come back for?

**Product work in the same 30 days** (Claude builds, Jannet reviews; each one is from Jannet's own list in `hackathons/anna/chat-notes.md`): connect a GitHub token so a run reads the whole repo, not 30 PRs; continue a cut-short load; copy results out as Markdown and a draft CODEOWNERS file. No new features beyond these until users ask.

### SMT: who, offer, price

**Who exactly:** two named contacts. WEEX's affiliate BD manager (Mitch, from `MITCH_EMAIL.md`) and the Bitunix partnerships contact who approached us. Then 3–5 smaller exchanges with no flagship AI product.

**The offer:** a 60-day pilot of SMT World for the exchange's users: they sign in, watch the agent trade on the simulated account, read why each trade opened, and see every graded call, including the losing ones. The exchange gets an engagement product with no build cost; we get distribution and a reference.

**Price:** one of two models, to settle in the first call: (a) the affiliate revenue share the exchange already runs, or (b) a fixed monthly pilot fee. We don't promise trading returns, and the pitch says the record is net negative so far.

**What we measure:** replies, calls held, a written pilot offer (yes / no / not now, and why). A "no" with a reason is a result.

### The calendar

| When | Lore | SMT | Other |
|---|---|---|---|
| **Nov 16–18** | Jannet: release v0.1.1 when Anna approves; message Dora on Discord | Claude drafts the WEEX and Bitunix emails (human voice); Jannet edits and sends | Buildathon shortlist email by **Nov 18** ([#121](https://github.com/JannetEkka/DSProjects/issues/121)) |
| **Nov 20–21** | — | — | **Buildathon, Kolkata, if shortlisted.** Its pitch rehearses exactly the story investors ask for (problem, market, way to reach it) |
| **Nov 17–30** | Claude: list 40 target projects with named maintainers; drafts the outreach; Jannet sends 10 a week. Claude ships the token/continue/export work | Calls with WEEX and Bitunix if they reply | Anna grant qualification window closes **Nov 30** |
| **Dec 1–16** | First 5 feedback calls done; decide on the paid pilot price; first company pilot offer | Follow-up; a pilot offer or a clear no | Read the numbers on Dec 16 and decide: keep going, change the offer, or switch product |

Claude can't send messages, sign up or post for Jannet. Every send is Jannet's; Claude drafts and tracks.

---

## 3. Company setup

**Not legal or tax advice.** These are the options with the costs we could find; several figures come from filing-service websites, not the government, and are marked. **Jannet confirms with a chartered accountant (CA) before filing anything.**

### The options

| Option | What it is | Cost to start | Cost every year | Fits when |
|---|---|---|---|---|
| **Stay as an individual (sole proprietor)** | No registration. Jannet invoices in her own name | ₹0 | Her own income-tax return. GST registration only if service turnover passes the threshold (₹20 lakh for most states, West Bengal included, as we understand it; confirm with the CA) | Now: before any revenue |
| **LLP** | Partnership with limited liability; needs at least 2 designated partners | Name reservation and FiLLiP fees by contribution slab (filing-service sites quote a few thousand rupees in total, plus a digital signature per partner) | Form 11 (May 30) and Form 8 (Oct 30) every year; audit only above ₹40 lakh turnover or ₹25 lakh contribution | Rarely for a startup: investors can't buy shares in an LLP |
| **Private Limited company** (MCA SPICe+) | The standard Indian startup company; can issue shares, can get DPIIT recognition | **No MCA filing fee for authorised capital up to ₹15 lakh** (Rule 38-based waiver, per [TaxGuru](https://taxguru.in/?p=982949) and other filing sites; check the MCA fee table). Plus West Bengal stamp duty on the MoA and AoA, digital signature certificates, and the CA's fee | A statutory audit every year whatever the revenue, annual returns (AOC-4, MGT-7), director KYC, income tax. This yearly cost is the real one; get two CA quotes | When a trigger below happens |
| **US Delaware C-corp** (Stripe Atlas) | US company; what US accelerators and SAFEs usually expect | **$500** one-time with Atlas, first year of registered agent included ([Stripe](https://stripe.com/resources/more/how-much-does-it-cost-to-incorporate-a-business-in-the-us-here-is-what-you-need-to-know)) | Registered agent $100/year after year one; Delaware franchise tax and annual report (third-party estimates start around $175–$400; [Delaware](https://corp.delaware.gov/) is the source); US federal tax filings; Indian compliance on top (below) | Only if a US investor requires it, and only after advice |

**The Indian-resident rules for a foreign company** (FEMA Overseas Investment Rules, 2022): when an Indian resident sets up or holds shares in a foreign company, that's an overseas direct investment (ODI), reported through her bank. Two points, as summarised by [Treelife](https://treelife.in/legal/fema-odi-rules-and-regulations/) and other guides (check against RBI's Master Direction before relying on them):
- A resident individual may hold ODI only in a foreign operating company **not engaged in financial services**, and **without a subsidiary she controls**. SMT trades crypto futures, which could be read as financial services, and the second condition blocks the common "US parent, Indian subsidiary" setup for an individual.
- So a US company is not a quick form; it's a decision for a CA or lawyer who knows FEMA.

### DPIIT Startup India recognition

- Free to apply on the Startup India portal. Only a **Private Limited company, LLP or registered partnership** qualifies; an individual doesn't ([Startup India](https://www.startupindia.gov.in/bodo/content/sih/en/startupgov/startup_recognition_page.html)).
- Benefits that matter to us: eligibility for the **Startup India Seed Fund** (below), lower patent fees and expedited examination for a recognised startup, self-certification for some labour and environmental laws, and the tax-holiday application (80-IAC), which needs a separate approval.
- **The patent:** Jannet filed SMT's provisional as a natural person, which already pays the lowest fee tier, so recognition doesn't lower her fees today. Whether the company should own the patent (an assignment from Jannet to the company) is a question for a patent agent and the CA. The dates don't move: **Form 3 by Jan 26, 2027; complete specification by Jul 26, 2027** (`EXPENSES.md` budgets ₹25–60K for a patent agent to draft it; that's an earlier estimate, not a quote).

### Recommendation

1. **Now: stay an individual.** Use the name as a brand on the website and in emails. Nothing stops Jannet selling a pilot, invoicing a foreign client or entering the Buildathon without a company (the Buildathon's FAQ welcomes "aspiring entrepreneurs" and solo founders; it says nothing about incorporation).
2. **Incorporate a Private Limited company when the first of these happens:**
   - a customer needs to contract with a company;
   - a grant, program or prize needs one (Seed Fund, NVIDIA Inception, most cloud credit tiers, a Buildathon payout if its terms require it);
   - an investor offers money;
   - Jannet decides the patent should be the company's before the Jul 2027 filing.
3. **A US company only if a US investor's terms require it**, after a FEMA-aware CA or lawyer says how. If 16VC accepts SMT, their reply to "which entity and jurisdiction does your SAFE need?" decides this.

### The name

**"JTech Solutions" has three problems** (checked 11-16):
- **Domains:** `jtechsolutions.com` (registered since 2007), `.in` and `.ai` are taken; so are `jtech.ai`, `jtechai.com` and `jtechlabs.com`.
- **Company name:** no exact "JTech Solutions Private Limited" showed up, but J & J Tech Solutions, J.M. Tech Solutions, JAI Tech Solutions and J Tech IT Solutions & Training Private Limited exist (aggregator listings). MCA's name rules reject names that are too close to existing ones, so it may not pass.
- **Trademark:** live US registrations for **JTECH** (Class 9, JTECH Global Enterprises) and **JT TECH** (Class 42, software services). Selling software abroad under "JTech" risks a conflict.
- "Solutions" also reads as an IT-services shop, not a product company.

**Proposal:** pick a distinctive name, then check it properly before paying for anything: MCA's name check (RUN) and company search, IP India's trademark search, the USPTO's search, and the domain. Some starting points, domain-checked only (RDAP lookups on 11-16 found no registration; .io couldn't be checked):

| Candidate | Domains not registered (11-16) | Note |
|---|---|---|
| **Saakshi Labs** (साक्षी, "witness") | saakshilabs.com, .ai, .in | Fits the thread through the work: every answer comes with its evidence. "Sakshi Software" and "Sakshi Softech" exist, and a tool named SAAKSHI exists; MCA may treat them as close |
| **Receipt Labs** | receiptlabs.ai, .in (.com taken) | Echoes SMT Receipts and Proof of Fix's receipts |
| **JTech Labs** | jtechlabs.in, jtechlabs.ai (.com taken) | Keeps "JTech"; the US trademark risk above remains |
| **jtechhq.com** | jtechhq.com | Keeps "JTech" as a brand only |

Jannet may have her own idea; the checks are the same. No domain is bought until she says so.

---

## 4. The company website

- **One page per product that's for sale (Lore, SMT World)**, then a short "what we've built" section with the strongest measured results from `projects/`, each with its live demo link, and an honest line on what isn't measured.
- **Built from what exists:** `_portfolio_src/data.py` already holds every project with its links; `build.py` renders the portfolio with no dependencies. The company site can be a second template over the same data, so one edit updates both.
- **Lesson 10 for the home page:** a headline of six words or fewer; the product on the first screen; one accent colour; not the default dark navy.
- **Hosting:** Cloudflare Pages or GitHub Pages, ₹0, no card (Cloudflare is already in the no-card list in `hackathons/cards.md`). The live demos stay on Render's free tier, which has a cold start of up to a minute; the site says so.
- **Cost:** only the domain, a yearly fee paid to a registrar. Price it when the name is chosen; it may need a card, which goes in `cards.md` first.
- **Contact:** a form or a plain email address on the domain. Several programs (Google's cloud credits among them) want a company email on the same domain as the website.
- **Who:** Claude builds it in a build session after Jannet signs off the name and the page plan (discuss-before-build rule).

---

## 5. Funding: non-dilutive first

| Source | What it gives | Needs | Card? | When |
|---|---|---|---|---|
| **Google AI Startup Buildathon India** | Top 10 teams: **$5,000 cash + $5,000 Google AI & Cloud credits** each ([startupbuildathon.com](https://startupbuildathon.com)); mentors, investors, Google's startup programs | Shortlist by Nov 18; build "a new product with Google AI" and deploy on Google Cloud | **Unclear.** The site doesn't say whether participants get cloud access at the event; credits are listed only as a prize. Deploying on Google Cloud normally needs a billing account (a card). Ask the organisers before the event. The previous billing account is closed (`cards.md`) | Nov 20–21 |
| **Anna grants** (Lore) | Monthly grant by tier, from **$50 at 200 qualified monthly users** up to $5,000 at 20,000 (program rules in #46) | Lore live on the Anna marketplace; real signed-in users | No | Qualification to Nov 30, then monthly cycles |
| **Hackathon prizes** | Cash | Already entered: Proof of Fix (GitLab, ~Nov 16), Aside (Amazon, ~Dec 3), Footfall (Nebius × NVIDIA, Dec 1–15), Lights Out (Hermes), Beauty Within (~Nov 24) | Per hackathon | Ongoing; keep entering, but the 30-day plan comes first |
| **Startup India Seed Fund** | Up to **₹20 lakh grant** for proof of concept and prototype, or up to ₹50 lakh as debt or convertible for commercialisation, through an approved incubator | DPIIT-recognised, incorporated not more than 2 years before applying, at least 51% Indian promoters ([seedfund.startupindia.gov.in](https://seedfund.startupindia.gov.in/about)). The scheme was approved for four years from 2021-22, so **check it's still open** | No | After incorporation; a reason to incorporate if it's open |
| **Google for Startups Accelerator: India** | Equity-free, 3 months, mentors, credits subject to eligibility | AI-first, seed to Series A, traction ([Google](https://startup.google.com/programs/accelerator/india/)) | No | The 2026 class closed Apr 19; watch for the 2027 call. Needs traction first |
| **Google for Startups Cloud Program** | Up to $2,000 on the Start tier, per third-party guides | A Google Cloud account **with a billing ID**, a public website and a company email on that domain | **Yes** (billing account) | Only if we need Google Cloud; record the card first |
| **AWS Activate Founders** | $1,000 in credits, some startups up to $5,000 ([AWS](https://aws.amazon.com/startups/credits)) | Self-funded, pre-Series B, a company website or profile, an AWS account on the Paid Tier plan | **Yes** (a paid-tier AWS account needs a card; we skipped OpenCV for this reason) | Only if we need AWS |
| **Microsoft for Startups** | Azure credits, starting around $1,000; more after business verification (third-party reports) | An idea to start; a registered business for larger amounts | Check at sign-up | Only if we need Azure |
| **NVIDIA Inception** | Free membership; partner credits and discounts on request | Per third-party guides: incorporated, a website, at least one developer; **crypto-focused companies are excluded** | No | After incorporation, for Lore (not SMT) |

**Free tiers already carry us:** Render, Cloudflare, Firebase Spark, Oracle Always Free, AI Studio keys and NVIDIA build keys run everything today at ₹0. Credits matter only when a paying customer needs more.

**Angels and pre-seed: what they'd need to see, and when.** Investors and accelerators ask about traction: who uses it, who pays, how fast that grows. Today we can show engineering depth and honest evaluation, which is the founder half of the story. The product half is what the 30-day plan builds: named users, repeat use, a paid pilot, a reason the next 100 users will come. **We don't approach angels before we have at least one of those.** The exceptions already in motion: 16VC (applied; they asked follow-up questions on 10-19) and the Buildathon's investor showcases. No funding is promised by anyone.

---

## 6. Hiring

- **Nothing salaried until revenue or a grant covers it.** An unpaid "equity-only" team at this stage tends to cost more time than it saves.
- **First paid help: a freelance designer for one fixed job** (the company site and Lore's interface), paid from the first prize, grant or pilot money. Fixed scope, fixed price, agreed in writing.
- **Second: product help** only when there are enough users that we can't talk to all of them ourselves.
- **An engineer for SMT World** only with an exchange pilot signed. The 16VC plan budgeted one for SMT World's front end if that funding came; that plan stands only if it does.
- **Equity** is for a long-term co-founder, not a contractor, and needs a company first (part 3).

---

## Costs at a glance

| Item | Cost | When | Source |
|---|---|---|---|
| Selling, outreach, Buildathon entry | ₹0 | Now | — |
| Website hosting | ₹0 | After the name | Cloudflare / GitHub Pages free plans |
| Domain | A yearly registrar fee, priced when chosen | After the name | Registrar |
| Private Limited company | MCA filing fee ₹0 up to ₹15 lakh capital, plus stamp duty, digital signatures and CA fees; then a yearly audit and filings | On a trigger (part 3) | MCA fee table; CA quotes |
| US C-corp (only if required) | $500 with Atlas, then $100/yr agent, Delaware tax, US and Indian filings | Only on advice | Stripe; Delaware |
| Patent: Form 3 | Check the fee with a patent agent | **By Jan 26, 2027** | IP India |
| Patent: complete specification | Agent drafting (earlier estimate ₹25–60K in `EXPENSES.md`) plus the IP India fee | **By Jul 26, 2027** | Patent agent quote |
| Designer (freelance) | Fixed quote | After first money comes in | Quote |

---

## Owners and dates

| Task | Owner | By |
|---|---|---|
| Read this plan; decide parts 1–3 | Jannet | Nov 18 |
| Watch for the Buildathon shortlist; if selected, ask the organisers about cloud access and the payout terms | Jannet | Nov 18 |
| Draft the WEEX and Bitunix emails | Claude | Nov 17 |
| Send them | Jannet | Nov 18 |
| Release Lore v0.1.1 on Anna when approved; message Dora | Jannet | when approved |
| List 40 target projects with maintainers; draft outreach | Claude | Nov 20 |
| Send 10 outreach messages a week; hold feedback calls | Jannet | weekly to Dec 16 |
| Lore: GitHub token, continue a cut load, Markdown/CODEOWNERS export | Claude (build session, after sign-off) | Nov 30 |
| Name check (MCA, IP India, USPTO, domain) for the chosen name | Claude (search), Jannet (decides) | Nov 25 |
| Company site from `_portfolio_src` | Claude (build session) | after the name |
| Two CA quotes: Pvt Ltd yearly cost; advice on patent ownership and on a US entity | Jannet | Dec 10 |
| Patent agent: Form 3 by Jan 26 | Jannet | Dec 31 |
| Count the results and decide what's next | Jannet + Claude | Dec 16 |

## Waiting on Jannet

1. **Products:** Lore first and SMT as an exchange pilot? Or a different pair? (Part 1.)
2. **Paid build work:** does Jannet also want to take fixed-price AI build jobs for clients abroad under the company name, to bring money in sooner? It's the fastest cash, and it competes for the same hours as finding users. If yes, how many days a week. (Not in the plan above until she says.)
3. **Outreach:** OK for Claude to draft, and Jannet to send, the WEEX and Bitunix emails this week?
4. **Name:** keep "JTech Solutions", or choose another (part 3)? Any names she already likes?
5. **Incorporation:** agree to wait for a trigger, and to get two CA quotes in the meantime?
6. **Buildathon:** if shortlisted, enter with a new product built on SMT, or something else? Its own discussion session is planned in [#121](https://github.com/JannetEkka/DSProjects/issues/121). Deploying on Google Cloud may need a card: ask the organisers first, and record any card in `cards.md` before it's added.
7. **16VC:** any reply since the 10-19 follow-up?
8. **Patent ownership:** a question for a patent agent and the CA, before the Jul 2027 deadline.

## Sources

Repo: `projects/*.md` (measured results and weak spots), `hackathons/lessons.md`, `hackathons/november-2026.md`, `hackathons/october-2026.md`, `hackathons/cards.md`, `hackathons/anna/chat-notes.md`, issues [#46](https://github.com/JannetEkka/DSProjects/issues/46), [#93](https://github.com/JannetEkka/DSProjects/issues/93), [#121](https://github.com/JannetEkka/DSProjects/issues/121); SMT's `docs/business/16VC_APPLICATION.md`, `EXPENSES.md`, `MITCH_EMAIL.md`.

Web (read 2026-11-16): [startupbuildathon.com](https://startupbuildathon.com) · [Startup India recognition](https://www.startupindia.gov.in/bodo/content/sih/en/startupgov/startup_recognition_page.html) · [Startup India Seed Fund](https://seedfund.startupindia.gov.in/about) and [TaxGuru's summary](https://taxguru.in/corporate-law/dpiit-startups-grant-upto-rs-20-lakhs-loan-upto-rs-50-lakhs.html) · SPICe+ fee waiver: [TaxGuru](https://taxguru.in/?p=982949), [SetIndiaBiz](https://support.setindiabiz.com/portal/en/kb/articles/private-limited-company-registration-government-fee-structure) · LLP: [Kanakkupillai](https://www.kanakkupillai.com/learn/costs-and-fees-associated-with-llp-registration-in-india/) · ODI rules: [Treelife](https://treelife.in/legal/fema-odi-rules-and-regulations/), [VJM Global](https://www.vjmglobal.com/blog/revised-overseas-investment-rules-fema-a-step-toward-ease-of-doing-business-part-1) · [Stripe: US incorporation costs](https://stripe.com/resources/more/how-much-does-it-cost-to-incorporate-a-business-in-the-us-here-is-what-you-need-to-know) · [Google for Startups Accelerator: India](https://startup.google.com/programs/accelerator/india/) and [Google's blog](https://blog.google/intl/en-in/inviting-ai-first-startups-to-apply-for-google-for-startups-accelerator-india/) · [Google for Startups Cloud Program summary](https://www.startupgrantsindia.com/providers/google/google-for-startups-cloud-program) · [AWS Activate credits](https://aws.amazon.com/startups/credits) · Microsoft for Startups: [guide](https://guptadeepak.com/startup-offers/guides/microsoft-for-startups) · NVIDIA Inception: [guide](https://hub.causo.ai/guides/how-to-apply-to-nvidia-inception-2026) · Patent fees for startups: [Intepat](https://www.intepat.com/blog/patent-benefits-for-msme-india) · [CodeScene knowledge distribution](https://codescene.com/knowledge-distribution) and [G2 pricing listing](https://www.g2.com/products/codescene/reviews?page=2) · [git_sme](https://github.com/sjaveed/git_sme) · [Bybit AI](https://www.financemagnates.com/cryptocurrency/bybit-adds-chat-to-its-ai-stack-pointing-to-a-broader-shift/) · [WhiteBIT AI Hub](https://coingape.com/whitebit-launches-ai-hub-trade-monitor-and-automate-through-your-favourite-ai-assistant/) · letter-explainer apps: [BriefAI](https://apps.apple.com/us/app/-/id6757674090), [Myndio](https://apps.apple.com/app/id6779995564), [Tax Panic](https://play.google.com/store/apps/details?id=com.taxpanic.app), [NKEMBA](https://www.producthunt.com/products/nkemba/launches) · Name checks: company aggregators ([J & J Tech Solutions](https://www.infyner.com/finance/j-j-tech-solutions/U72200DL2015PTC282956), [J.M. Tech Solutions](https://qorpiq.com/company/jm-tech-solutions-private-limited/U72300DL2015PTC278109), [JAI Tech Solutions](https://companies-india.onrender.com/company/jai-tech-solutions-private-limited-U43212TN2026PTC191540), [J Tech IT Solutions & Training](https://qorpiq.com/company/j-tech-it-solutions-training-private-limited/U72900UP2013PTC061272)), US marks ([JTECH Global Enterprises](https://trademarkdir.com/owner/jtech-global-enterprises-inc), [JT TECH](https://markinton.com/trademark/jt-tech-97414994)), domains by RDAP (Verisign for .com, rdap.org for others), [Sakshi Softech](https://clutch.co/profile/sakshi-softech-private), [SAAKSHI tool](https://www.jukshio.com/saakshi-ai-diagnostic-tool).
