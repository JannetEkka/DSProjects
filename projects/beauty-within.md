# Beauty Within: hair, clothes and one lip tint chosen from your own colours

**YouCam API Skin AI & eCommerce VTO hackathon (Perfect Corp).** Idea picked Oct 27; built Oct 27 and Nov 1–2, 2026; **submitted Nov 2, with the Women in Tech prize opted in**. Judging to Nov 20; winners ~Nov 24.
**Live:** [beauty-within.pages.dev](https://beauty-within.pages.dev) · **Code:** [github.com/JannetEkka/beauty-within](https://github.com/JannetEkka/beauty-within) (MIT) · video 2:10 [youtu.be/ATzI4K94w44](https://youtu.be/ATzI4K94w44)

## The 30-second version

Most beauty try-ons sell a look and retouch the face to sell it. Beauty Within reads **your own colours and face shape** with YouCam's analysers (Facial Color Tones, Face Analyzer, AI Skin Analysis) and shows **one look built from them, on your own unretouched photo**: outfit (from YouCam's clothes catalogue in your colours), then hairstyle (templates matched to face shape, keeping your hair colour), then **one lip tint** at your own lip depth. A "Care from within" tab adds strengths first, then nutrients and habits from an "About you" form.

**Measured, on YouCam's own sample photos (Nov 1):**
- **Lip depth:** YouCam's default makeup render made lips ~5 L* darker. The calibrated render keeps her lip depth **within ~2 L*** on three lip types (medium, deep and saturated, light).
- **No retouching:** skin smoothing is set to 0 (the default is 50). YouCam's hair-colour try-on brightened cheek and background by 10–13 points (RGB) as well as the hair, so hair colour was **dropped**.
- **Fairness:** undertone from hue alone labelled **every deep skin tone in the sample cast "cool"**; the depth-adjusted reading doesn't (tested).
- **Inputs:** YouCam's hair-colour read was wrong or empty on **4 of 5** sample photos, so the user can correct it.
- **Not measured,** and the README says so: whether it lowers wrong-shade purchases or returns. A store could measure it by comparing return rates for try-on purchases vs others.

## 1. Architectural reasoning
- **Storage: Cloudflare KV as a content-addressed cache.** Every YouCam result is cached **by content hash**; a look is built layer by layer, and **every prefix of layers is cached**, so changing one layer only re-runs from there. The cache key carries a version: lip renders are versioned, so old faint tints aren't served after the calibration changed. The sample portraits' readings are recorded fixtures (YouCam's real replies) so judges always have them.
- **Compute: Cloudflare Pages + Pages Functions** (free tier). The frontend is Vite + TypeScript; the API is one Pages Function (`functions/api/[[path]].ts` → `src/server/api.ts`). Why serverless here: each call is short orchestration of YouCam's async tasks with caching in KV, and there's no long-lived state.
- **Domain code is pure and tested:** colour maths in **CIELAB and CIEDE2000**, lip tint, palette, hair and care, with unit tests (~40). The vendor client (`youcam.ts`) is separate.

## 2. Data & security pipelines
- **Auth:** no user accounts. The YouCam key is a **Cloudflare Pages secret** (`wrangler pages secret put`), locally in `.dev.vars`, never in the repo. "About you" answers are **saved on the device**, not on the server.
- **Ingestion:** YouCam's flow per feature: `POST /s2s/v2.0/file` → PUT bytes to a pre-signed URL → `POST` task → **poll** `GET task/{id}` every 2 s up to a timeout (60 s; 90 s for look layers). The camera uses YouCam's JS Camera Kit (face alignment and lighting guidance), with upload as the fallback.
- **Privacy:** a face photo is biometric-adjacent personal data. Photos and portraits are cached in KV with a TTL (90 days for sample portraits; shorter for live ones), not kept indefinitely. A real store deployment would need explicit consent and a short retention period.
- **Repo hygiene:** working files (Devpost text, narration) were moved out of the submitted repo into DSProjects (Nov 2).

## 3. Reliability & failure operations
- **A hard budget floor:** live YouCam calls **stop when the account's units fall below `UNIT_FLOOR` (150)**, so judges always get the sample portraits from cache even after the live budget is spent. ~735 units were left at submission; the units expire ~90 days after redemption.
- **Bounded polling** with a clear 504 "still running after Ns" error; a daily counter in KV.
- **Feature removal as a fallback:** hair colour was dropped rather than shipped with a known whole-image brightening artefact.
- **Camera unavailable** → a clear message, and upload still works.

## 4. Evaluation & optimisation metrics
- The colour measurements above (L* error on lips, the brightening delta, the undertone fairness check, the hair-read failure rate) are the evaluation, done on YouCam's sample cast of different skin tones.
- **Cost:** a full portrait reading is **44 units** (Skin 14 + Colour Tones 20 + Face 10), each look layer 1–2, **repeat views 0** (cached). 1,000 free units from the redeem code; Cloudflare free tier.
- **Constraints:** YouCam unit budget; async task latency; sample cast of five photos; no store data.

## What the history shows
- Oct 27: idea (Jannet's: build on the skin scan stores already do), first build, global API host.
- Nov 1: live YouCam readings, hair-colour correction, catalogue outfits, deploy → Jannet's testing removed hair colour and asked for stacked looks, tabs, Camera Kit and "About you" → evening: the lip tint was nearly invisible at intensity 45 and darkened lips, so it was measured on three skin tones and calibrated.
- Nov 2: the impact section rewritten to measured-only claims ("the closing narration now cites the lip-depth measurement instead of an unmeasured 'fewer wrong buys'"), working files removed, submitted.

## Weak spots to own
- Five sample photos is a small cast for fairness claims. Say "on YouCam's sample cast".
- Built with Claude Code as the coding assistant; I picked the idea, tested on my own photos and made the product calls (drop hair colour, lip tint only, no retouching).

## Sources
`README.md` (what it does, impact, units, code), `src/server/api.ts` (KV cache, `UNIT_FLOOR`), `src/server/youcam.ts` (task polling), git log Oct 27 – Nov 2 (PRs #1–#3, commit bodies); [DSProjects#56](https://github.com/JannetEkka/DSProjects/issues/56) (submitted 11-02, Women in Tech, video, units left).
