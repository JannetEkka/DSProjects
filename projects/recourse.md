# Recourse: receipts for welfare algorithms

**Web3 for Social Good 2026 (SMU × GSR Foundation × University of Málaga), Tech Track.** Built Oct 21, 2026, submitted Oct 21. **Passed screening into Round 2** (10-29): presentation video 5:05 submitted; 10 finalists announced by Nov 1; the final (Nov 26) is in person only at SMU Singapore.
**Live:** [jannetekka.github.io/recourse](https://jannetekka.github.io/recourse/) · **Code:** [github.com/JannetEkka/recourse](https://github.com/JannetEkka/recourse) · contract `0x0113802632a88f7f5ebd7603a8eea5f31e5c30ce` on Monad testnet, verified on Sourcify · demo 2:54 [youtu.be/KDfbYbLN7Cw](https://youtu.be/KDfbYbLN7Cw) · Round 2 presentation [youtu.be/xjoOjeGhZQo](https://youtu.be/xjoOjeGhZQo)

## The 30-second version

When an algorithm cuts a family off its rations, nobody can tell them which record did it. In Telangana, Samagra Vedika tagged Bismillah Bee's late husband, a rickshaw puller, as a car owner, and her family lost its rations (Al Jazeera / The Reporters' Collective, Jan 2024). About 20 lakh ration cards were deleted from 2016 on (The South First). The department keeps the only log, and the department is the party being checked.

Recourse makes the agency publish the hash of its matching rules on chain *before* using them, and the contract refuses a batch decided under rules that weren't public in an earlier block. Every decision gets a receipt naming only the records whose removal would flip the outcome. One Merkle root per batch goes on chain, so nothing personal does. Gemini explains the receipt in Telugu, Hindi or English, and a guard rejects any draft that invents a number or record ID. Appeals are filed on the record and go visibly overdue if unanswered.

**In the synthetic demo the truth is known:** of 1,005 households, rules v2 refused 209, and **127 of them wrongly**. v1 refused 75 (10 wrongly). 2,010 decisions were sealed; 16 appeals filed, 14 answered (11 reversed, 3 upheld), 2 left open to show "overdue". The transactions are real.

## 1. Architectural reasoning

### Database / storage
- **Decisions stay in the agency's system; only commitments go on chain:** rule hashes (with a URI to the file) and one Merkle root per batch. Why: personal data must never sit on a public ledger, but the *commitment* must be public so the agency can't rewrite history.
- **Per-ruleset counters live on chain** (decisions, refused, appeals, upheld, reversed), so the public record page needs **no indexer**. It reads the contract directly. That was a deliberate contrast with SMT Receipts, which needed Envio.
- **Receipts are files:** canonical JSON (sorted keys, no spaces, UTF-8, integers only), **salted**, then keccak-256 hashed. A leaf is `keccak256(outcome byte ‖ receipt hash)`, so a refusal and an eligible decision can't be swapped. Inner nodes hash sorted pairs, the same scheme as OpenZeppelin's MerkleProof.
- **Pipeline state** is a JSON file (`out/<network>/state.json`) recording every step, so a re-run never repeats a transaction.

### Compute & hosting
- **Static web page on GitHub Pages** with no build step. The verification runs in the family's browser: re-hash the receipt, fold its Merkle proof into the batch root, call the contract's `verify()`. No backend means no server the agency, or I, could tamper with.
- **The engine is a Python batch job** (`pipeline.py`) run by the agency: decide → build receipts → seal → explain → export.
- **Monad testnet:** about 160k gas per batch (Round 2 deck), free faucet MON.

### Frameworks & libraries
- **Solidity 0.8.28 with Foundry** (21 tests). The contract tests read a batch the Python engine made, so the Python/Solidity seam is tested, not just each side alone.
- **Gemini** for explanations and appeal drafts, behind a deterministic guard (`explain.py`).
- **Plain JS** for the page. "Try to edit it" shows every check failing on an edited copy, and a QR code holds the whole receipt.

## 2. Data & security pipelines

### Authentication & access control
- **Any address can act as an agency** (`nameAgency`), then `publishRuleset(rulesHash, uri, responseDays)`, then `sealBatch(rulesetId, root, count, refused)`, **only from the next block on**.
- **`answerAppeal` is the agency's alone**, and only once.
- **Appeals are accepted only against sealed refusals:** `fileAppeal(batchId, receiptHash, proof, groundsHash)` checks the Merkle proof against a *refusal* leaf.
- **The family needs no wallet:** a legal-aid worker files the appeal with the receipt's proof. That's a deliberate accessibility choice. The people affected are the least likely to hold crypto keys.
- **Keys:** the agency and legal-aid keys are read from files named by env vars (`RECOURSE_AGENCY_KEY_FILE`, `RECOURSE_LEGAL_KEY_FILE`), testnet only, and never held real funds.
- **The Gemini key is per project:** on 10-21 the pipeline was changed to call Gemini *only* with `--gemini-env NAME`, because it had picked up a `GEMINI_API_KEY` from the environment that belonged to another project. That followed the "one key per entry" rule.

