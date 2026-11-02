# Beauty Within: Devpost form, field by field (paste-ready)

Working notes for the submission; not part of the submitted repo. Images are in `devpost/` next to this file.

## Project overview

**Project name**

Beauty Within

**Elevator pitch**

Hair, clothes and one lip tint chosen from your own colours and tried on your own photo with the YouCam API. Nothing about your face is retouched.

**Thumbnail:** `devpost/thumbnail.png`

## Project details

**About the project** (Markdown)

```markdown
## Inspiration

Every woman is already beautiful. A good haircut and the right lipstick go a long way, but confidence is what makes you shine. Most beauty try-on apps start by smoothing your skin and reshaping your face, so the "after" picture isn't really you. I wanted to start from the woman as she is and only show what suits her.

## What it does

Pick one of five sample portraits, take a photo with the camera, or upload one.

- **Camera.** YouCam's JS Camera Kit opens the camera and guides face position, size and lighting before it takes the photo.
- **Your colours.** The Facial Color Tones Analyzer measures skin, lip and eye colour, and the Face Analyzer reads face shape. Hair colour can be corrected with one tap.
- **One look, in layers.** An outfit, a hairstyle and a lip tint stack onto the same photo, in that order, and any of them can come off again.
  - **Clothes:** six colours picked from your undertone, the contrast between your skin and hair, and your eye and lip colour. Outfits from YouCam's clothes catalogue in those colours go on with AI Clothes.
  - **Hair:** styles from YouCam's hairstyle templates chosen for your face shape. AI Hairstyle keeps your own hair colour.
  - **Lip tint, the only makeup:** your own lip colour at the same depth, with a touch of rose, pink or red. It never goes darker or lighter, so it works the same for a deep-skinned woman and a fair one. Makeup Virtual Try-On runs with skin smoothing at 0.
- **Zoom to compare.** Tap any photo to open it full screen, tap again to zoom in on the lips or hair, and flip between "As you are" and "Your look" at the same zoom.
- **Care from within.** Tell the app your diet (vegetarian, eggetarian, non-vegetarian or vegan), weight, water, sleep, activity and time in the sun, plus your own hair and skin concerns. AI Skin Analysis shows what's already working first. Then each concern, and your lowest scan areas, get the nutrients involved, the published daily amounts for adult women (NIH Office of Dietary Supplements, National Academies), foods that fit your diet and a few habits, each with a source link. It's general information, not a prescription.

## How I built it

- React and TypeScript on the front end, Cloudflare Pages Functions for the API, so the YouCam key stays on the server.
- YouCam APIs: AI Skin Analysis, Facial Color Tones Analyzer, Face Analyzer, AI Clothes (v4), AI Hairstyle (v2.1 transfer), Makeup Virtual Try-On, and the JS Camera Kit in the browser.
- A look is built layer by layer: each try-on runs on the previous result. Every prefix of layers is cached in Workers KV, so changing one layer only re-runs from there, and a repeat view costs no API units.
- Colour maths in CIELAB with CIEDE2000, for lip depth, palette contrast and matching outfits to colours.
- 37 unit tests cover the colour maths, the response parsers, the care rules and the layer order.

## Challenges

- **The first lip tint was nearly invisible, and the engine darkens lips.** Measuring lips before and after showed Makeup Virtual Try-On makes lips about 5 L* darker. I calibrated against rendered lips on three skin tones: the colour sent is lifted so the result lands on her own lip depth, with enough added colour to see, capped for lips that are already rich in colour.
- **Hair colour changed her face.** YouCam's hair-colour try-on brightened the cheek and background by 10 to 13 points (RGB 0–255) as well as the hair, so I took it out. The point is not to change her face.
- **Undertone was unfair to deep skin.** Reading undertone from hue alone called every deep skin tone in the cast "cool", because deep skin sits redder in colour space. The reading now adjusts for depth, and a test checks it.
- **Hair read.** YouCam read two black-haired women as blonde, and gave no read for two more, so the user can fix the hair colour before the palette uses it.

## What I measured

On YouCam's own sample photos, on Nov 1:

- Lip depth: the default makeup render made lips about 5 L* darker; the calibrated render keeps her lip depth within about 2 L* on three lips (medium L*≈40, deep and saturated L*≈40, light L*≈63).
- Skin smoothing is 0 instead of the engine's default of 50.
- Cost: a full portrait reading is 44 API units, each layer of a look 1 or 2, and a repeat view 0.

What I haven't measured is whether this lowers wrong-shade purchases or returns. There's no baseline yet. A store could measure it by comparing return rates for lip shades and outfits bought after a Beauty Within try-on against those bought without one.

## What I learned

Try-on engines come with defaults that quietly change a face: skin smoothing at 50, lips rendered darker. The only way to keep a promise like "never darker" was to measure the rendered pixels and calibrate against them. Colour rules also need to account for skin depth, or they fail deeper skin first.

## What's next

- A store mode that loads a retailer's own lipstick and clothing catalogue and matches it with the same rules.
- Full-length photos, so dresses and trousers can be tried on whole.
```

