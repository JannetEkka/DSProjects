# Afterburn: farm-fire verification from Sentinel-2 burn scars

**IEEE ClimateChain Global Hackathon 2026, Climate Data & Environmental Monitoring track.** Idea picked and built Oct 21, 2026, submitted the same day (4 days early). Judging Oct 26 – Nov 8, winners Nov 20.
**Live:** [jannetekka.github.io/afterburn](https://jannetekka.github.io/afterburn) · **Code:** [github.com/JannetEkka/afterburn](https://github.com/JannetEkka/afterburn) (MIT) · pact `0xC892d8B3FeB08Cb36c705019B500dd646CcF6b2D` on Monad testnet · demo 4:36 [youtu.be/XqyN4N3_2TY](https://youtu.be/XqyN4N3_2TY) · deck `media/afterburn-deck.pdf`

## The 30-second version

Punjab's official farm-fire count fell more than 90% between 2021 and 2025, while burnt area mapped from Sentinel-2 fell only 25–35% (iFOREST *Stubble Burning Status Report 2025*). Farmers moved their fires to after the counting satellites pass at 10:30 and 13:30, so a scheme that pays or fines on fire counts now pays for nothing. Afterburn reads the **burn scar**, which stays for days whatever hour the fire was lit, and runs a pay-for-not-burning pact on that check, modelled on a J-PAL trial in 171 Punjab villages: 25% at sign-up, 75% after a clean season, and a village bonus only if every field stays clean.

**On this season's real data** (80 × 52 km of Amritsar, Tarn Taran and Kapurthala): 23,963 ha of burn scars mapped. Between the Oct 13 and Oct 18 passes, only **2.9%** of the 5,585 scars found had a VIIRS fire detection within 375 m. Validated against VIIRS (an independent sensor on a different schedule): inside VIIRS fire footprints the rule finds 18.9% of harvested land newly burnt against 5.6% on random harvested land, a **3.4× lift**. All 24 demo verdicts recheck as MATCH from fresh public reads, and the pact ran a full season in 98 transactions on Monad testnet.

## 1. Architectural reasoning

### Database / storage
- **No database.** The pipeline writes flat files: per-plot evidence JSON (`docs/evidence/plot-N.json`) and site layers (`docs/data/*.json`, `scars.png`). The site is static and reads the chain live.
- **The chain holds only what must be tamper-evident:** per plot, the farmer address, village, area, status (Enrolled → Verdict → (Disputed) → Clean/Burnt), burnt share, challenge deadline, **polygon hash and evidence hash**. The polygon itself stays with the cooperative.
- **Why hashes on chain and not the data:** the evidence file is keccak-256 hashed over canonical JSON, so Python and Solidity agree byte for byte, and anyone can rebuild the file from public scenes and compare hashes. Personal land data never goes on a public ledger.
- **Land cells:** each plot is cut into 50 m cells, and each cell can be enrolled once, so the same field can't be paid twice under two names. It's a uniqueness constraint enforced by the contract instead of a DB index.

### Compute & hosting
- **The pipeline runs on a laptop-class machine:** "an 80 km area runs in minutes on a laptop." Sentinel-2 L2A is read from Earth Search (AWS Open Data) with **byte-range requests on cloud-optimised GeoTIFFs**, so a 40 km box costs a few MB instead of whole tiles. No GPU and no cloud bill.
- **Static site on GitHub Pages** (Leaflet + ethers.js), reading the pact from Monad testnet in small batches with retry.
- **Why Monad testnet:** free faucet MON, and the pact is a public ledger that a funder, a cooperative and a challenger can all read. For a real pilot the README says payments could stay on India's direct-benefit-transfer rails, with the pact as the ledger they settle against.

### Frameworks & libraries
- **Python geospatial stack:** rasterio, numpy, scipy, scikit-image (field segmentation from 10 m imagery), scikit-learn (the PU experiment). NASA FIRMS 7-day VIIRS files, no key needed.
- **Solidity + Hardhat** (13 tests) for the pact.
- **Gemini** writes the farmer notices in Punjabi and English, from the verdict's facts only.
- **The key choice was a published rule over a model:** a positive-unlabeled gradient-boosting model trained on fields Sentinel-2 caught in flames scored a **2.5× lift against the rule's 3.7×** in the same comparison (`experiments/pu_model.py`). The rule is also a dozen published thresholds, so anyone can recompute a verdict exactly. For a system that moves money, recomputability matters more than a few points of accuracy.

## 2. Data & security pipelines

### Authentication & access control
- **Roles are fixed at deploy:** funder, cooperative (enrols), verifier (posts verdicts), arbiter (resolves challenges). A funder can't swap in a friendlier verifier mid-season.
- **Money controls in the contract:** it won't promise money it doesn't hold; the funder can only withdraw money no farmer is owed; finalize and bonus are callable by anyone once conditions are met.
- **Challenge mechanism:** anyone can stake a bond with a counter-claim and its own evidence hash within the window (72 h in design, 10 minutes in the demo so a season fits one session). The demo ran a deliberately wrong challenge (a watcher claimed the most clearly burnt field was clean), the arbiter rejected it, and the bond joined the pool.
- **Keys:** the testnet deployer and role keys were throwaway, lived only in the build container, and were never needed again once the pact settled (DSProjects#20, 10-21).

### Data ingestion & flows
- **Batch, per satellite pass:** `run_season.py` fetches new Sentinel-2 passes and VIIRS detections, maps scars and exports layers → `plots.py` judges the demo fields and writes evidence files → `chips.py` renders before/after images → `notices.py` writes the messages → `scripts/demo.js` runs the pact on chain.
- **Only pixels the scene classification marks clear are used.** A whole pass is skipped if the darkest tenth of its pixels is brighter than 0.05 in blue, which is how smoke haze shows up. Two of six October passes (Sep 25, Oct 8) were skipped.

### Privacy & compliance
- **The villages aren't named on purpose:** "Stubble burning carries fines, and a verdict from an imperfect detector shouldn't point at a real family." The 24 fields are real and their verdicts are real, but the farmers, addresses and enrolment are simulated.
- Only hashes go on chain, and the polygon stays with the cooperative.
- All inputs are public: Copernicus Sentinel-2 and NASA FIRMS.

## 3. Reliability & failure operations

### State management
- The contract is the state machine (Enrolled → Verdict → Disputed → Clean/Burnt; per village: plots, settled, clean, bonus unlocked). Enrolment is closed before anything settles, which fixes each village's plot count, so the bonus logic can't be gamed by adding plots late.
- One deployment is one season.

### Error handling & fallbacks
- **Asymmetric error cost drives the rule:** a false "burnt" verdict takes money from a farmer who did the right thing, so the rule leans toward clean and accepts missing some burns. The challenge window is where a missed burn gets raised (for example with a geostationary or commercial image).
- **Monad's reserve-balance rule broke the deploy:** the second fund transfer reverted, because an account holding under 10 MON gets one value-spending transaction per 3 blocks. The script now waits 3 blocks after each value-spending transaction.
- **Bad passes are skipped, not guessed:** cloud and haze tests drop a pass, and the evidence file records how many looks a verdict rests on.

### Logging & observability
- `pipeline/recheck.py` is the audit tool: it refetches the exact scenes named in the evidence file, reruns the rule, and prints the recomputed share alongside the file's hash and the on-chain hash. Plot 19: 74.55% scarred between Oct 13 and Oct 18, and all three hashes match.
- `docs/data/deployment.json` lists every pact transaction.

## 4. Evaluation & optimisation metrics

### Performance benchmarking
- **Baseline:** the official fire count (VIIRS active fires). Between Oct 13 and Oct 18, 2.9% of the scars had a VIIRS detection within 375 m. On Oct 18 at 11:20 IST Sentinel-2 caught 160 fields actually in flames, and only 8% of them had a VIIRS detection within 1 km that day.
- **Validation:** a **3.4× lift** inside VIIRS fire footprints vs random harvested land (`experiments/validate.py` → `docs/data/validation.json`).
- **Model vs rule:** PU model 2.5× vs rule 3.7× in the same comparison, so the rule ships.
- **Reproducibility:** 24/24 verdicts MATCH from fresh public reads.
- **What it isn't:** a field-level accuracy figure. The best published Sentinel-2 model for Punjab burn patches (a CNN, Anand et al., *Remote Sensing* 2025) reports Dice 0.64. A real pilot needs ground visits on a sample.

### Cost & resource efficiency
- Free data (Sentinel-2 every 2–5 days over all of Punjab and Haryana; FIRMS), byte-range reads (a few MB per 40 km box), a laptop, GitHub Pages and faucet MON. The cost per field-season is close to zero.
- 98 testnet transactions for a full 24-field season.

### System constraints
- A field burnt and ploughed before the next clear pass can look like ordinary ploughed soil.
- Clouds and haze cost passes (2 of 6 here).
- The arbiter is one address in the demo; a real season would use a multisig (funder, farmers' union, independent scientist).
- The Punjabi notices haven't been checked by a native speaker.

## What the history shows (real decisions)
- **The idea came second:** S13 first proposed Forestproof (EUDR deforestation), Every Hour Counts (hourly renewable matching) and Retired Once (offset double-claims). Jannet asked for something "less obvious" than what every AI suggests, and picked Afterburn from four new ideas (10-21).
- **The science check came before the build:** on real Oct 13/18 passes the first numbers were a 3.3× lift and a PU model at 3.0×, both later refined (final 3.4×; PU 2.5× vs rule 3.7× in the final comparison). I'd quote the final numbers and say the early ones moved as the rule was fixed.
- **Three bugs found by checking, not by tests:**
  1. **Ploughed fields:** freshly ploughed wet soil also darkens and lifts the burn index. A visual check of the first verdicts caught it. Fresh char next to fires Sentinel-2 caught burning never sits below MIRBI 1.6, while wet soil stays near 1.5, so rule v2 requires the char level.
  2. **Reproducibility:** the first rechecks didn't match. The pipeline judged the original polygon, while the recheck used the published one rounded to 6 decimals, a one-pixel difference. Everything is now computed from the published polygon.
  3. **Monad's reserve-balance revert**, described above.
- The repo history is short (8 commits on Oct 21) because the build was pushed once the repo existed: GitHub refused repo creation from the session, so Jannet created it.

## Weak spots to own before they ask
- The lift proves the rule finds burns, not how accurate it is per field.
- The IEEE eligibility pages contradicted each other (the sidebar said "students only", the rules allowed independent developers). We entered under the written rules, and the forum question was never answered.
- Built with Claude Code as the coding assistant; Gemini writes the notices. I chose the problem and the "scar, not flame" framing, picked the rule over the model on the numbers, and checked the verdicts visually.

## Sources
`README.md`, `media/submission.md`, `experiments/`, `pipeline/recheck.py`; the 8 commits of Oct 21 (rule v2, chain snapshot, reserve-balance fix, video); [DSProjects#20](https://github.com/JannetEkka/DSProjects/issues/20) comments (rules 10-20, idea picked 10-21, built 10-21 with full Devpost text, submitted 10-21).
