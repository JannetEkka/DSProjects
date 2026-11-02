# Project write-ups for FDE interviews

One file per project on the portfolio. Each one answers the four things a forward-deployed-engineer interview probes, using what actually happened in the repo (commits, PRs, issues and tracker comments), not what the pitch said:

1. **Architectural reasoning:** why this database, this hosting, these frameworks.
2. **Data & security pipelines:** auth and access control, how data flows, where it lives.
3. **Reliability & failure operations:** state after a crash, fallbacks, observability.
4. **Evaluation & optimisation metrics:** the measured result against a stated baseline, cost, constraints.

Every file also has **"What the history shows"** (real decisions, in order) and **"Weak spots to own before they ask"**. Read those two first: they're what an interviewer finds if they open the repo. Each file ends with its sources.

Written 2026-11-01/02 from the repos as they stood then.

## Production system

| Project | File | The one line to lead with |
|---|---|---|
| Smart Money Trading (SMT) | [smt.md](smt.md) | Moved a live system off GCP to ₹0 in two days; found an order bug that rejected 1,137 live orders while every test passed |

## October–November 2026 builds

| Project | Hackathon | File | Lead with |
|---|---|---|---|
| Beauty Within | YouCam (Perfect Corp), submitted 11-02 | [beauty-within.md](beauty-within.md) | Calibrated the vendor's lip render to within ~2 L*, and dropped a feature that brightened whole faces |
| Spona | NTP Novi Sad (JigJoy × Mozaik) | [spona.md](spona.md) | 12 concurrent agents, every claim checked by a critic while the others work; 489 challenges in 5 min 48 s |
| Footfall | Qloo + Nebius × NVIDIA | [footfall.md](footfall.md) | A hard spend cap and replay mode, so a public demo can't run up the card or die when a key expires |
| SQL Noir | Open Agent (Zetaris), Track 02 | [sql-noir.md](sql-noir.md) | No verdict from the model: every answer is a result-set comparison on live data |
| Proof of Fix | GitLab Duo | [proof-of-fix.md](proof-of-fix.md) | A fix that passed tests and AI review was caught by production (32% → 9%), then proven (0 of 875) |
| Ghost Ledger | HackerRank Orchestrate | [ghost-ledger.md](ghost-ledger.md) | 100% status accuracy on samples; the transcript lesson (3/10) |
| Aside | Amazon Fire TV | [aside.md](aside.md) | Spoilers 6/16 → 0/16 by never giving the model the future |
| Afterburn | IEEE ClimateChain | [afterburn.md](afterburn.md) | Read the burn scar, not the flame; a 3.4× lift vs VIIRS; a transparent rule beat the ML model |
| Recourse | Web3 for Social Good (Round 2) | [recourse.md](recourse.md) | A receipt names only the records that flip the decision; an AI guard rejects invented numbers |
| RSNA Knee | Kaggle | [rsna-knee.md](rsna-knee.md) | Scored public label sets against 58 hand labels before training on them |
| Lore (+ Anna port) | Graph Hacks (FalkorDB) | [lore.md](lore.md) | 90% real reviewer in top 3, against 88% for the obvious baseline, and I say where it loses |
| Klarbrief | Hack Apertus | [klarbrief.md](klarbrief.md) | Offline on a 4-core CPU; the verifier stopped 6 of 7 wrong dates |
| SMT Receipts | Monad Metropolis | [smt-receipts.md](smt-receipts.md) | An ownerless contract grades the bot's calls; the record is unflattering, which is the point |
| SMT World: Clock In | Solana Mobile | [smt-world-clock-in.md](smt-world-clock-in.md) | Two wallet bugs found and fixed through four releases tested on my own phone |

## 2024–2026 agents and GenAI

