# Design brief: Countersign (Mozilla Otari Hackathon: Devs Wilding Online)

**Process (Jannet, 11-08):** a discussion session wrote this brief on 11-12 (https://claude.ai/code/session_016VDQoozJyWqR9nsww5zYBx). Jannet reads it, explains it back, and signs it off. Then a **separate build session** starts from the build prompt in section 10. Checked against [../lessons.md](../lessons.md). Name: **Countersign** (a second model has to countersign every claim before it is shown); Jannet approved it on 11-12. Jannet registered on DoraHacks and joined the Discord on 11-12.

## 0. The hackathon, in one screen

- **Link:** https://dorahacks.io/hackathon/mozilla-devs-wilding/detail. Online, solo is fine.
- **Deadline:** **Nov 12, 10:29 IST** (04:59 UTC, "Extended" on the DoraHacks timeline, read 11-12). The page text still says "Nov 11th 11:59PM", so 10:29 IST is the latest possible. Our own target: submitted by **08:30 IST**.
- **The brief:** "Finish your side projects using Otari!" The hosted gateway at otari.ai is required. A gateway is one address our code calls instead of calling each model company directly; it picks the model, counts the cost and enforces limits.
- **Deliverables** (missing any one means no prize):
  1. Project name, the email used on otari.ai, one line on what the project does.
  2. Public GitHub repo link and the hackathon branch name.
  3. A link to the first commit on that branch where Otari came in.
  4. The list of Otari features used.
  5. Any PRs or issues we opened on the Otari repo.
  6. A 3–5 minute demo video: Jannet's own screen recording with her voice. No AI video or voice.
  7. Feedback on Otari: a 3–5 minute screen recording, or written answers to three questions, or both. We do the written one.
- **Judging** (rubric doc, out of 100):
  - Open-weight models, 30: "20 points: The project meaningfully uses at least one open-weight model. 10 additional points: The project uses two or more open-weight models for different purposes."
  - Otari features, 60: "10 points for each advanced capability demonstrated", from eight: routing and fallbacks, MCP integrations, web search or web fetch, code execution, budgets and spending limits, multiple models serving distinct roles, guardrails, per-user budgets. "A feature only earns points when it is actually used in the application, not simply enabled in the dashboard."
  - Project and demo, 10: 5 for "works and demonstrates a real use case", 5 for a video that "clearly explains how Otari was integrated and demonstrates the claimed capabilities".
- **Prizes:** $1,000 + 3 hours with Mozilla.ai engineers / $200 + 2 hours / 1 hour.
- **Money:** none of ours. Jannet's otari.ai account shows a **$2.00 welcome credit, "No card needed"** (11-12). The hackathon's "$20 for the first 200 sign-ups" has not appeared; it may come as a voucher (the Billing page has "Redeem voucher"). We plan for $2 only. **Never click Add funds, Recurring top-up or Auto top-up.** No card is on file, so [../cards.md](../cards.md) needs no row.

## 1. The idea

**One sentence:** for someone who reads a weekly market brief written by a model, Countersign shows only the claims a second model and a calculation could confirm against that week's news and prices, and shows what was removed and why.

**The side project being finished:** [Stock Market Sentiment Analysis](../../Stock_Market_Sentiment_Analysis_NLP/) (PGP in AI/ML, Nov–Dec 2024). It classified the sentiment of 349 Apple-related headlines (Jan–Apr 2019) and wrote weekly summaries with Mistral-7B on a notebook GPU. Two things were left unfinished, both written down in [the project note](../../projects/stock-sentiment-nlp.md) before this hackathon:
- The summaries had no grounding check: "LLM summaries can invent facts."
- Sentiment was weak: test F1 0.30–0.38, with the selected model at 0.366.

**Why it's not the obvious use (lessons 1):** the obvious Otari project is a chat app with a budget meter. Here the gateway's features each do a job in a checking pipeline: two models that must disagree usefully, a sandbox that redoes the arithmetic, a guardrail that stops the brief turning into investment advice.

**Closest existing work (lessons 0, searched 11-12):**
- [Daily Stock Analysis](https://github.com/ZhuLinsen/daily_stock_analysis): an LLM stock dashboard with sentiment scores. No second-model or calculation check found.
- [FinGPT](https://github.com/AI4Finance-Foundation/FinGPT): finance language models, not a checked brief.
- In this hackathon's 42 builds: Recount (recomputes numeric claims in Otari's sandbox), Lintel (one model writes, another checks, on NYC building records), Themis (claim ledger for pull requests). None is about market news.
- Honest note: stock-news sentiment is a common project. What is ours is the checked brief and the before/after numbers on Jannet's own 2024 project. Jannet accepted this on 11-12 because the brief asks for an existing side project.

**Ideas considered and dropped:**
- Proof of Fix + Otari: PR and claim checkers are the most crowded group in the 42.
- Lights Out + Otari: Lingua already did "Hermes plugin finished with Otari", and Lights Out's core is fixed code with little for a model to do.
- SMT (checked 11-12 at Jannet's request): its personas do read market news and regime, but it trades crypto futures, its core repo is private (the rules need a public repo), it is a live system with a patent pending, and its own audit found sentiment had no skill at 24h. Not a side project to finish in a night.

## 2. The measured comparison (decide before building)

Both are run, and both are reported, including if they come out badly.

**A. Sentiment score, two ways.**
1. **Same split as 2024.** The notebook split the data 70/15/15 with `train_test_split(..., random_state=42, stratify=y)` twice, and scored weighted F1. We rebuild that exact test set (about 53 headlines) and score an open-weight model on it with no training. Compared with: the 2024 selected model's **0.366**, and RF 0.296, GB 0.348, XGBoost 0.378, all from the notebook.
2. **All 349 headlines.** The model was never trained on any of them, so every row is a test row. This is a bigger and steadier sample, but the 2024 models can't be fairly scored on it (they trained on 70% of it), so we report it on its own and say so.

- Are we trying to improve the score? Yes, but we promise nothing: we report what we measure. The labels are -1/0/+1 with 170 neutral, 99 negative, 80 positive, and we don't know how the course created them. If the model scores no better than 0.366, the README says that and says the labels may be the limit.
- No extra test data is added. More labelled data from elsewhere would use a different labelling rule and wouldn't compare with 2024.
- Caveat to state: 2019 news may be in a model's training text, though these labels are not.

**B. The check, on and off.** For the 18 weekly briefs: how many claims the writer made, how many the check removed, and why (unsupported by the cited headlines, cited headline doesn't exist, number doesn't match the price data). With the check off, all of those would have been shown. That count is the impact statement: "N of M claims in the unchecked briefs could not be confirmed."

## 3. What a judge sees in the first 10 seconds

- One weekly brief as a newspaper column. Confirmed claims in black, each with a small source mark. Removed claims struck through in red with a one-line reason beside them.
- A toggle: "Check on / Check off".
- Above it, two numbers: sentiment F1 then and now, and claims removed out of claims written.
- **Headline:** "Every claim checked before you read." (six words)
- **Look:** a financial broadsheet: serif type, off-white paper. One accent colour, red, used only for what the check removed. Motion: claims appear, then the failed ones get struck one by one.

## 4. Architecture

```
stock_news.csv (349 headlines + daily prices, 2019)
        │
        ├─► [1] Classifier model ──► label -1/0/+1 ──► code scores F1 (same split, all 349)
        │
        └─► group by week (18 weeks)
                 │
                 ▼
        [2] Writer model  ──► brief as a list of claims, each citing headline ids and numbers
                 │
                 ▼
        [3] Checker model (different family) ──► per claim: supported / not, with the quote
                 │
        [4] Otari code execution ──► recomputes weekly price change, high, low from the CSV rows
                 │
        [5] Decision rule (our code) ──► keep or remove each claim
                 │
        [6] Otari guardrail ──► blocks buy/sell advice in the final text
                 │
                 ▼
        run artefacts (JSON) ──► static results page
```
All model calls go through `https://api.otari.ai/api/v1` with one API key that has a spending cap.

**Model judgment vs fixed rules (lessons 4):**
- Models: label a headline; write claims; say whether the cited headlines support a claim.
- Code: check every model reply has the required fields and allowed values; check cited headline ids exist in that week; compare each number in a claim with the sandbox's recomputed figure; decide keep or remove; compute F1. A claim is kept only if the checker says supported **and** its ids exist **and** its numbers match. The model describes, the code decides.

**The models' roles (lessons 7):** the writer is asked to summarise; the checker is asked to find what the headlines do not support, and never sees the writer's reasoning, only the claim and the cited headlines. They are from different model families so they don't share the same blind spots. Exact model ids are picked from Jannet's Models page at build time; GPT OSS 120B is confirmed available.

**Otari features used, six for 60 points:**
| Feature | Where it is really used |
|---|---|
| Multiple models in distinct roles | classifier/writer, checker |
| Routing and fallbacks | a routing policy: writer's main model, with a second open-weight model if the first fails |
| Code execution | step 4 recomputes the price figures |
| Web search or fetch | "this week" mode: fetch current Apple headlines and run the same pipeline on them, to show it works on news the models can't have memorised |
| Budgets and spending limits | the key's cap; the run stops cleanly and says so when Otari refuses |
| Guardrails | step 6 |

Skipped: MCP, and per-user budgets (open issue mozilla-ai/otari#3187 says hosted workspaces can't create per-user keys and budgets through the API yet).

**Hosting and cost:** Python scripts, no server. The results page is static HTML built from the run's JSON files, served from the repo. Cost: the $2 credit only.

## 5. The flow, step by step

1. Load the CSV; rebuild the 2024 test split with the same seed.
2. Classify all 349 headlines; reject any reply that isn't -1, 0 or +1 and retry once; a second failure is recorded as "no answer" and counted as wrong.
3. Score weighted F1 on the 2024 test rows and on all 349.
4. For each week: writer returns claims as JSON.
5. Checker judges each claim against its cited headlines.
6. Sandbox recomputes that week's price figures.
7. Decision rule keeps or removes each claim and records the reason.
8. Guardrail screens the kept text.
9. Write `results.json`; build the page.
10. Bad input: a week with no headlines gets "no brief", not an invented one. A budget refusal stops the run and the page shows which weeks are missing. Nothing is marked complete with weeks missing (lessons 8, 9).

## 6. Decisions settled now

- **Repo and branch:** the side project lives in this repo, so the hackathon branch is `otari-hackathon` in `JannetEkka/DSProjects`, with new code under `Stock_Market_Sentiment_Analysis_NLP/countersign/`. Jannet asked on 11-12 whether a new public repo would be better. We stay here: the rules say "Start a new branch in your project", this repo's history shows the 2024 notebook the branch finishes, and it is already public. A separate repo can be split out after the deadline.
- **Where it runs:** the build session tries to reach `api.otari.ai` from the cloud and asks for the key through the secure credential form. If the cloud can't reach it, Jannet runs one command in Ubuntu (WSL) and sends back the output. The key is never pasted in chat.
- **Key:** on otari.ai, API keys → create one named `countersign`. Environment variable: `OTARI_API_KEY`.
- **Budget:** cap the key at $1.50, leaving $0.50 spare.
- **Requests stay short:** open issues #3131 and #3144 report a 504 from the hosted gateway after about 30 seconds, so one headline or one claim per call.
- **Feedback:** written answers, from what really happened in the build. Given to Jannet in chat, not stored in the repo (rule of 11-11).

## 7. Acceptance conditions

- [ ] Every model call in the code goes to otari.ai; no direct provider call.
- [ ] Two open-weight models from different families, each with its own job, visible in Otari's Activity view.
- [ ] Each of the six features produces a visible effect in a run: a fallback that fired (forced once for the demo), a sandbox result, a fetched live headline, a budget refusal handled, a guardrail block.
- [ ] F1 reported on the rebuilt 2024 split and on all 349, next to the 2024 figures, with the caveats from section 2.
- [ ] Claims written, removed, and reasons, for all 18 weeks.
- [ ] Tests for the decision rule and reply validation pass.
- [ ] Page: the six-word headline, a brief on the first screen, red used only for removed claims, the strike-through motion, the on/off toggle.
- [ ] README states the impact with its source numbers and names the closest projects.
- [ ] No submission text in the repo.

## 8. Demo plan

3–5 minutes, Jannet's screen and voice.
1. (30 s) The 2024 project note: no grounding check, F1 0.366.
2. (60 s) The results page: one brief, check off then on, claims struck in red; the two numbers.
3. (90 s) Otari's dashboard: Activity showing both models, the routing policy and a fallback, the sandbox call, the budget, the guardrail.
4. (30 s) "This week" mode on live headlines.
5. (20 s) The first Otari commit on the branch.

## 9. Jannet's check

Answer in your own words before sign-off:
1. Why are there two test sets for sentiment, and which one compares with 2024?
2. Who decides whether a claim stays: the checker model or the code? What three things must be true?
3. What does the sandbox recompute, and why not let the writer do the arithmetic?
4. Which six Otari features do we use, and where does each show up?
5. What happens if the $1.50 cap is hit halfway?
6. What is built, and what is only planned?

- **Jannet's answers (11-12):** right on who decides and the three conditions (2) and on the six features and where each shows up (4).
- Gaps found and how they were fixed:
  - (1) The two test sets are both from the same 349 headlines. The first is the rebuilt 2024 test split (about 53 rows), and it is the one that compares with 0.366. The second is all 349 rows, reported on its own because the 2024 models trained on 70% of them.
  - (3) The writer doesn't do the arithmetic because a language model can state a wrong or invented number confidently. The sandbox runs real code on the price rows, so the figure doesn't depend on any model being right, and a claim whose number differs is removed.
  - (5) A cap isn't a warning. Otari refuses every further request on that key. Our run stops, the page shows which weeks are missing, and nothing is marked complete.
  - (6) Built: only the 2024 notebook and its data. Everything in sections 4 and 5 is planned until the build session makes it.
- **Signed off:** Jannet, 11-12 ("u can start the build session yourself"), with the four gaps above explained back to her in chat.

## 10. The build prompt

> Build Countersign from `hackathons/countersign/design.md`. Read that brief and `hackathons/lessons.md` first. Work on branch `otari-hackathon`; put the code in `Stock_Market_Sentiment_Analysis_NLP/countersign/`. The first commit that adds Otari must be its own commit, and tell me its link. Every model call goes through otari.ai (`https://api.otari.ai/api/v1`, key in `OTARI_API_KEY`, asked for through the credential form, never in chat). Models describe and code decides: a claim is kept only if the checker model says supported, its cited headline ids exist, and its numbers match the sandbox's recomputation. Validate every model reply. Report weighted F1 on the 2024 split (`random_state=42`, 70/15/15, stratified) and on all 349 rows, and the claims written and removed for all 18 weeks. Meet every acceptance condition in section 7. Spend at most $1.50 of Otari credit and never add funds. Deadline: submitted by 08:30 IST on Nov 12; hard close 10:29 IST. Keep the chat log raw from this message on. Give me the DoraHacks form answers and the written Otari feedback in chat, not in the repo.