**Built with** (tags)

react, typescript, vite, cloudflare-pages, cloudflare-workers, cloudflare-kv, youcam-api, perfect-corp, ai-skin-analysis, makeup-virtual-try-on, ai-clothes, ai-hairstyle, face-analyzer, js-camera-kit, cielab, vitest, playwright

**"Try it out" links**

- https://beauty-within.pages.dev
- https://github.com/JannetEkka/beauty-within

**Image gallery** (in this order): `devpost/gallery-0-lip-tint-close-up.png`, then `gallery-1` to `gallery-9`.

**Video demo link**

https://youtu.be/ATzI4K94w44

## Additional info

**Upload a file:** leave empty.

**Sponsor / Special Prizes:** tick **Women in Tech Special Award**. Leave Rising Star unticked.

**Submitter type:** Individual

**Country of residence:** India

**App status:** New

**Text description: features, functionality, and consumer or retail value**

Beauty Within is a web app that starts from the woman as she is. From one photo (sample portrait, camera through YouCam's JS Camera Kit, or upload), the Facial Color Tones Analyzer reads her skin, lip and eye colour, the Face Analyzer reads her face shape, and AI Skin Analysis reads her skin. From those it suggests clothes in her colours (outfits from YouCam's catalogue, tried on with AI Clothes), hairstyles for her face shape (AI Hairstyle, keeping her own hair colour) and one lip tint made from her own lips at the same depth (Makeup Virtual Try-On, skin smoothing 0). The three stack into one look on her own photo, and she can zoom in to compare with "as you are". A Care tab takes her diet, habits and hair and skin concerns and lists nutrients with the published daily amounts, foods that fit her diet, and habits, each with a source.

Consumer and retail value: every suggestion is something that suits her as she is, seen on her real, unretouched face before she buys. For a store, the lip tint is a shade it can stock and the outfits are its own products, ranked for her. Measured: the calibrated lip render keeps lip depth within about 2 L* where the default made lips about 5 L* darker. Not yet measured: the effect on returns; a store could test it by comparing return rates with and without a try-on.

**Code repository URL**

https://github.com/JannetEkka/beauty-within

**Was there a moment during the hackathon where the API surprised you, in a good or frustrating way?**

Both. The good surprise: Makeup Virtual Try-On left every pixel outside the lips exactly as it was (I diffed the images), and AI Clothes changed the top while keeping her face, hair and earrings untouched. The catalogues were a gift too: 99 women's hairstyle templates and 250 outfits meant I could build a real store-style catalogue without shooting a single garment. The frustrating ones: the hair-colour try-on brightened the whole face by 10 to 13 points along with the hair, so I dropped it; the makeup engine renders lips about 5 L* darker than the colour you send, which I had to calibrate around; the hair-colour read called two black-haired women blonde; and cloth-v4 doesn't take a template_id, so I pass the template's own photo as the reference instead.

**Are there industries or use cases you think Perfect Corp.'s API could serve that nobody is talking about yet?**

- Shade-range testing for cosmetics brands: render every shade in a range on photos across skin depths and measure the result before launch, to catch shades that turn grey or ashy on deeper skin. That's the measurement loop I ran for one lip tint, at catalogue scale.
- Wig shops and hair-loss support: hairstyle transfer that keeps a person's own colour lets someone try styles privately before choosing a wig.
- Resale and rental fashion: one-off pieces usually have a single photo. AI Clothes takes that photo as the reference, so a second-hand seller can offer try-on without studio shots.
- Occasion and traditional wear in India, such as sarees, lehengas and kurtas, where trying on is a big part of buying and the catalogue already has cultural attire.

**Where did you hit a wall technically? How did you work around it?**

- Lip colour: the tint was invisible at low intensity and darkened lips at higher intensity. I measured rendered lips on three skin tones and now send a colour lifted by an amount that depends on lip lightness, at intensity 75, so the result keeps her lip depth within about 2 L*.
- Photo framing: the colour and skin readers need the face to fill most of the image, but clothes try-on needs a chest-up photo. Users frame their face once with a square; the face crop goes to the readers and the full photo to the try-ons.
- Stacking: each try-on returns a new image. I upload the previous result through the File API to run the next layer, and cache every prefix in Workers KV, so changing the lip tint doesn't re-run the outfit and hairstyle.
- Camera Kit: its YMKAsyncInit hook didn't fire when the script loaded after the page, so I start it from the script's load event.
- Units: 1,000 free units for building, a demo and judging. Sample readings were recorded once, every result is cached, and live calls stop below a 150-unit floor.

**Social posts:** leave empty (or add the links if you post for the Share & Earn bonus before 22:15 IST).

**Terms & conditions:** tick.
