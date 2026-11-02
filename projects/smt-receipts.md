# SMT Receipts: an AI trading bot's calls, sealed on Monad and graded by signed prices

**Monad Metropolis, Onchain Finance & Trading track.** Built Oct 6–14, 2026, submitted Oct 14. The keeper is still running (archive batch 325 on Nov 1).
**Live:** [jannetekka.github.io/monad-hack](https://jannetekka.github.io/monad-hack/) · **Code:** [github.com/JannetEkka/monad-hack](https://github.com/JannetEkka/monad-hack) (MIT) · contract `0xDF9f42AE4f81F086F8495c5a5339dDaa90057993` on Monad testnet (chain 10143) · demo 1:48 [youtu.be/7IpMa2UPJPk](https://youtu.be/7IpMa2UPJPk) · pitch 1:51 [youtu.be/KYqEICJNxeA](https://youtu.be/KYqEICJNxeA)

## The 30-second version

Anyone selling trading calls can delete the ones that lost, and a bot that reports its own win rate is marking its own exam. SMT Receipts writes every hourly call from my trading agent (SMT) to a contract on Monad *before* the market moves: all 8 coins, WAITs included. It then grades each call against RedStone oracle prices signed at an exact second, net of a 12 bp fee SMT declared once and can't change. The contract has no owner, no admin key and no upgrade path, so nobody can edit a receipt, including me.

The record it built is not flattering, and that's the point. Live numbers from the Envio indexer on **Nov 1, 2026**: the committee agent has sealed 227 batches with 88 LONG/SHORT calls and 1,728 WAITs. 75 calls were graded and **26 were hits** net of fees, and 11 expired as misses. The live-positions agent has 49 graded calls, **18 hits**. Both are net negative after fees (sum of net moves −254,776 ppm and −170,014 ppm). A track record you can't curate shows exactly this.

## 1. Architectural reasoning

### Database / storage
- **The contract is the system of record** (`SMTReceipts.sol`, Solidity 0.8.28). Why a blockchain here and not Postgres: the product *is* the guarantee that nobody, including the operator, can edit history. A database I control can't make that promise to a stranger.
- Storage is designed for gas: `seal()` packs each coin's direction and conviction into one 256-bit word (2 bits per feed for direction), uses one storage slot per batch, and keeps the batch's block number so a reader never scans a log range.
- **Envio HyperIndex** (V3) turns the events (`AgentRegistered`, `Sealed`, `Graded`, `Expired`) into four GraphQL entities: Agent, Batch, Receipt, PairStat. Why an indexer: a page reading every receipt straight from RPC is slow, and Envio's free hosted tier does the aggregation. **The page falls back to reading the contract directly** if Envio is down, and the header says which source it used.
- **Archive branch in git:** the keeper commits the exact snapshot bytes for every seal to an `archive` branch (277 commits by Nov 1), so anyone can recompute the hashes that went on chain.

### Compute & hosting
- **Why Monad:** a receipt only means something if *every* call gets one, including the dull WAITs, every hour. That's 8 calls per seal and 24 seals a day, plus grading transactions carrying a dozen signed price packages. Measured gas: `seal` with 8 pairs is 95,545; `grade` is 113,772 / 174,662 / 236,118 for 1/2/3 pairs. A seal cost about 0.015 testnet MON and landed in seconds. If every receipt cost real money you'd only seal the calls you liked, which brings back the original problem.
- **The keeper runs on GitHub Actions**, not a VM: free minutes on a public repo, the secret lives in a GitHub environment, and every run's log is public. The page is static on GitHub Pages.
- **Deployed through the canonical CREATE2 proxy**, so the address is derived from the code itself: anyone can check the deployed bytecode is the published one.

### Frameworks & libraries
- **Hardhat + ethers v6 + Node 22** for the contract, keeper and tests.
- **RedStone over Pyth or Chainlink, decided by checking the free options:** Pyth's Hermes had needed a paid API key since Aug 26, and Chainlink on Monad testnet had only BTC and ETH. RedStone's public gateway serves all 8 coins with 5 signers each, needs no key, and keeps about 24 hours of signed history at 10-second ticks. Of 60 random ticks over 20 hours, all 60 had every coin with at least 3 valid signatures.
- **I wrote a small RedStone payload verifier (MIT)** instead of inheriting RedStone's base contract. Theirs is BUSL-licensed and reads one payload from the end of calldata. Mine takes payloads as normal arguments, so one `grade()` transaction checks both the entry and the exit timestamp.

## 2. Data & security pipelines

### Authentication & access control
- **One publisher address per agent.** `registerAgent(name, source, feeBps, feeds)` binds an agent to the address that registered it, and only that address can seal for it. The fee (12 bp) is fixed at registration.
- **Anyone can grade or expire.** Grading needs no trust because the contract verifies the prices itself: it recovers each package's signer, accepts only RedStone's five `redstone-primary-prod` signers, needs 3 distinct signers per coin, takes the median, and requires every package to carry *exactly* the entry or exit timestamp.
- **One secret:** the keeper's private key exists only as a GitHub environment secret (`monad-testnet`). The positions agent signs with a key derived from it (`keccak256(key ‖ "smt-receipts/positions")`), and the keeper tops that wallet up (`[FUND]`, the first transaction of a pass because of Monad's reserve-balance rule).
- Without the secret, a run is a dry run: it builds every transaction and sends none, with a visible warning.

