# Design brief: SMT Receipts, reasoning lanes (SERV Hackathon 02)

**Process (Jannet, 11-08):** a discussion session wrote this brief on 11-12 (https://claude.ai/code/session_016VDQomosrndnmEPAEdiezY). Jannet reads it, explains it back, and signs it off. Then a **separate build session** starts from the build prompt in section 10. Tracking issue: [#110](https://github.com/JannetEkka/DSProjects/issues/110). Checked against [../lessons.md](../lessons.md).

## 0. The hackathon, in one screen

- **What:** [SERV Hackathon 02](https://openserv.ai/hackathon-2) by OpenServ. Online, solo is fine.
- **Deadline:** **Nov 16, 05:29 IST** (Nov 15, 23:59 UTC). Our own target is everything in by **Nov 15, 22:00 IST**, because the Catalyst build takes Nov 15, 09:00–17:00 IST.
- **What the rules force:**
  - SERV Reasoning must be part of the build.
  - An existing project is allowed with "a meaningful feature" added; the write-up must say what was built during the hackathon and how SERV Reasoning powers it.
  - Deliverables: a public repo, a demo link or video (no length given), a short write-up (what it does, how it uses SERV Reasoning, which track), and a post on X whose link goes in [the form](https://openserv.typeform.com/submissions02).
- **Track:** Open. Kite needs real USDC, Dolphin needs a coupon code we don't have, and Reppo gives only 10 free evaluations.
- **Judging:** "creativity, user readiness and revenue potential". No weights published.
- **Prizes:** $5,000 across 2 track winners, best overall build and a special mention. The split isn't published.
- **Money:** none of ours.
  - OpenServ gave **$1.00 of free credit on sign-up, with no card** (Jannet, 11-12). Buying more needs a card, so we never do; see [../cards.md](../cards.md).
  - The build stops itself at **$0.80** of SERV spend.
  - The raw lane runs on a Google AI Studio free-tier key (no billing).
  - Monad testnet gas is faucet MON, already in the keeper's wallet.

## 1. The idea

**One sentence:** anyone deciding whether to pay for a reasoning layer on a trading agent can watch the same model make the same hourly calls with and without SERV Reasoning, sealed on chain before the market moves and graded by signed prices, so the answer is a record nobody can edit instead of a vendor's chart.

- **The existing project:** [SMT Receipts](https://github.com/JannetEkka/monad-hack) (Monad Metropolis, Oct 2026). A contract on Monad testnet seals SMT's hourly calls on 8 coins and grades each one 4 hours later against RedStone-signed prices, net of a 12 bp fee. `registerAgent` is open to any address. The keeper sealed batch 443 on 11-12, so it's alive.
- **The feature built in the hackathon:** two new agents ("lanes") on that same contract.
  - **Raw lane:** a small model, called directly at its provider.
  - **SERV lane:** the same model, same prompt, same market snapshot, called through SERV Reasoning.
  - Plus a backtest of both lanes on the last 14 days, and a "Lanes" tab on the live page.
- **Why it's not the obvious use (lessons 1):** the obvious use is to put SERV inside an agent and say it got better. We point SERV at a referee instead. OpenServ's own headline chart is a "DeFi trade-decision benchmark" with and without SERV ([docs](https://docs.openserv.ai/serv-reasoning)); we run that test forward in public, where neither they nor we can pick the results.
- **Closest projects (lessons 0, searched 11-12):**
  - [Alpha Arena (nof1)](https://nof1.ai): different LLMs trading real money live. Nothing is sealed before the move, and there's no reasoning-on/off pair.
  - [Foresight Arena](https://arxiv.org/pdf/2605.00420): on-chain commit-reveal for LLM forecasters on Polymarket. The mechanism is close, but it doesn't isolate a reasoning layer.
  - What ours does differently: one model, with and without the layer, sealed and graded on chain.
- **Ideas we didn't pick:**
  - Recourse + an appeal letter on SERV: no close match found, but weak on revenue potential.
  - "Ask SMT why" with checked claims: a [lablab entry](https://lablab.ai/u/@NilayMastaadmi) already does it.
  - A SERV Judge between SMT's personas: that is [TradingAgents](https://github.com/TauricResearch/TradingAgents).
  - A Chithi reply drafter: Mail Assistant, EasyMail AI and GST Reply AI exist.
- **Revenue potential (proposed, not built):** agent builders and signal sellers pay to register a lane and get a track record they can't curate; model and middleware vendors pay for a public A/B of their product. Nothing is charged in this build.

## 2. The measured comparison (decide before building)

**The same task, with and without SERV:** each hour, both lanes get one identical snapshot and must answer LONG, SHORT or WAIT for each of 8 coins, with a conviction and a one-sentence reason, as JSON.

- **Backtest (gives a result on day 1):** the last 14 days of hourly candles, one decision every 4 hours so windows don't overlap: 84 decision points × 8 coins = 672 calls per lane. Graded by the contract's own rule in code: entry at the decision hour, exit 4 hours later, minus 12 bp. The period is after the model's training cutoff, so it can't have memorised it; the build confirms the cutoff and says so.
- **Live lanes (the proof):** both lanes sealed hourly on Monad testnet from the first working deploy until the deadline, graded by the contract with RedStone prices.
- **Numbers reported per lane:**
  1. Hit rate net of fees on LONG/SHORT calls, with a 95% interval.
  2. How often it waits.
  3. **Invalid answers** (not valid JSON, missing coin, value outside the allowed set). One attempt per call, no retry, so the failure is counted. OpenServ claims "parse failures disappear".
  4. **Cost per call** from the usage each API returns, at each provider's list price. The raw lane runs on a free tier, so its cost is what the same tokens would cost at Google's list price, and we say that.
  5. Latency.
- **Baselines shown beside them:** always-LONG over the same windows (the market itself), and SMT's committee record from the same contract.
- **A good result:** any measured difference on failures, cost or hit rate, in either direction.
- **What we say if it isn't good:** the truth. The 8 coins move together, so 672 calls are far fewer independent bets, and 2–3 live days are fewer still. If the hit-rate intervals overlap, the write-up says "no detectable difference in direction on this sample" and leads with failures and cost. If SERV does worse, we publish that. We never claim an edge the interval doesn't support (impact rule).

## 3. What a judge sees in the first 10 seconds

- **The screen:** the live SMT Receipts page, "Lanes" tab. Two columns side by side, Raw and SERV, the same model name on both. Under each: hit rate, waits, invalid answers, cost per call. Below, the latest hour as two rows of 8 coin chips (LONG green, SHORT red, WAIT grey), each chip turning to a tick or a cross when graded, with a link to its transaction.
- **Headline (6 words):** "Same model. Sealed calls. Two lanes."
- **Look:** the existing SMT Receipts style (a ledger; it already has its brand). One accent colour marks the SERV lane and nothing else. Motion: chips seal with a stamp, then flip when graded.
- **Backtest strip** under the columns, labelled "backtest, not on chain", so nobody mistakes it for sealed calls.

## 4. Architecture

```
public hourly candles ──► snapshot builder (code) ──► one snapshot JSON, hashed
                                   │
                 ┌─────────────────┴──────────────────┐
                 ▼                                    ▼
        RAW lane: model at Google           SERV lane: same model via
        (AI Studio free key)                inference-api.openserv.ai
                 │      same system prompt, same user message      │
                 └─────────────────┬──────────────────┘
                                   ▼
                  validator (code): schema, allowed values
                  invalid ► all 8 coins WAIT, counted as a failure
                                   ▼
        keeper (GitHub Actions, hourly) ── seal() ──► SMTReceipts on Monad testnet
                                   ▼                         │ 4 h later
        usage ledger (tokens, cost, latency, failures)   grade() with RedStone prices
                                   ▼                         ▼
                      web page "Lanes" tab ◄── Envio indexer / contract reads
```

- **Model judgment (the only model decisions):** for each coin, the direction, a conviction, and a one-sentence reason.
- **Fixed rules (code or contract):**
  - What goes in the snapshot, and that both lanes get the same bytes.
  - Whether an answer is valid. An invalid answer becomes 8 WAITs and a counted failure; the code never repairs or re-asks.
  - Sealing, the entry and exit prices, the fee and the grade. These are the existing contract, unchanged.
  - The spend cap.
  - Why: "let the model describe, let deterministic code decide" (lessons 4). The model can't grade itself or touch the record.
- **Agents:** two, with the same role, on purpose: this is a controlled A/B, so they must not act on each other (lessons 7 doesn't apply, and we say so if asked).
- **The model:** `gemini-3.1-flash-lite`. It's in SERV's catalog at $0.30 / $1.80 per million tokens, and AI Studio serves it on a free tier. If the free tier doesn't offer it, fall back to `gemini-2.5-flash` on both lanes.
- **Why the raw lane goes to Google directly:** SERV's Playground has a Raw mode, but the API docs show no switch for it. The build asks on OpenServ's Discord once; if a raw flag exists, the raw lane may use it and the brief is updated.
- **Hosting and cost, all free:**
  - Lanes and keeper: GitHub Actions in the public `monad-hack` repo (free minutes), inside the existing keeper workflow.
  - Chain: Monad testnet. Lane wallets are derived from the keeper's one key (labels `smt-receipts/lane-raw`, `smt-receipts/lane-serv`), the way the positions agent already is, and the keeper tops them up.
  - Page: GitHub Pages. Indexer: Envio's free tier (already running).
  - SERV: the $1.00 credit. Estimate, not measured: about $0.002 a call, so 84 backtest calls plus about 60 live hours is about $0.30.
  - Ledger: a JSON file on the repo's `archive` branch, like the batch archive.

## 5. The flow, step by step

1. At :17 each hour the keeper runs (existing).
2. The snapshot builder fetches the last 48 hourly candles for the 8 coins and writes one JSON: prices, 1h/4h/24h changes, volume. It hashes it.
3. The same system prompt and the same snapshot go to the raw lane and to the SERV lane, once each, with the same temperature and output limit.
4. The validator checks each answer: valid JSON, all 8 coins, direction in {LONG, SHORT, WAIT}, conviction 0–100, a reason under 200 characters.
5. A valid answer is sealed as that lane's batch. An invalid one, a timeout or an API error is sealed as 8 WAITs with the reason "invalid answer" and counted. If the snapshot itself can't be built, nothing is sealed for either lane that hour, so the lanes always have the same hours.
6. The ledger gets one row per call: tokens, cost, latency, valid or not, snapshot hash.
7. Before each SERV call the code adds up the ledger. At **$0.80** it stops calling SERV, and it stops the raw lane with it, so the pair stays matched. The page then says "lanes paused: credit cap reached".
8. Four hours later the keeper grades both batches with the RedStone-signed prices (existing).
9. The page reads the scoreboard and the ledger. It shows a number only when its count is above zero, and shows "n = …" beside every rate.
10. The backtest runs the same steps 2–6 over 84 past decision points, grades in code with the contract's rule, and writes one results file the page reads.

## 6. Decisions settled now

- **One attempt per call, no retries.** A retry would hide the failures we're measuring.
- **Both lanes or neither** each hour.
- **Fee:** 12 bp for both lanes, the same as SMT's.
- **Candle source:** Binance's public market-data endpoint (`data-api.binance.vision`). GitHub's runners are in the US, where Binance's main API is blocked, so the build's first step is to prove this from Actions; if it fails, use another keyless public source (OKX, then Coinbase) and record which.
- **The contract isn't changed or redeployed.**
- **The repo:** the work goes into `JannetEkka/monad-hack` by PRs dated Nov 13–15, so "built during the hackathon" is visible in the history. No submission text goes in that repo.
- **SMT's own tabs stay as they are,** including the net-negative record.
- **Keys Jannet creates** (never pasted in chat):
  1. **SERV key.** [console.openserv.ai](https://console.openserv.ai) → API Keys → Create secret key → name `serv02-hackathon`. Save it in two places under the name **`SERV_API_KEY`**: this cloud environment's secrets (for the backtest), and on GitHub at `monad-hack` → Settings → Environments → `monad-testnet` → Add environment secret (for the live lanes). Don't open Billing.
  2. **Gemini key.** [aistudio.google.com](https://aistudio.google.com) → Get API key → Create API key → **in a new project** named `serv02` (no billing account attached). Save it in the same two places as **`SERV02_GEMINI_API_KEY`**.
  3. **The $5 ask** on OpenServ's [Discord](https://discord.com/invite/9u724WsWCU) or [Telegram](https://t.me/openservai), as insurance. If it arrives, the cap can rise to $4 with Jannet's say-so.

## 7. Acceptance conditions

- [ ] A script proves both lanes received byte-identical prompts (the same hash in both ledger rows) for every sealed hour.
- [ ] A test feeds the validator broken answers (not JSON, 7 coins, "BUY", conviction 140) and each becomes 8 WAITs and one counted failure.
- [ ] A test shows the cap: with the ledger at $0.80, no SERV request is sent and no raw request either.
- [ ] The backtest's grading function gives the same result as the contract on at least 20 already-graded SMT batches.
- [ ] Both lane agents are registered on the existing contract, and at least 12 hourly batches per lane are sealed and at least 8 graded before the video is recorded.
- [ ] The backtest results file exists with all five numbers per lane, intervals included, and the always-LONG baseline.
- [ ] The page's Lanes tab shows the 6-word headline, both columns on the first screen at 1366×768, one accent colour used only for SERV, the stamp and flip motion, and "n =" beside every rate.
- [ ] The README says what was built Nov 13–15, how SERV Reasoning is used, the measured numbers with their sample sizes, the closest projects and how this differs, and what isn't shown (small sample, correlated coins, testnet).
- [ ] Total SERV spend in the console is under $1.00, and the ledger's total is within 20% of it. If the gap is bigger, the cap is recalculated from the console's cost per call.
- [ ] Existing tests and the keeper's SMT tracks still pass and still seal.

## 8. Demo plan

- **Length:** no limit in the rules; ours is under 2 minutes, captioned.
- **Storyboard:**
  1. (10 s) The claim: OpenServ's chart, "same model, better decisions". "We tested it where nobody can edit the answer."
  2. (25 s) The Lanes tab live: the same model name twice, the latest hour sealing, one chip opened to its Monad transaction.
  3. (25 s) A graded hour: chips flip; the contract checked the signed prices.
  4. (30 s) The numbers: backtest strip, then the live scoreboard, each with n, said plainly, including what isn't significant.
  5. (15 s) What it's for: any agent can register a lane. Where SMT started: OpenServ's 2024 hackathon.
- **Live vs replayed:** the page and transactions are live; the stamp and flip can be replayed from real batches for timing.
- **UI step:** 2–3 directions for the Lanes tab on a Claude Design canvas before any UI code; Jannet picks one.
- **X post (Jannet posts it; numbers filled only from our run):**

  > In 2024 I won Best DeFi Application at OpenServ's hackathon. For SERV Hackathon 02 I pointed SERV Reasoning at my own referee.
  >
  > One model makes hourly calls on 8 coins, once raw and once through SERV. Both are sealed on Monad before the market moves and graded by signed prices 4 hours later.
  >
  > [N] calls so far: [raw hit rate] vs [SERV hit rate] net of fees, [raw invalid] vs [SERV invalid] invalid answers, [raw cost] vs [SERV cost] per call. [One plain line on whether the gap is bigger than the noise.]
  >
  > Live: [page link] · Code: [repo link] @openservai

## 9. Jannet's check

Answer in your own words before sign-off:
1. What do the two lanes have in common, and what is the one thing that differs?
2. Who decides whether a call was right: the model, our code, or something else? Why does that matter?
3. What happens when a model returns a broken answer, and why don't we just ask again?
4. Why is there a backtest as well as the live lanes? Which one is on chain?
5. What happens when SERV spend reaches $0.80?
6. If the two hit rates come out nearly the same, what do we say?
7. What is built today, and what is only planned?

- Jannet's answers:
- Gaps found and how they were fixed:
- **Signed off:** _(Jannet, date)_

## 10. The build prompt

> Build "reasoning lanes" for SMT Receipts from `hackathons/serv02/design.md` in `JannetEkka/DSProjects`. Read that brief, `hackathons/lessons.md` and the rules in `hackathons/october-2026.md` first. The code goes in `JannetEkka/monad-hack` (attach it), on a branch, through PRs for me; never push to main, never change or redeploy the contract, never run anything that deletes the keeper's state, and put no submission text in that repo. Tracking issue: DSProjects#110; tick its checklist and comment at each milestone.
>
> Two lanes get the same hourly snapshot and the same prompt: a raw lane (`gemini-3.1-flash-lite` at Google, key in `SERV02_GEMINI_API_KEY`) and a SERV lane (the same model at `https://inference-api.openserv.ai/v1`, key in `SERV_API_KEY`, a system prompt on every request). If a key is missing, ask me through the credential form, never in chat. The model only chooses LONG, SHORT or WAIT, a conviction and a reason per coin. Code decides everything else: the snapshot, validation (an invalid answer becomes 8 WAITs and a counted failure, with one attempt and no retry), both lanes or neither each hour, sealing through the existing keeper with wallets derived from the keeper key, and a hard stop at $0.80 of SERV spend from a usage ledger. No card and no credit purchase anywhere.
>
> Order of work: (1) prove from GitHub Actions that the candle source works; (2) the snapshot builder, lane callers, validator and ledger with tests, checking SERV's real cost per call on 3 calls against the console before anything bigger; (3) the 14-day backtest (84 decision points, graded by the contract's rule, 95% intervals, always-LONG baseline); (4) register both lanes and start sealing hourly, because live hours can't be made up later; (5) the Lanes tab, after I pick one of 2–3 directions on a Claude Design canvas; (6) the README and the video storyboard. Meet every acceptance condition in section 7 and tell me which ones fail. Report numbers as measured, with n, and say plainly when a difference is inside the noise. Deadline: everything ready for me to submit by Nov 15, 22:00 IST.
