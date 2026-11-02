# Smart Money Tracker: multi-agent whale tracking (OpenServ × Hack2skill, Best DeFi Application)

**2024 hackathon. Winner, Best DeFi Application, OpenServ × Hack2skill; runner-up, Best Website Application** (résumé, `docs/business/16VC_APPLICATION.md` in the SMT repo: "the multi-agent wallet tracker SMT grew out of"). It's the origin of SMT's name and personas (Jan 31 origin post: "an AI trading bot with 5 personalities that argue about crypto then somehow agree on trades").

> ⚠️ **No source code for the 2024 hackathon build exists in any repo I could access** (`_portfolio_src/data.py`: "no repo exists: Smart Money Tracker → left blank"). The stack claims on the portfolio card (OpenServ SDK, Alchemy webhooks with sub-second monitoring, Moralis, Cloud Run, pgvector, three chains, confidence-scored accumulation/distribution, exchange-wallet exclusion) **can't be checked against code here.** Before an interview, fill the gaps below from memory or the hackathon submission page, and drop any claim you can't explain.
>
> **The closest code that does exist** is the private repo `JannetEkka/smt-application` (Aug 26–28, 2025): a FastAPI backend and Flutter app that track whale wallets on **Ethereum, BNB Chain (56) and Polygon (137)** through Etherscan V2, with a Gemini chatbot. It's the successor app on the same three chains, not the hackathon code. The facts below marked *(smt-application)* come from it.

## The 30-second version (as claimed on the portfolio, to verify)
Multi-agent whale tracking across Ethereum, BNB Smart Chain and Polygon on the OpenServ SDK, with Alchemy webhooks driving near-real-time transaction monitoring; confidence-scored detection of accumulation, distribution and coordinated movements; exchange-wallet exclusion so exchange shuffles aren't read as whales.

## 1. Architectural reasoning
- **Database:** the portfolio card says pgvector *(unverified)*. In smt-application, a **unified DB layer supports SQLite in development and Firestore in production** (`src/database/connection.py`), the same "cheap locally, managed in prod" pattern as SmartDesk's pgvector/AlloyDB.
- **Compute:** the card says Cloud Run *(unverified)*. smt-application is a FastAPI service (~6,900 lines of Python) with a Flutter client (~2,200 lines of Dart).
- **Frameworks:** OpenServ SDK for the agents *(unverified; the hackathon's sponsor SDK)*. In smt-application: Etherscan V2 (one key, multiple chains), CoinGecko for prices, Gemini for the chat.

## 2. Data & security pipelines
- **Auth** *(smt-application)*: JWT (HS256) issued by the backend, verified per request, with expiry handled (`jwt.ExpiredSignatureError`). The secret comes from settings and the environment.
- **⚠️ A finding from reading the repo:** `firebase-service-account.json` is **committed** in `smt-application` (private repo). A private repo isn't a secret store: anyone with repo access, any fork or any leaked clone gets the key. **Rotate that service-account key in the Firebase/GCP console and remove the file from history.** Since GCP billing is closed the blast radius is smaller, but the key may still grant Firestore access. This is a good interview story *only after it's fixed*.
- **Ingestion:** the card says Alchemy webhooks, push-based and event-driven *(unverified)*. smt-application polls Etherscan V2 per chain on a schedule, a pull model. If asked "webhooks vs polling", the honest comparison is between these two builds: webhooks are lower-latency and cheaper per event but need a public endpoint and replay handling; polling is simpler and stateless but rate-limited.
- **Privacy:** public on-chain data only; wallet addresses are pseudonymous.

## 3. Reliability & failure operations
- Not verifiable for the 2024 build. In smt-application: service classes per provider (Etherscan, CoinGecko, notifications, alerts). I haven't reviewed their error handling in depth, so don't claim fallbacks.

## 4. Evaluation & optimisation metrics
- **The result:** a hackathon win (Best DeFi Application) and a runner-up (Best Website Application). **No measured accuracy for "accumulation / distribution detection" is on record.** If asked how I'd measure it: label a sample of flagged movements by hand against exchange inflow and outflow, and grade "accumulation" calls against forward price moves vs a baseline. That's what SMT's later direction audits did, and they found the whale/flow persona at roughly zero skill at 4–24h (SMT F-505, whale −0.8 / −0.2pp). Mention that link if they push.
- **Constraints:** free-tier API rate limits (Etherscan, CoinGecko) bound how many wallets can be tracked.

## Weak spots to own before they ask
- No public code; the stack claims rest on memory.
- The committed service-account key in the successor repo (fix it first).
- Whale signals later measured at no directional skill in SMT.

## Sources
`_portfolio_src/data.py` (card + "no repo" note), SMT repo `OPERATOR_CONTEXT.md` (origin post), `docs/ROADMAP.md` ("OpenServ Hackathon — WON, Best DeFi Project"), `docs/business/16VC_APPLICATION.md`, SMT `docs/FINDINGS.md` F-505; private `JannetEkka/smt-application` (README, `main.py` JWT, `src/database/connection.py`, `src/services/*`, commits Aug 26–28, 2025).
