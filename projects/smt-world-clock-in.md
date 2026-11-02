# SMT World: Clock In (native Android app on Solana devnet)

**Solana Mobile "Clock In" hackathon.** Built Oct 7–12, 2026 (6 days), submitted Oct 12 (ref 90FBFC7C). Judging Oct 13 – Nov 9, results Nov 10/11.
**Code:** [github.com/JannetEkka/smt-solana-hack](https://github.com/JannetEkka/smt-solana-hack) · APK on the repo's Releases page · deck `docs/pitch/` · demo video 2:51 (captioned)

## The 30-second version

Once a day you call one coin UP or DOWN for the next 4 hours. Your call and my trading agent's call (SMT) go on Solana devnet **in the same transaction**, signed by your wallet through Mobile Wallet Adapter, and both are graded on real market prices 4 hours later. Neither call can be written after the market moves, so the agent's track record isn't whatever its operator's logs say: anyone can re-check it on Solana Explorer without this app.

It's a native Kotlin / Jetpack Compose app with four tabs (Clock In, My calls, Players, SMT), a leaderboard that needs no server, a streak rebuilt from the chain, notifications, a home-screen widget and a share card. I tested it on my own phone across four releases (v0.1.2 → v0.3.3), and that found and fixed two real bugs: a wallet refusing a saved session, and a "graded" notification that never fired.

## 1. Architectural reasoning

### Database / storage
- **The blockchain is the database for anything that must be trusted.** Each Clock In is an SPL Memo, plain text such as `SMT Clock In v1 | ETH | me UP @ … binance | SMT DOWN 36% WAIT | grade +4h`. History and the streak are rebuilt with `getSignaturesForAddress`, so they survive a reinstall or a new phone.
- **The leaderboard needs no server.** Each Clock In carries a second, tiny memo naming one fixed address, `2Hbn8…ZLVg`, the SHA-256 of "SMT Clock In registry v1", so nobody holds its key. The Players tab reads every player's calls from that address.
- **Why two memos:** Memo v2 rejects an account that didn't sign, and a wallet that rebuilds the transaction drops an unused key. I saw this happen: Solflare added priority-fee instructions to my own Clock In. So the tag is a separate Memo v1 instruction, which doesn't require signers.
- **Local cache** (`Store.kt`, SharedPreferences + JSON) holds grades, notification state and history. It's a cache, not the source of truth. It has a schema version, and when grading rules changed in v0.3.0 the cached grades were dropped once and re-graded.
- Why not a relational DB or a backend: a server would be the one place a call could be edited, and it would cost money to run. The whole idea is that nobody, including me, can change a call after the fact.

### Compute & hosting
- All compute runs on the phone. The only infrastructure is public: the Solana devnet RPC, Binance's public market-data API, CoinGecko, and SMT's public `decisions.json` feed on Cloudflare Workers, which already existed.
- **No backend means ₹0 hosting**, and judges could install the APK and use it without any of my servers being up, apart from SMT's static feed.
- The APK is built by GitHub Actions on every push, which runs the unit tests, builds a release APK signed with a demo key and publishes a SHA256 checksum. `v*` tags attach the APK to a release.

### Frameworks & libraries
- **Native Kotlin + Jetpack Compose**, not a WebView: the rules said *"Direct ports or PWA wrappers will score poorly."* The first build had a WebView tab of SMT World. v0.3.0 replaced it with a native SMT tab because a WebView tab reads as a wrapper, and the web app's own Calls tab made the game appear twice.
- **Mobile Wallet Adapter `clientlib-ktx` 2.0.8** for connect and `signAndSendTransactions`. That was required by the hackathon, and it means the app never holds a private key.
- **The memo transaction is built by hand** (`MemoTransaction.kt`) instead of pulling in a full Solana SDK. A unit test compares its bytes with the same message built by `solders`, the Python bindings of Rust's `solana-sdk` (`docs/golden_memo_message.py`), so the wire format is checked against an independent implementation.
- **WorkManager** for the 9:00 reminder and the grade check, `AppWidgetProvider` for the widget, `FileProvider` for the share card. It doesn't depend on Google Play Services, so the same APK runs on Fire TV / Android TV with D-pad focus rings.

## 2. Data & security pipelines

### Authentication & access control
- **The wallet is the identity.** Connect through MWA, authorize, and the wallet signs. The app stores the MWA auth token so the user isn't asked every time.
- **The real bug here (v0.3.2):** Solflare connected, then answered `-1` (authorization failed) to the saved token from that morning. MWA 2.0.8 reports that as "Failed establishing local association", so my retry never saw "Auth token" and kept retrying the same dead token. The fix reads the wallet's own error code from the cause chain (`-1` = not authorized, `-7` = not on Devnet). If a saved token was in use and the wallet says `-1`, it forgets the token and authorizes afresh in the same tap. Without a saved token, `-1` means the person declined, so it never asks twice. **Both retries happen before signing**, never after.
- **The leaderboard trusts no memo.** Anyone can write a memo to the registry address, so (from the v0.2.0 code review) every call is graded on prices the app fetches itself. A memo whose stated price is more than 2% off the market's is flagged `MEMO-PRICE-MISMATCH` and left off the board. Before that fix, a hand-written `BTC UP @ 0.01` would always have graded RIGHT. SMT's row takes the call most distinct players recorded per coin and hour, with ties counting nothing, so one player can't rewrite SMT's score.

### Data ingestion & flows
- **Clock In:** read the price and SMT's current call → fetch the blockhash *inside* the wallet session, after authorization (a blockhash lives about a minute, so time spent approving can't expire it) → wallet signs and sends → reveal SMT's call and reasons.
- **Grading** is pulled on a schedule: WorkManager runs a check, and so does opening the app. It uses Binance's 1-minute candle at the first minute at or after the call and at the 4-hour mark. If Binance answers HTTP 451 (blocked in some countries), it uses CoinGecko's first point at or after the time, within 65 minutes. **Both ends of a call come from one source**, and the source is stored with the grade.
- **SMT's call** comes from its public `decisions.json` feed. If the feed is more than 6 hours old, SMT isn't scored.

