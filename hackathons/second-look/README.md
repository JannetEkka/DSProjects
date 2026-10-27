# Second Look

Beauty counters already scan the shopper's skin. Second Look takes that scan and checks it against the basket they're about to buy and the products they already own at home. Every item gets **keep**, **swap** or **skip**, with the reason tied to the scan. A suggested swap can be tried on the shopper's own photo next to the original before they buy.

Built for the YouCam API Skin AI & eCommerce VTO hackathon. All brands and products in the demo store are made up. It gives cosmetic guidance, not medical advice.

## YouCam APIs used

| API | What it does here | Units |
|---|---|---|
| AI Skin Analysis (SD, 12 concerns including T-zone/U-zone skin type) | Oil, moisture, pores, texture, redness, under-eye and more drive the rules | 14 |
| AI Facial Color Tones Analyzer | The measured skin colour drives shade matching (CIEDE2000) and undertone | 20 |
| AI Makeup Virtual Try-On | Renders the product's own hex colour and finish on the shopper's photo, original and suggested side by side | 1 each |

## How it works

- `src/domain/check.ts` holds the rules: finish against oil and dryness, shimmer against pores and texture, fragrance and acids against redness, base shade against measured skin colour (ΔE2000 plus undertone), nudes that wash out against the skin, duplicates of products already owned, and what's missing.
- `src/domain/color.ts`: sRGB to CIELAB, CIEDE2000 (tested against Sharma et al.'s reference pairs), and undertone from the LAB hue.
- `src/domain/tryon.ts` turns a product into a Makeup VTO effect payload.
- `src/server/youcam.ts`: File API upload, starting tasks, polling.
- `src/server/api.ts` is the app's API on Cloudflare Pages Functions. The key stays on the server. Every result is cached in KV by image hash. Live calls stop when the account drops below `UNIT_FLOOR` units, and each visitor gets `LIVE_SCANS_PER_DAY` live scans.

## Run locally

```bash
npm install
npm test
npm run build
npx wrangler pages dev dist     # http://localhost:8788
```

Without a key, the sample shopper works and try-on is off. To use a key locally, put it in `.dev.vars`:

```
YOUCAM_HACK_API_KEY=...
```

## Deploy (Cloudflare Pages, free tier)

1. Run `npx wrangler kv namespace create CACHE` and put the id in `wrangler.toml`.
2. `npm run build && npx wrangler pages deploy dist`
3. `npx wrangler pages secret put YOUCAM_HACK_API_KEY`

## Licence

MIT
