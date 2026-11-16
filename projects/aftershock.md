# Aftershock: did the news move the chain? An event study on NEAR

**NEAR Hackathon, Investment Thesis track, Nov 2026.** Designed 11-12/13, built 11-13/14, submitted Nov 15 about 03:30 IST (two hours before the close). Results due by Nov 19.
**Live:** [jannetekka.github.io/aftershock](https://jannetekka.github.io/aftershock/) · **Code:** [github.com/JannetEkka/aftershock](https://github.com/JannetEkka/aftershock) · thesis `THESIS.md` · tracker [DSProjects#85](https://github.com/JannetEkka/DSProjects/issues/85)

## The 30-second version

For someone deciding whether to hold NEAR for years, headlines are the usual evidence. Aftershock tests them. Code finds every spike of news about NEAR (GDELT), checks whether the chain's own daily records (NearBlocks, DefiLlama) moved in the 7 days after, and compares that with ordinary days. **Of 74 news events, 8 moved the price (10.8%, against 5.1% of ordinary days) and 10 moved usage (13.5%, against 16.5% of ordinary days).** Transactions alone: 0 of 74. So NEAR's usage did not follow its headlines, and the thesis is written from that.

## 1. Architectural reasoning

### Database / storage
- **A data snapshot in the repo** (`data/`) with SHA-256 fingerprints: 2,305 days of NearBlocks charts (2020-07-21 to 2026-11-11, one call), DefiLlama TVL, DEX, stablecoin and Intents volume, GDELT article counts. All free, no keys. A snapshot makes the run reproducible: `make verify` rebuilds every result byte for byte with the network blocked.
- **A NEAR testnet contract** (Rust) stores the snapshot fingerprint, the run counts and four forecasts with due dates, posted before the outcome is known. Testnet only, no money (our rule; the hackathon allowed testnet in all tracks).

### Compute & hosting
- Python 3.9+ scripts and a Makefile. Static page on GitHub Pages. Models on build.nvidia.com's free endpoints.

### Frameworks & models
- **Code decides, models describe.** The event finder (news count above the 95th percentile of the previous 90 days and at least 3 articles) and the event test (change from 28 days before to 7 after, against the same change on every ordinary day) are code.
- Two model seats from different labs: Bear and labeller on `nvidia/nemotron-3.5-lightning-30b-a3b`; Bull and Judge fall back across GLM 5.3, MiniMax M3.1 and StepFun Step 5 (every recorded reply names the model that answered). A claim is always examined by the other family.

## 2. Data & security pipelines

- Fetch → fingerprint → events → labeller → event test → Bull and Bear write claims as data, rebut once → recomputation (code) → Examiner (other family) → decision rule (code) → Judge writes from kept claims only → final check cuts any sentence without a kept claim behind it.
- `make live` refetches all three sources and stops, publishing nothing, if one fails or returns too few days.
- No keys in the repo or its history (checked); the testnet key file is with Jannet only.

## 3. Reliability & failure operations

- Every model reply is validated (required fields, allowed values) and retried; failures are recorded, not skipped.
- Missing days in an event's window make that measure "not tested", never "nothing".
- GDELT refused per-event requests, so headlines come from one top-articles-per-day request. Mistral and the large Nemotron timed out on long prompts and were replaced.

## 4. Evaluation & metrics

| Question | Result | Compared with |
|---|---|---|
| News events that moved the price (7 days) | 8 of 74 (10.8%) | 5.1% of ordinary days |
| Events stamped "moved usage" | 10 of 74 (13.5%) | 16.5% of ordinary days (measured with the same rule) |
| Transactions alone | 0 of 74 | 3.7 expected by chance |
| Claims kept after the check | 14 of 20 (6 removed by the Examiner, 0 by recomputation) | with the check off, all 20 would print |
| The same models asked for a thesis with no data | 1 right, 15 wrong, 4 uncheckable (right = within 10%) | kept claims must be within 1% |

- Sensitivity at 3, 7 and 14 days is in the README. The price result at 7 days does not hold at 3 or 14 days, so the thesis doesn't lean on it.
- 26 unit tests, including a made-up series with a planted +50% jump that must be stamped "moved" while a quiet day is not; 6 contract tests.

## What the history shows (real decisions)

1. The web check (lessons 0) killed the first three ideas; Jannet picked a checked thesis and added the angle: news sets the bull or bear story, so test the news.
2. The "ordinary days" comparison was added at sign-off, to rule out chance. The event rule's 3-article floor was fixed before any test result was seen.
3. Internal targets were missed; submission was about two hours before the hard close.

## Weak spots to own before they ask

- 49 of the 74 spikes were market-wide price coverage rather than NEAR-specific news; filtering them first is proposed, not built.
- Nearby days aren't independent, so the odds on the page are approximate; the ordinary-day band uses the whole history, where early years swing more.
- One news source. The four real forecasts settle on 2026-12-11 and 2027-02-09.

## Sources

The aftershock README (results, sensitivity table, contract transactions, implemented vs proposed); DSProjects#85 comments 11-08 to 11-14.