### Privacy & compliance
- **Devnet only, so no real money moves.** The one mainnet touch is a read-only SKR balance for the connected wallet, read at most every 10 minutes. Nothing is ever sent to mainnet.
- On-chain memos are public by design. They hold the coin, direction, price and source, and nothing personal beyond the wallet address.
- The release APK's signing key is committed in `signing/` on purpose, so CI can build an installable APK. The README says it protects nothing, and a store build would get its own private key. Be ready to explain that.

## 3. Reliability & failure operations

### State management
- **The chain is the stable state.** If the app is killed mid-flow, nothing is lost: a call is either on chain or it isn't, and the next refresh rebuilds history from `getSignaturesForAddress`.
- History pages through up to 1,000 of the wallet's transactions (5,000 for the registry) and keeps cached calls older than the last page, so the streak and score never shrink.
- Cache writes share one lock between the screens and the background workers, so a Clock In sent during a slow refresh isn't dropped (found in code review).
- Returning to the app refreshes prices, the feed, history and grades if the last refresh is over 2 minutes old.

### Error handling & fallbacks
- **Wallet hand-off is where it broke on a real phone:**
  - v0.1.3: my first BTC Clock In never reached the chain. Two likely causes: the 90 s approval window ran out while I read Solflare's "unknown site" warning (raised to 180 s), or the wallet missed MWA's 10-second window to connect back while starting (now retried once, before signing).
  - v0.3.1: the retry fired immediately onto a wallet still closing its first screen. It now waits 2 s, and the error card shows MWA's own message and cause chain in a small grey line, so the next screenshot would name the cause.
  - v0.3.2: the dead saved token, described above.
- **Bounded retries:** grading retries a call at most 5 times, only for calls due in the last day, and grades at most 12 per run, so a reinstall doesn't fire hundreds of requests. A throttled payer-lookup chunk on the board is skipped, not fatal.
- **Price fallback:** Binance first, CoinGecko if Binance refuses. Data from the two is never mixed within one grade.
- **SMT sitting out:** in v0.3.0 I noticed my 3 graded calls, re-graded independently on Binance, were all against SMT *sitting out* (WAIT at 24–45% conviction). The app had been grading a lean that SMT itself refused to trade. Now SMT is scored only on real LONG or SHORT calls, and a WAIT shows "SMT sat out (leaning X)".
- **Devices with no wallet** (Fire TV): the wallet features hide themselves instead of erroring.