### Data ingestion & flows
- A batch flow per re-verification run: the agency publishes the rules (block N) → decides every card → builds salted receipts → seals the Merkle root (block > N) → each family gets its receipt and proof → an appeal is filed against a refusal → the agency's answer is sealed too.
- `--export-only` rewrites `web/data` from the saved state without the chain or wallet keys, retrying explanations that had fallen back to fixed wording.

### Privacy & compliance
- Only salted hashes and roots go on chain. The salt stops anyone brute-forcing a receipt from guessable fields.
- **An open issue I'd raise myself:** receipts carry *other people's* registry records (the stranger's car that matched). A real deployment needs a rule for how much of a matched record the family may see.
- All households, names and registries are synthetic and seeded (`engine/recourse/world.py`). Amina's case is modelled on Bismillah Bee's, with invented names and records.

## 3. Reliability & failure operations

### State management
- `state.json` records each completed step, so the pipeline is **resumable and idempotent**: a crash mid-run resumes without double-sealing.
- On chain, the ordering rule (rules published in an earlier block than the batch) is enforced by the contract, not by process.

### Error handling & fallbacks
- **LLM fallback chain:** Gemini model A → model B (a timeout now falls through to the next model instead of ending the call) → **fixed wording** if the model fails twice. Fixed wording is retried later with `--export-only`.
- **The real run (10-21):** Gemini was overloaded (timeouts, 429s), so 12 explanations shipped in fixed wording. Two export-only re-runs replaced them. On the first, RV-2026-001003's drafts were **rejected by the guard** because they quoted rule weights and the threshold, numbers an *eligible* receipt doesn't carry, and RV-2026-001005 hit HTTP 503 twice. The second run passed both. All 5 spotlight receipts ended with guard-passed Gemini text in en/hi/te.
- **The guard is the core safety mechanism:** it collects every number and record ID in the receipt (and in what the family told the legal-aid worker), then checks the model's text. It works across all three languages because names and IDs stay in Latin letters and digits stay 0–9. It also rejects a draft that leaves out a decisive record.
- **RPC rate limits:** the public Monad RPC drops calls (429) when about 40 arrive at once, so the page retries contract reads.

### Logging & observability
- The public record page *is* the observability: refusals and reversals per rule version, the rule diff, every batch and appeal, letter hashes checked, and overdue appeals flagged with a date.
- Commit messages record exactly which receipts and languages were model-written vs fixed wording at each step.

## 4. Evaluation & optimisation metrics

### Performance benchmarking
- **The synthetic world exists so the truth is known:**

| | Rules v1 | Rules v2 |
|---|---|---|
| Refused | 75 (7.5%) | 209 (20.8%) |
| Really outside the scheme | 65 of 82 | 82 of 82 |
| Wrongly refused | 10 | 127 |

- v2 caught 17 more real cases and cut off 117 more families who should have kept their rations. An auditor can't see the "wrongly refused" row in real life. What the public record *does* show is that v2 refused nearly three times as many families and that most of its appealed refusals were reversed (11 of 14 answered).
- **Decisive-reason test:** `decide.py` re-runs the rules with each set of counted records removed, smallest sets first, and lists only the sets whose removal flips the outcome. That's the same counterfactual test SMT uses for its explanations.
- Tests: 21 Foundry + 21 Python engine tests. The page was checked at 1280 px and 390 px with no console errors.

### Cost & resource efficiency
- About 160k gas per sealed batch, whatever the batch size, because one Merkle root covers 1,005 decisions. No indexer, no backend, GitHub Pages, and faucet MON.

### System constraints
- **It proves which rules the agency *said* it ran, when, and what it decided. It can't prove the agency ran them on every household.** A family or auditor with a receipt can re-run the published rules and catch a mismatch.
- It can't force the agency to answer, only make a missing answer visible.
- Public-RPC rate limits (~40 concurrent reads) shape the page's read pattern.

## What the history shows (real decisions)
- **Positioning by reading the field:** on 10-20, about 10 of 31 early builds were donation or aid trackers, so the plan avoided that lane. Three ideas were proposed (Fair Hearing/Recourse, anticipatory flood aid, Keepers for digital public goods). Jannet picked the welfare-receipts idea.
- Built and rehearsed on a local chain (anvil) by 13:10 IST on 10-21, then deployed live on Monad and sealed two batches and 16 appeals in the next commit, all on Oct 21.
- **Round 2 (10-29):** the organisers revealed the final is in person only in Singapore, which overturned the tracks page's "online or in person". Jannet chose to make a new 4–5 minute presentation and decide about travel after Nov 1. recourse#3 added an architecture diagram and impact and feasibility slides.

## Weak spots to own before they ask
- The demo is synthetic. The case it's modelled on is real, but no agency has used it.
- Exposure of third-party records on receipts is unresolved.
- Built with Claude Code as the coding assistant; Gemini writes explanations and the guard decides whether they're used; the narration is a synthetic voice reading my script.

## Sources
`README.md`, `contracts/test/Recourse.t.sol` (21 tests), git history Oct 21–29 (PRs #1–#3); [DSProjects#45](https://github.com/JannetEkka/DSProjects/issues/45) comments 10-20, 10-21 and 10-29; tracker row in `hackathons/october-2026.md`.