| Project | File | Lead with |
|---|---|---|
| Wiretrap | [wiretrap.md](wiretrap.md) | "Said No, Did Yes": audit the tool-call log, not the reply |
| SmartDesk | [smartdesk.md](smartdesk.md) | The eval stopped a reranker that cost 82× latency for a gain inside the noise |
| Location Intelligence Agent | [location-intelligence-agent.md](location-intelligence-agent.md) | Remote MCP (BigQuery, Maps) vs SmartDesk's stdio MCP |
| SMT Chain Adapters | [smt-chain-adapters.md](smt-chain-adapters.md) | One brain, thin per-chain adapters, guardrails before signing |
| Smart Money Tracker | [smart-money-tracker.md](smart-money-tracker.md) | ⚠️ no code available; fill the gaps before an interview |
| AutoKorrekt | [autokorrekt.md](autokorrekt.md) | ⚠️ dates: the repo says 2024, not 2023 |
| MedTestAI | [medtestai.md](medtestai.md) | Workload Identity Federation in CI, no long-lived keys |
| VerseCanvas | [versecanvas.md](versecanvas.md) | The "before" picture: credentials learned the hard way |
| Asha Chatbot | [asha-chatbot.md](asha-chatbot.md) | Rasa, not an LLM: it never invents a job |
| WebContentQnA | [webcontentqna.md](webcontentqna.md) | A model ladder; the SSRF risk I'd fix |
| E-commerce analysis | [ecommerce-analysis.md](ecommerce-analysis.md) | Polite scraping with checkpoints |
| NBFC Loan Default | [nbfc-loan-default.md](nbfc-loan-default.md) | ⚠️ code is in .docx, no score recorded |
| Yatra automation | [yatra-test-automation.md](yatra-test-automation.md) | POM + data-driven + Jenkins: the Deloitte skill set |

## PGP in AI/ML coursework (UT Austin McCombs × Great Lakes)

| Project | File | Note |
|---|---|---|
| Automotive Surveillance (capstone) | [automotive-surveillance-capstone.md](automotive-surveillance-capstone.md) | 69.2% on a **16-class subset**, not all 196 |
| Botanical classification | [botanical-classification.md](botanical-classification.md) | 83.79% CNN; the flowers transfer runs failed with NaN loss |
| Signal & SVHN | [signal-svhn-classification.md](signal-svhn-classification.md) | Signal ~65% (not 90%); SVHN 87.1% |
| Customer churn | [customer-churn.md](customer-churn.md) | RF + grid search 81.48%; accuracy is the wrong headline |
| Semiconductor yield | [semiconductor-yield.md](semiconductor-yield.md) | ⚠️ SMOTE before the split: 99.2% is leaked |
| YouTube AdView | [youtube-adview.md](youtube-adview.md) | R² 0.25: say it plainly |
| Automobile USL | [automobile-usl.md](automobile-usl.md) | 398 × 8 and 846 × 18, not "102 features" |
| Stock sentiment | [stock-sentiment-nlp.md](stock-sentiment-nlp.md) | Test F1 0.30–0.38; Mistral-7B GGUF for summaries |
| New-Wheels SQL | [new-wheels-sql.md](new-wheels-sql.md) | KPI definitions matter more than queries |
| Business analytics | [business-analytics-sl.md](business-analytics-sl.md) | "86%" was an R² |
| Applied statistics | [applied-statistics.md](applied-statistics.md) | No evidence of a difference ≠ no difference |

## Things these write-ups found that need fixing outside interviews

- **Résumé dates:** AutoKorrekt "May 2023 – Jan 2024" contradicts the public repo (commits Jun–Dec 2024). JTech reads "Jan | 2025", while SMT says Jan 2024.
- **Portfolio card corrections** (applied in the same update): MedTestAI, e-commerce, capstone, signal/SVHN, churn, USL, business analytics, applied statistics.
- **A committed Firebase service-account key** in the private repo `smt-application`: rotate it, then remove it from history.
- **SMT figures:** quote today's (≈87.5K lines of Python outside tests, 3,152 tests, 362 merged PRs, 673 findings), not the older 91K / 344 / 611.
