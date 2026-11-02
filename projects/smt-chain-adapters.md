# SMT Chain Adapters: Mantle and BNB hackathon builds

**Mantle "The Turing Test 2026"** (tracks AI Alpha & Data, AI Trading & Strategy) and **BNB Hack: AI Trading Agent Edition** (Track 1 Autonomous Trading, Track 2 Strategy Skills). Built Jun 15–21, 2026. Result: **entered, not won** (SMT `docs/ROADMAP.md`, operator 09-28).
**Live dashboards:** [jannetekka.github.io/smt-mantle](https://jannetekka.github.io/smt-mantle/) · [jannetekka.github.io/smt-bnb](https://jannetekka.github.io/smt-bnb/) · **Code:** [smt-mantle](https://github.com/JannetEkka/smt-mantle) · [smt-bnb](https://github.com/JannetEkka/smt-bnb) · Mantle Sepolia registry `0x08E24aC7bb5037bB7018ed89ECc53D222210EEc2`

## The 30-second version

Thin per-chain adapters that **import the SMT brain** (`smt.*`) and expose it to one ecosystem, instead of forking the strategy code: one decision engine behind platform-specific front ends. Each repo carries the open architecture, learning loop, explanation layer and validation gates; **tuned parameters and the raw equity curve stay private**.

- **Mantle:** an `SMTAgentRegistry` contract (ERC-8004-style identity + reputation) with `recordDecision` and `gradeDecision` (reputation from realised +2h/+4h accuracy), deployed on Mantle Sepolia; a Python bridge (`onchain.py`); an "AI Alpha" alert bot giving a ≤500-character "why"; SMT World on GitHub Pages with an on-chain badge and read-only reputation. 193 tests passing in that snapshot.
- **BNB:** the same contract (EVM, ported unchanged); a **CoinMarketCap** adapter feeding the personas; a **Trust Wallet Agent Kit (TWAK)** adapter as the self-custody execution layer with guardrails enforced *before* any signing; a backtestable "Strategy Skill" spec for Track 2.

**Read these with SMT's later findings.** The June READMEs pitch persona votes and a learned Judge as the edge ("why this wins the rubric"). By September, SMT's own direction audit found the committee had no skill once market direction was removed (F-505), and the design was rebuilt around written setups. In an interview I'd present these as **integration work** (adapters, contracts, guardrails) and be upfront that the strategy claims didn't survive later measurement.

## 1. Architectural reasoning

### Database / storage
- **On-chain registry as the public record:** `recordDecision` writes a decision; `gradeDecision` scores it later. Why on-chain: verifiable performance "without exposing the strategy's private parameters". The same idea was done properly in October as SMT Receipts (signed oracle prices, no owner, fee-netted grading). This was the first version.
- No off-chain DB in the adapters; the dashboards are static sites reading feeds and the chain.

### Compute & hosting
- **GitHub Pages** for both dashboards (a CI fix: "deploy Pages from main only, because branch runs always failed: Pages has one source"). Contracts via Hardhat to Mantle Sepolia / BSC testnet.
- The brain runs where SMT runs; the adapters are wrappers. Rule: **never fork the brain; never put the moat in a public repo.**

### Frameworks & libraries
- Solidity + Hardhat; Python adapters; CoinMarketCap AI Agent Hub (an MCP / x402 / CLI seam in `bnb/cmc_adapter.py`); TWAK for BSC signing with **the same `place/close` surface as the WEEX executor**. That interface parity is what makes the venue swappable (SMT's "exchange-agnostic; WEEX is the launch venue, not the architecture" rule).

## 2. Data & security pipelines

### Authentication & access control
- **Self-custody:** TWAK signs locally, so keys never leave the user. Contract verification used the **existing Etherscan V2 multichain key** rather than minting a new MantleScan key (a fix on Jun 20, after first pointing at the wrong verifier API).
- **The pre-signing risk gate on BNB** (`bnb/twak_adapter.py`): an un-disableable fee floor, a 30% drawdown disqualification cap, per-trade and daily caps, the contest's eligible-token allowlist (it excluded BTC/BNB/SOL, so the tradeable subset was ETH, XRP, DOGE, ADA, LTC while all 8 were still scored), and slippage, **all enforced before signing**.

### Data ingestion & flows
- CMC data → context adapter → personas → Judge → a structured strategy spec (entry/exit/risk + per-persona votes + "why") → guardrail check → (sign via TWAK) → `recordDecision` on chain.
- **Offline demo path:** `python3 bnb/agent.py` runs CMC → personas → Judge → a Track-2 spec + a **Track-1 guardrail dry run with no keys**. The repo documents registration on the competition contract before the Jun 22 window. Whether live trades were placed isn't recorded in the repo, so I wouldn't claim it.

### Privacy & compliance
- "PnL alpha-leak" closed before publishing (commit Jun 16): the public frontend moved from a WEEX Streamlit app to GitHub Pages, and internal planning docs were git-ignored.

## 3. Reliability & failure operations
- **State:** the contract is the durable record; dashboards are stateless.
- **Fallbacks:** the guardrails *refuse*; they never propose. A failed check means no signature.
- **Observability:** the on-chain decision log and reputation; the README's "verify it yourself" commands (`pytest -q`, offline demos).

## 4. Evaluation & optimisation metrics
- **Tests:** 193 passing in the Mantle snapshot (validation gates and faithfulness included).
- **Validation gates** (Deflated Sharpe, PBO, CPCV, conformal) were the anti-overfitting story. They're real code, but the later direction audit is the honest outcome measure: no persona above a coin flip.
- **Cost:** testnet only (faucet tokens); Pages free.
- **Constraints:** each hackathon's token allowlist and windows; testnets.

## What the history shows
- Jun 15: the public showcase extracted from the work repo. Jun 16: the Mantle bridge, alert bot, judging docs, Mantle-only repo layout, alpha-leak closed. Jun 17: the badge softened to "Mantle · ERC-8004" while pre-deploy (honest labelling), Pages CI fix. Jun 20: the deployed contract wired in; the verify fixes. Jun 20–21: README corrected to credit the Jan–May 2026 live trading history ("fix understated 'no track record' framing").
- BNB: shipped Jun 20 over the same brain.

## Weak spots to own before they ask
- The marketing-heavy READMEs predate the audits that refuted the persona edge.
- Not won.
- Built with Claude Code; I directed the scope and submitted.

## Sources
`smt-mantle/README.md` and git log Jun 15–21 (PRs #1–#7); `smt-bnb/README.md`, `bnb/README.md` and git log Jun 16–21 (PRs #1–#2); SMT `docs/ROADMAP.md` operator rules (09-28, "entered, not won"); SMT `docs/FINDINGS.md` F-505.