### Data ingestion & flows
- **Scheduled pull, hourly:** keeper reads SMT World's public `decisions.json` → `seal()` → entry price = first RedStone tick strictly after the seal block → exit = entry + 4 h → the keeper fetches the two signed packages → `grade()` → Envio indexes the events → the page reads Envio.
- **What the contract refuses:** a snapshot older than 3 hours (`StaleSource`), one already sealed or out of order, and one missing a coin (`LengthMismatch`, so no cherry-picking). A batch not graded within 22 hours can be expired by anyone, and its LONG/SHORT calls count as misses that paid the fee. Letting a bad call lapse never helps the bot.
- The 22-hour window comes from RedStone's ~24 hours of history.

### Privacy & compliance
- **Data minimisation for the second agent:** the keeper reads `live.open[]` from SMT World's `account.json` and keeps seven fields per position: pair, side, entry, opened_at, setup_name, lane, leverage. No size, equity, mark price or PnL leaves the file, and `paper.open` is never read. A test runs the snapshot over an account fixture whose private fields hold sentinel values that must never come out.
- Testnet only. The keeper wallet only ever held free MON from QuickNode's faucet.
- Everything on chain is public by design. SMT's parameters, research and PnL stay private.

## 3. Reliability & failure operations

### State management
- **The chain holds all state.** The keeper is stateless: each pass reads what's on chain, then deploys if the address is empty, registers if needed, seals the newest snapshot, grades every batch past its horizon and expires anything past the window. A crashed run loses nothing, and the next pass picks up from the chain.
- Each snapshot can be sealed at most once and in order (`lastSourceTs`), so a retried pass can't double-seal.
- The positions agent seals once per horizon, so no two receipts grade the same move, and at once when a position opens or closes.

### Error handling & fallbacks
- **GitHub's cron was the failure (10-13):** after the merge, the hourly cron fired **once in 8 hours** (18:12 manual, then 00:37 scheduled, none at 18:17–23:17). "A track record with 1 seal in 8 hours is not the product." The fix: one run works at :17 every hour for about 5.5 hours, then dispatches its own successor with `gh workflow run`. The cron, now every 3 hours, only restarts the chain if it breaks, and a concurrency group keeps it to one run at a time.
- A keeper pass that ends in `[ERROR]` raises a workflow warning, and the loop continues to the next hour. An archive push failure is retried on the next pass.
- **Gas:** Monad charges the gas *limit*, so the keeper sets each limit to the estimate + 20%.
- **The page has two data paths** (Envio → contract) and says which one it's on.
- **Envio failures (10-17 to 10-28):** deployment `76591f5` stalled at block 71,941,997 on 10-17 and synced slower than the chain grew. On 10-21 I moved the page to deployment `eb5fcaa`, which was at the chain head over HyperSync, after checking its Agent counters against the contract's own `stats()` for both agents. Separately, Envio Cloud shuts down an indexer idle for 7 days, and nothing queried it because the page could read the chain. A workflow now pings it every 6 hours (29 green runs by 10-28). The 10-28 shutdown email turned out to be for the stalled old deployment, exactly 7 days after the ping moved off it.

