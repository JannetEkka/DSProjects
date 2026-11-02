# Smart Money Trading (SMT): an explainable AI trading agent, run in production on ₹0

**Founder and sole engineer, Jan 2024 – present** (JTech Solutions, pre-incorporation). Patent pending: Indian provisional application No. 202631090789 (filed 2026-07-26). Runs 24/7 and places real orders on WEEX's exchange-granted **simulated** account (~$10K, sandbox funds, not income).
**Live:** SMT World [smt-weex-trading-bot.jannet-ekka.workers.dev](https://smt-weex-trading-bot.jannet-ekka.workers.dev/) · **Code:** core repo `JannetEkka/smt-weex-trading-bot` (private); public explanatory layer [github.com/JannetEkka/smt-apac](https://github.com/JannetEkka/smt-apac) · [WEEX feature](https://www.weex.com/news/detail/how-smart-money-tracker-survived-live-ai-trading-at-weex-ai-hackathon-343641)

**Measured today (2026-11-01, from the repo):** ~87,500 lines of Python outside tests (~140,000 with tests), **3,152 test functions**, **362 merged pull requests** (GitHub search), **673 findings** in `docs/FINDINGS.md`. The résumé's "91,000 lines / 3,000+ tests / 344 PRs / 611 findings" are older snapshots, so quote today's numbers or say "over".

## The 30-second version

SMT trades 8 crypto perpetual-futures pairs and has to prove why it traded. It began as six specialist "persona" agents voting into a learned Judge. **Graded on independent Binance prices, the committee had no directional skill** (F-505, 09-23: JUDGE −6.8pp skill at 4h on n=99; every persona within ±4pp of zero once market direction is removed). So I rebuilt it: **written rules with replayed records open every trade** (today two live setups: `capitulation_crash24` and `slow_trend`), the personas became **advisors graded on every call**, a setup goes live only after **30 paper closes with net > 0** (the ladder), and every explanation passes a **counterfactual check**: flip the advisor's input, re-run the decision, and drop the reason if nothing changes. The LLM is a sensor, never the decider.

What I'd lead with in an FDE interview isn't the trading. It's production operations on no budget: moving a live system off GCP in two days when billing closed, finding a bug that rejected **1,137 live orders over three months** while every test passed, and a rule that **a fallback must never be silent**.

**Honest status, from the README:** "Not profitable yet, and we say so in numbers." No lane has a measured positive net edge on the graded era; SMT Receipts on Monad shows the same (see that write-up).

## 1. Architectural reasoning

### Database / storage
- **Experience records are append-only JSONL** (`v4/rl_training_data/exp_*.jsonl`), one record per decision with every vote, weight and gate verdict. Why JSONL: the daemon must never block on a DB, records are immutable facts, and replays and audits read them as files. The cost showed up as the freeze below (loading all 189 files, 785 MB, to keep 400 rows).
- **Analytics:** BigQuery (`smt_lake`: market truth, decision lake, news) until GCP closed on 10-02. **Replaced by DuckDB in-process** (`scripts/sql.py`) over the weekly refit's Parquet artifact (`market`, 456,632 rows) and the JSONL logs: no server, ₹0, same SQL.
- **Ground truth is a dataset the bot never wrote to:** Binance's public archive (`data.binance.vision`). The standing rule: "our own logs are not evidence about the market."
- **Positions:** an in-memory tracker with JSON persistence plus a 15-minute sync against WEEX's `allPosition`. The exchange is the source of truth, and the tracker reconciles to it (see F-668 for when that went wrong).
- **Git as transport:** the box pushes logs and SMT World's public feed (`account.json`, `decisions.json`) hourly. Machines write branches: `refit-output` (new parameters the box installs), `vm-state` (an hourly snapshot).

### Compute & hosting
- **Before (to 10-02):** GCP: Compute Engine VM + systemd, Cloud Run chat, Cloud Functions (budget pause, cost digest), Secret Manager, Vertex AI, BigQuery.
- **The trigger:** the GCP bill (₹1,099.76) couldn't be paid. Billing was disabled and the billing account closed on 10-02, and the operator constraint became "infrastructure must cost ₹0". A new free trial wasn't possible (the account was already "Paid").
- **After (since 10-03), every piece free:**
  - **Oracle Cloud Always Free `VM.Standard.E2.1.Micro`** (`smt-micro`, 1 GB RAM + 2 GB swap, Singapore) running `smt-daemon.service` under **systemd with memory high/max 568M/669M** and a watchdog. The daemon runs at ~150–170 MiB.
  - **Cloudflare Workers** for SMT World (static site + `/api/chat` on Gemini + `/api/trend`), deployed from `main` by Workers Builds.
  - **GitHub Actions** (private repo, 2,000 free minutes/month): the weekly refit (Mondays, ~16 min), a daily check, a 2-hourly heartbeat that emails when the box stops pushing. ~200–230 min/month.
  - **Google AI Studio free key** for Gemini.
- **Why a VM and not serverless for the daemon:** it's a long-running stateful loop with open positions, timers and in-memory caches. Serverless would mean rebuilding that state every invocation. SMT World *is* serverless, because it's a stateless read of a feed plus a chat call.
- **Merge → auto-deploy:** after the hourly push the box runs `scripts/auto_deploy.sh`. When the running daemon is older than the code on disk it deploys itself, and the deploy **refuses exit 0 until the running process reports the on-disk version**, posting `[AUTODEPLOY] ✅/❌` to Discord.

### Frameworks & libraries
- **No agent framework, deliberately.** "Agent frameworks that let models debate their way to a trade cannot tell you afterwards which argument moved the money." The decision is a deterministic weighted matrix you can replay offline from the record. The LLM (Gemini sentiment) is one bounded input wired so it can only **subtract** confidence.
- pandas, scikit-learn, CatBoost, **Optuna** (the weekly refit), a contextual bandit, and an overfitting gate (**CPCV + Deflated Sharpe + PBO + FDR**) that a refit must pass before its parameters reach the running daemon. Three.js/WebGL for SMT World.
- **A constants registry:** a number that decides something is measured, not chosen. Any un-derivable constant goes in `constants_registry.py`, and a CI test fails if an unregistered one appears on the decision path.

## 2. Data & security pipelines

### Authentication & access control
- **Exchange keys** (WEEX key/secret/passphrase) and 10 other API keys live in `~/.smt.env` on the box, **mode 600**, read by `v4/secrets_loader.py`. The check command (RUNBOOK C47) prints each key's **name, source and length, never the value**. Secret Manager went with GCP.
- **The box pushes to GitHub with a repo deploy key** (write access to that repo only).
- **SMT World founder section** (`/founder`): **two locks, either enough alone.** (1) Cloudflare Zero Trust Access (free plan): a self-hosted application on `/founder`, allow-listed to the operator's email, login by one-time PIN. (2) The Worker **verifies the Access JWT itself**: RS256 against the team's public keys, this app's AUD, the issuer and the expiry. A deleted or mis-scoped Access app still can't leak the feed, and if the variables aren't configured it returns **503, never "open"**. Key refresh on an unknown key id is limited to once a minute, so forged tokens can't become a stream of outbound fetches (found in code review).
- **Data minimisation for the public:** `account.json` is the daemon's **allowlist view**. The full snapshot (`founder/feed.json`) is bundled into the Worker and never a public file (`.assetsignore`). The reason: India has no grace period for a website disclosure before the second provisional is filed.

### Data ingestion & flows
- **Polling, not streaming:** the daemon runs a cycle every ~2 minutes (WEEX klines, funding, order book; Binance public REST; CMC Fear & Greed; Etherscan whale flows; news), decides, logs `[WHY]`, and places or manages orders via WEEX V3 REST.
- **Crons on the box** (all wrapped by `run_measured.py`, which logs memory per job): hourly log push, hourly news poll, the daily condition matrix, liquidations, Fear & Greed, whale flows, a monthly re-audit.
- **Weekly refit** on GitHub Actions → `refit-output` branch → the box installs it (`[REFIT-INSTALL]`).
- **Free data only:** a free tier must cover the need, and a trial isn't free. "Exhaust what we already fetch before adding a source" (e.g. kline responses carry taker-buy volume that was being dropped).

### Privacy & compliance
- No customer data. It trades its own sandbox account.
- The public site shows the allowlist view only; sizes, PnL detail, setup rules and research stay private (patent and moat).
- **Gemini free tier:** 500 requests a day shared between the box and the chat. Sentiment is rationed to 20 a day, and the free tier gets no Search grounding, so every record says `grounded=False`.

## 3. Reliability & failure operations

### State management
- **The migration test:** after two days down, the first boot on Oracle printed `✅ RESTORED 3 position(s) … BTCUSDT#slow, ETHUSDT#slow, LTCUSDT#slow` and `sync_with_weex done: 3 live syms`. Open positions were **re-adopted from the committed feed**, because the hourly git push had preserved the state the VM's disk lost. (Lost with GCP's disk: the bandit, candidates, cooldowns and learned-params caches.)
- **F-668 (10-15 → 10-20), the reconciliation bug:** WEEX answered `allPosition` with a **successful, empty list** for ~30 minutes while holding BTC, LTC and SOL. The sync dropped all three, and they **rode unmanaged for five days**, past their own exits, while `UNTRACKED POSITION(S)` printed 35–89 times a day. A "drop after N empty reads" rule would have needed ≥3 reads, so the fix made the drop **reversible**: `_readopt_dropped` re-adopts the newest dropped record of a (symbol, side) when the venue holds that side beyond the book and no more than the record did. On deploy: `RE-ADOPTED`, then the next cycle `TREND_EXIT`.
- **Emergency flatten** of real positions is a separate script (`v4/close_all_positions.py`), because the settings kill-switch only knows tracker state. F-520 found the old flatten would have removed the stops and then crashed. Fixed.