### Logging & observability
- Named log lines for each failure path: `[WALLET] association failed (...); retrying once`, `[WALLET] the wallet refused the saved session (...); authorizing afresh`, `[BOARD] N Clock Ins on the registry, M players, K payers looked up`, `[REMINDER] graded <coin> <sig> notified`, `[REMINDER] daily nudge scheduled for <next 9:00>`.
- **A silent bug caught from the phone (v0.3.3):** my BTC call came due at 21:05 IST and never notified. The app graded it when I opened it at 21:10, before the background job ran (the phone defers jobs), and only the job posted notifications, for calls *it* had graded. The fix: one notifier posts once per own call graded in the last day, whoever graded it, keyed on the transaction id so the two paths can't post twice.
- **A second silent bug:** the 9:00 reminder drifted to 09:15, ~09:47, ~09:57 and ~11:47 over Oct 9–12, because a 24-hour periodic job counts from its last (deferred) run. It is now a one-time job that schedules the next 9:00 when it runs.

## 4. Evaluation & optimisation metrics

### Performance benchmarking
- **Correctness against an independent implementation:** the transaction bytes match `solders` byte for byte, and devnet accepted the signed transaction in simulation before any phone test.
- **Tests:** 17 → 40 unit tests across v0.1 → v0.3.3 (wire format, memo round trip, streak, grading, feed parsing, leaderboard trust rules, wallet error mapping, reminders), plus one live devnet test that is skipped by default.
- **Real-device testing:** four releases on my phone with Solflare on devnet. A SOL Clock In landed on the first run (fee 0.000025 SOL); an ETH call landed with both memos and showed on the registry address on Explorer.
- There's no user-adoption number. The submission was judged on the build, and I don't have a retention metric to quote.

### Cost & resource efficiency
- About 0.000005 SOL per Clock In on devnet, from free faucet SOL. 1 SOL pays for about 200,000 Clock Ins.
- ₹0 infrastructure: no server, only public RPCs and APIs.
- Load control: grading capped at 12 calls per run, the SKR balance read at most every 10 minutes, and payer lookups in batched `getTransaction` calls cached for good.

### System constraints
- Devnet only. The history window is the wallet's latest 1,000 transactions plus the cache. A player is ranked only after 3 graded calls.
- MWA gives the wallet 10 s to connect back after it opens. That limit sits outside my code, which is why the retry logic exists.
- Grading depends on Binance's or CoinGecko's public APIs being reachable. CoinGecko is hourly beyond a day, hence the 65-minute window.
- Clock Ins made before v0.2.0 have no leaderboard tag.

## What the history shows (real decisions)
- **Oct 6:** reading the rules changed the plan. "Direct ports or PWA wrappers will score poorly", and the project must be new or show significant new mobile work, so wrapping SMT World in a WebView was out.
- **Oct 7:** PR #1 shipped the whole app. A `/code-review` pass found 10 issues, all fixed: the reveal now shows the SMT call snapshot that went into the memo, not the feed's current call; odd feed actions are normalised; the CoinGecko fallback never grades on a price before the horizon; grade retries are bounded.
- **Oct 7:** phone test 1 led to v0.1.3. Then v0.2.0 (leaderboard, SKR, widget, share card) and its own code review (10 findings), then v0.2.1 from phone test 2.
- **Oct 12:** a week of use led to v0.3.0. "Why is SMT wrong?" turned out to be the app grading SMT's WAITs. Same day: v0.3.1 → v0.3.2 → v0.3.3 from three more phone failures. The final demo video follows my real ETH Clock In (Oct 12, 21:10 IST).
- The deadline moved from Oct 12, 17:29 IST to Oct 13, 05:29 IST.

## Weak spots to own before they ask
- Claude Code wrote most of the Kotlin under my direction, and the README says so. My part was the product decisions, the phone testing and the failure diagnosis, and the bugs above came from my device runs.
- It's not on the dApp Store. That only happens if it wins.
- The leaderboard is only as fair as the trust rules: a call is a public memo anyone can write. I can explain each rule and the attack it blocks.
- No usage numbers beyond my own testing.

## Sources
`README.md`, `RELEASE_NOTES.md`, `.github/workflows/build.yml`, `app/src/main/.../{solana,data,smt,market}/*.kt`, test count from `app/src/test`; the full git log Oct 7–12 (PRs #1–#7 on branch `claude/eloquent-hopper-digb0s`, with commit bodies for v0.1.3, v0.2.0, v0.2.0 review fixes, v0.3.0–v0.3.3); [DSProjects#30](https://github.com/JannetEkka/DSProjects/issues/30) comments of 10-06, 10-07 and 10-12.
