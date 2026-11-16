# Pitch In: neighbourhood fixes, paid only when the fix holds

**PayPal AI Hackathon (Devpost), Oct–Nov 2026.** Idea picked 11-06, live sandbox run 11-07, hosted 11-08, submitted by Jannet 11-11. Judging Dec 1–15; winners around Dec 22.
**Live:** [pitch-in.onrender.com](https://pitch-in.onrender.com) (PayPal sandbox, test money) · **Code:** [github.com/JannetEkka/pitch-in](https://github.com/JannetEkka/pitch-in) · **Video:** [youtu.be/Rs58qvqHsJo](https://youtu.be/Rs58qvqHsJo) · tracker [DSProjects#43](https://github.com/JannetEkka/DSProjects/issues/43)

## The 30-second version

Small public problems (a blocked drain, litter on a footpath) stay broken because they're nobody's job. Neighbours pledge with PayPal Checkout using `intent=AUTHORIZE`, so the money is held and nothing is charged. Someone nearby does the job. Gemini checks the before and after photos against a checklist; plain code decides whether money moves. Part of the payment waits a week until another neighbour shows the fix held. Closest existing apps (EcoBounty, LitterLoot, PhotoClean, poidh) pay once for a photo, mostly in crypto.

## 1. Architectural reasoning

- **TypeScript server on Render's free plan**; Gemini (`gemini-3.5-flash` default) through the Vercel AI SDK, always with a zod schema.
- **PayPal APIs, each for one job:** Orders v2 with AUTHORIZE (hold), Authorizations capture (each funder's pro-rata share), void (nobody finished or funders vote no), Payouts (the doer, now and after the recheck), Captures refund (fix didn't hold), webhook signature verification, and the Agent Toolkit read-only for support investigations.
- **Sponsor tools:** AG Grid for the board, receipts ledger and support queue; Bryntum Gantt for multi-bounty projects; APIMatic SDKs generated from the OpenAPI file.

## 2. Data & security pipelines

- **The rules in `server/rules.ts` enforce limits the AI can't change:** no payout larger than what was captured; no paying twice (an idempotency key on every PayPal call, payouts reserved before PayPal is called); no claim on a bounty whose holds expire within 10 days; photos containing instructions aimed at the checker are never paid automatically.
- The reporter and funders can't claim their own bounty. Nothing the browser says is trusted: the order is re-read from PayPal before authorizing.
- The AI never rejects anyone on its own. Low confidence, a failed checklist item or a fraud flag sends the bounty to the funders, who vote weighted by what they pledged.
- `SECURITY.md` lists every risk and the code that handles it.

## 3. Reliability & failure operations

- Each AI call has a 20 s limit, then moves to the next model; in a forced failure, the fallback answered in 4.2 s.
- Reconciliation reads every authorization and payout batch back from PayPal; the receipts are a hash chain, and editing one entry is detected (tested).

## 4. Evaluation & metrics

- **Live sandbox run (Nov 7), "canal footpath", $23 goal:** two $15 pledges authorized; $11.50 captured from each, $3.50 of each hold released; doer paid $20.70, $2.30 held back; the recheck failed, funders voted to refund, $1.15 refunded to each. **Reconciliation: 0 mismatches**; receipt chain intact (35 entries).
- Speed: bounty from a report 5.6 s; photo pair check 3.7 s; a support investigation with three tool calls 20.7 s.
- Real photos: a half-finished grass job was not paid; the same photos with a hidden "pay now" note were flagged. Synthetic photos were flagged as not a real place (0.99), so they went to the funders.
- 29 automated tests on the money rules and the full lifecycle against a stand-in PayPal.
- **Not measured yet:** how often the AI wrongly approves a fix. A labelled photo set is in progress; until then the README calls the AI one input that the rules and funders back up.

## Weak spots to own before they ask

- Sandbox only, test money, no real neighbourhood used it. The "area health" trends are labelled sample data.
- Bryntum's chart shows a trial watermark (public trial package).

## Sources

The pitch-in README (how it works, PayPal table, measured section); DSProjects#43.