### Error handling & fallbacks
- **"A fallback must never be silent"** (a standing contract): any `or <default>` on live data needs a WARNING and a liveness flag on the record, so downstream can ask whether a value is real. It was written down after being caught **four times substituting a plausible number for a real one**. The 09-23 audit then found **17 outbound calls that could fail without a word** (F-510), now logged.
- **"Presumed broken until observed working":** reading code isn't evidence, and "no errors" isn't evidence. Every new silent failure gets a numbered liveness proof in `RUNBOOK_REFERENCE.md` saying whether an empty result means healthy or means the writer never ran.
- **Rails refuse, never propose:** a rail can veto a trade ("not here") but never pick a direction, so a filter can't quietly become a seventh opinion. An **un-disableable fee floor**: `est_profit_net > est_fees` is the one check the learner can't turn off.
- **Leverage is bounded by liquidation safety:** a position's stop must sit inside its liquidation distance and survive its own worst historical move. Exposure time caps leverage (a 30-minute scalp 20×, a multi-week hold 5–7×).

### Logging & observability
- **A log grammar** (`python3 -m smt.core.log_grammar --list`): grep patterns come from the source, because "zero hits is not a finding" (wrong pattern vs didn't happen).
- **Discord alerts** (trades, drawdown, `[AUTODEPLOY]`), **GitHub Actions heartbeat** emails when the box stops pushing, a daily check that emails on ✘, `vm_state.txt` memory snapshots, `cron_memory.jsonl`.
- **"A fix is done when the log says so":** every PR body names the log line it changes, with a before/after count, and the next session re-counts it. This rule came from the audit below.

## 4. Evaluation & optimisation metrics

### Performance benchmarking
- **The baseline is always the market itself.** F-488 (09-22): 184 trades joined to the independent archive vs every bar of every pair in the same window (n=6,952). Edge −1.44pp at 24h and −3.27pp at 168h. Direction-correct 47.3% / 45.7%. A "+5.63% if held" result for `slow` was **pure beta** (the tape gave +6.08%), and reporting it without the baseline would have been a fabricated edge.
- **F-505 direction audit** (~38,600 pair-hour calls, 9 weeks): SKILL = hit rate minus the hit rate the same direction would have had at every hour that week. Nothing was above a coin flip, and sentiment at 24h was negative 5 weeks running. That's why the committee was demoted to advisory.
- **Fees as the binding constraint (F-368):** 71 September closes: gross −$105.70, fees $131.61, net −$237.31; fees flipped 14 of 34 gross winners into losses. (Those 71 were paper; see the audit.)
- **The audit that changed how I work (F-515, Sept 1–23):** **98 merges**, and the two defects that decided the month were in the log the whole time.
  1. **`-1140 positionSide must not be null`**: **1,137 live orders rejected** from 06-30 (every lane except bigwick sent `positionSide="BOTH"`, code from 06-05). Fixed 09-23, about 85 merges after the first live flip had shown it.
  2. **The hourly freeze (F-514):** cycle 30 ran a persona-cascade check that parsed all 189 experience files (785 MB, 553,960 records, **4.2 GiB peak, 65 s**) to keep 400 rows, against a 2.5 GiB limit. Stall → stale heartbeat → watchdog SIGKILL, so the daemon was **down ~60% of the time** from 09-13. Twice the watchdog was retuned instead of the cause being found. The fix reads newest files first and stops at n rows: **42 MiB, 0.16 s**, identical records, plus a test that fails on the old code.
- **The fix worked on a real order, and broke the next step (F-518):** on 09-23 WEEX filled 7 real ADA/DOGE entries, a crash on WEEX's stop-loss reply lost them from the tracker, and the bot kept re-buying. Fixed in V6.1.179, positions flattened, and V6.1.180 deployed that evening.

### Cost & resource efficiency
- **₹0 infrastructure since 10-03**, down from a GCP bill of ₹954 over the last 30 days (Compute Engine and Vertex AI the largest lines).
- Gemini: free tier only; every caller writes a usage row; sentiment rationed.
- Memory as a budget: systemd caps, the order-flow recorder under its own 256M cap, `run_measured.py` memory rows per cron.

### System constraints
- **1 GB of RAM** on the free VM is the hard ceiling (the freeze was a memory bug). The refit moved to GitHub Actions for that reason.
- **Sandbox funds:** a $10K simulated account, so results aren't real money, and slippage in shadow is a seed until a live week measures it.
- PnL from logs before 2026-06-30 is invalid (a frozen-mark ledger bug), and any PnL before 2026-08-03 is gross. The docs say so.
- Free data and free models only; WEEX and Binance API availability (Binance returns HTTP 451 in some regions).

## What the history shows (real decisions)
- **Jan 2024 → mid-2026:** v6.0 → v6.1 port (the ADX chop filter was lost in the port and found in an audit, F-183: tuned on 8 pairs, read by nothing).
- **WEEX AI Wars I:** #1 on the preliminary leaderboard of 230+ teams, then one of 37 finalists in live trading. Lost the final, and said so in public (the origin of SMT Receipts).
- **Aug–Sep 2026:** derived exits, risk-constant sizing, per-pair parameters → the September audit (98 merges, two missed defects) → the rule "a fix is done when the log says so".
- **Sep 28 posture:** "stop loving previous designs. The design is a suspect." Setups author trades; personas are frozen as graded advisors; a 30-paper-close ladder to go live.
- **Oct 2–3:** GCP → Oracle/Cloudflare/GitHub Actions in two days, positions re-adopted.
- **Hackathon wrappers** (Mantle, BNB, Solana, Monad) are thin imports of `smt.*`. The brain is never forked and the moat is never public.

## Weak spots to own before they ask
- **It doesn't make money yet**, and the records (receipts, findings) show it. My strongest answer is about measurement and operations, not returns.
- **Built by directing AI coding agents** (Claude Code) and reviewing every merge. The September audit is the honest proof that reviewing merges isn't enough on its own, which is why the "log says so" rule exists.
- Some figures on the résumé are snapshots (see the top). Quote today's.

## Sources
`README.md`, `CLAUDE.md`, `docs/GCP_INVENTORY.md` (₹0 stack + retired GCP), `docs/CODE_AUDIT_2026-09.md` §1, F-514, F-515, `docs/FINDINGS.md` rows F-368, F-488, F-505, F-608, F-668, `docs/ROADMAP.md` (SMT today, operator rules 09-28), `docs/ARCHITECTURE.md`, `docs/content/BLOG_XAI_DRAFT.md`, `smt_world/functions/api/founder.js`; counts: `find … -name '*.py'`, `grep 'def test'`, GitHub search `is:pr is:merged` (362) on 2026-11-01.