### Logging & observability
- One tagged line per keeper action: `[DEPLOY] [REGISTER] [FUND] [SEAL] [GRADE] [EXPIRE] [BUDGET] [ERROR]`, visible in each run's job summary.
- The explorers (MonadVision, Monadscan, Socialscan) put a bot check in front of scripted browsers, so **the page decodes the seal and grade transactions itself** from Monad's RPC: block, sender, gas, and the decoded event.
- A skipped hour shows up as a visible gap on the page. It's a feature: missing data is never hidden.

## 4. Evaluation & optimisation metrics

### Performance benchmarking
- **Tests:** 18 contract tests, including real RedStone signatures verified inside the contract, a real SMT World snapshot and the sentinel-field privacy test. An end-to-end rehearsal (`npm run e2e`) runs a local chain 6 hours behind real time with Monad's chain id, uses the real keeper for both agents, and grades against RedStone's real history. CI runs it on every PR. The Envio handlers have Vitest tests.
- **Grades cross-checked against an independent source:** a BTC grade of +4.0 bp sat inside Binance's 1-minute range of +2.6 to +13.0 bp; LTC came within about 2 bp. The first committee call graded (SOL SHORT at 51%) lost 105.6 bp after fees: RedStone showed +93.6 bp, and Binance candles showed SOL up ~71–98 bp between the same minutes, so the miss is real.
- **The record itself** (Envio, Nov 1): committee 26 hits of 75 graded plus 11 expired; positions 18 of 49. There's no "better than the traditional way" percentage to claim here. The measurable improvement is that *every* call is on the record, including 1,728 WAITs, against a signal group that deletes its losers.

### Cost & resource efficiency
- ₹0: GitHub Actions minutes (public repo), GitHub Pages, Envio's free hosted tier, RedStone's keyless gateway, and faucet MON.
- Gas design: 2-bit packed directions, one slot per batch, both timestamps verified in one transaction.

### System constraints
- RedStone's public history is ~24 hours, which caps the grading window at 22 hours; anything ungraded expires.
- The keeper chooses *when* to seal and which 3 of 5 signers to submit. It always takes the three lowest-index valid ones, and another choice moves the median by well under 1 bp against a 12 bp fee.
- Agent 1 grades SMT's committee calls, which SMT itself labels advisory. Agent 2 says whether price moved the held way over 4 hours, not what the trade made.
- GitHub Actions jobs time out at 6 hours, hence the 5.5-hour self-dispatch loop.

## What the history shows (real decisions)
- Oct 6: the whole first version (contract, keeper, indexer, page, 16 tests) as one PR; main was started on Oct 12 and PR #1 merged that night.
- Oct 12: the deck reads the scoreboard from the live contract; the pitch narration is Kokoro TTS (local open weights) because edge-tts started returning 403.
- Oct 13: PR #2 replaced the cron with the self-dispatching keeper. PR #3 added the second agent, because "the committee calls in decisions.json are advisory; SMT's trades are the positions." PR #4 rebuilt all media from the live chain after the first grades landed.
- Oct 21: PRs #6/#7 handled the Envio idle shutdown and the stalled deployment.

## Weak spots to own before they ask
- The hit rate is low and both records are net negative after fees. I'd say that first: the receipts are honest about the bot, and the bot needs work (see SMT's own write-up).
- Testnet only, and the keeper is a single GitHub workflow, a single point of failure for *when* things get sealed, though not for what they say.
- Claude Code was the coding assistant; the private notes on the submission say so. I designed the product and its trust rules, and reviewed and merged every PR.

## Sources
`README.md`, `contracts/SMTReceipts.sol` (Stats struct), `.github/workflows/keeper.yml`; main-branch history (PRs #1–#7, Oct 6–21) and the `archive` branch (277 commits, latest batch 325 on Nov 1); [DSProjects#26](https://github.com/JannetEkka/DSProjects/issues/26) (final form text 10-12/13; Envio comments 10-28); live Envio GraphQL query of 2026-11-01 for the Agent counters.
