# Where Jannet's card is on file

Every account where Jannet's card was added, held or charged for a project or hackathon, so a bill is never a surprise. This repo is public, so the file never holds card digits, account IDs or logins: only the service, what it's for, how it could charge, and what to check next.

**Rule (Jannet, 10-29):** when a sign-up, trial, credit claim or top-up asks for a card, add a row here in the same session, before anything is spent. When the card comes off, set Status to `removed` and keep the row.

**Hooks** (`.claude/hooks/cards.sh`): at the start of each session it shows the accounts marked `on file` or `unknown` and any **Next check** due within 7 days; when a message mentions a card or billing, it reminds Claude to update this file. The hook reads the table below, so keep its columns, start **Next check** with a `YYYY-MM-DD` date (or write `none`), and use one of these statuses: `on file`, `unknown`, `removed`, `closed`.

| Account | Used for | Card since | How it can charge | Guard | Next check | Status |
|---|---|---|---|---|---|---|
| Nebius Token Factory | Footfall, Nebius × NVIDIA ([#53](https://github.com/JannetEkka/DSProjects/issues/53)) | 10-27, required at sign-up | Charges the card automatically when the balance goes below zero (at the start of the month or at a billing threshold). No spending limit, and auto-charge can't be turned off | Spend only the $25 Builder credit and the $1 trial; never top up with the card. Footfall caps itself at $15 in total and 20 runs a day | 2026-12-16: judging is over. Delete the key, check the balance and invoices, remove the card or close the account, and suspend Render (a reminder is scheduled) | on file |
| Meta Model API (Pay as you go) | Chithi, Meta hackathon ([#40](https://github.com/JannetEkka/DSProjects/issues/40)) | 10-27 | After the $150 credits, Pay as you go bills at ₹1,000 or on the 1st of the month. Muse Code is a separate monthly subscription (₹399 or ₹1,399) | $150 spend-limit email; $0.97 used by 11-03 ($149.03 credit left, balance ₹0.00); the ₹1,198 pre-authorisation hold was released (Jannet, 11-03); never subscribe to Muse Code. The live demo keeps using the key during judging (capped at 15 letters per visitor, 400 a day) | 2026-11-10: Jannet waits for the results announced the night of 11-09, then deletes `META_HACK_API_KEY` from Render and check Billing still shows only credit used. Remove the card after the community vote (Nov 16) | on file |
| Oracle Cloud (Free Tier) | SMT's bot box, an Always Free VM since 10-03 | 10-02, an identity check at sign-up (a hold, not a charge) | Only if the account is upgraded to Pay As You Go | Never upgrade the account | none | on file |
| Google Cloud billing account | SMT, SMT World and Wiretrap's old hosting | 08-03, when the free trial was upgraded to redeem the Gen AI APAC $100 coupon | It can't any more: the billing account was closed and billing disabled on all three projects on 10-02. It charged the card once before that | Closed | none (optional: remove the card from the Google payments profile if nothing else uses it) | closed |

## Signed up without a card

Public AI (Hack Apertus) · Google AI Studio keys (free tier, no billing) · Firebase Spark · Cloudflare · FalkorDB Cloud free tier · YouCam API (1,000 units from a redeem code) · NVIDIA build.nvidia.com key · Kaggle · Santiment free plan · GitHub and Render (Jannet checked Billing on 11-09: no card on file on either, so GitHub Actions past the free minutes and Render's paid instances can't bill) · JigJoy's $20 Claude credit for the NTP Novi Sad hackathon (build.jigjoy.ai/credits handed over the key with no card, 10-31). Planned: the APIMatic trial (no card).

## Skipped because they needed a card or our own money

OpenCV AI Competition (an AWS account with a card on file) · Render Workflows · Arc Microgrants (mainnet gas) · the Web3 for Social Good final (flights and a visa).
