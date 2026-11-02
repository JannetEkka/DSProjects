# Chithi: official Indian letters explained, every date and amount checked

**Meta Global AI Developer Hackathon (Cerebral Valley), Indie Developer track, Build for Your World.** Built Oct 27 – Nov 3, 2026, submitted Nov 3. Results Nov 9.
**Live:** [chithi-oprj.onrender.com](https://chithi-oprj.onrender.com) · **Code:** [github.com/JannetEkka/chithi](https://github.com/JannetEkka/chithi) · **Video:** [youtu.be/wlRwfQghgOw](https://youtu.be/wlRwfQghgOw) (2:47)

## The 30-second version

Electricity bills, bank reminders and tax demands in India arrive in formal English or official Hindi, and many people who get them can't read that register. An AI explanation helps, but a wrong due date or amount in it is worse than none. Chithi takes a photo of the letter and answers in Bengali, Hindi or English: how much to pay, the last date and the days left, and what happens if you don't. It can read the answer aloud, add a calendar reminder or share it on WhatsApp, and it takes follow-up questions by voice.

It's built as a verifiable agent. The model makes claims, each claim quotes the letter, and a check with no model in it decides what is shown. Every date and number the reader is told must be in the quoted words and in a second, separate reading of the photo. Anything that fails sits apart under "check these yourself". Tapping a point shows the piece of the reader's own photo where the letter says it.

**Measured** on synthetic letters (electricity bills, bank EMI reminders, tax demands, Hindi property-tax notices): 28 live explanations, 16 of them from folded, shadowed, blurred photos, **114 dates and amounts shown, 0 wrong**; the total to pay and the deadline were told on 16 of 16 hard photos. A stand-in explainer that gets a quarter of its values wrong had **53 of 53 planted errors held back**. About 20 s and $0.04 a letter by my estimate; Meta's billing showed under $1 used by submission.

**What isn't measured:** real letters. All test letters are synthetic, and on them Muse Spark made no reading mistakes, so the live runs show good readings, not the check catching a real model error. The stand-in run is what shows the check working.

## 1. Architectural reasoning

### Database / storage
- **None.** Each letter is one request; nothing about it is stored. Results for the example letters are cached in memory per language, so judges clicking examples don't spend credits.
- Test data is files: `letters/generate.py` renders each synthetic letter with Chromium (real Devanagari shaping), makes a phone-photo and a "hard" photo of it, and writes the true text and every date and amount to JSON.

### Compute & hosting
- **FastAPI on Render's free tier**, one process. The model work (15–30 s) runs in a thread pool; the first deploy ran it inside the async handler and a health check timed out during a live run, so that was the first fix after deploy.
- The page is plain HTML and JS, no build step. Progress streams from the server as newline-delimited JSON, so each step ticks off when it finishes.

### Frameworks & models
- **SAM 3.1** (one short noun phrase per request): "sheet of paper" finds and crops the page; "table", "rectangle" and "stamp" find the parts with amounts. "boxed text" and "text box" found nothing in tests.
- **Muse Spark 1.3**: reads the page; reads it again in five zoomed strips and the SAM regions (the second reading); writes the explanation as JSON to a schema; rewrites failed points once. Reasoning effort `minimal` for reading and `low` for explaining halved cost and time on the first letter ($0.076 → $0.043, 69 s → 32 s) with the same result; running the calls in parallel brought a letter to 13–23 s.
- **Muse Voice Transcribe** for spoken questions (Hindi and Bengali are among its 25 languages), recorded in the browser as 16 kHz mono WAV.
- Muse Spark Open on Baseten is wired in as an optional explainer but wasn't used.

## 2. Data & security pipelines

### Authentication & access control
- One Meta key for this entry (`META_HACK_API_KEY`), in the cloud environment and on Render, never in the repo. The account needed a card for the $150 credits; a spend-limit email is set at $150. The "Subscription plan: Muse Code" box on Billing is an upsell (₹399/month), not something the API needs; that nearly ended the entry.
- The public site caps use at 15 letters per visitor and 400 a day.

### Data flow
- Photo → SAM page crop → in parallel: SAM regions, full read, strip reads → explanation (starts as soon as the full read is done) → check → one repair round → result. Every step is in the trace on the page with model, time and tokens.

### Privacy
- While free credits are in use, Meta's billing page says content may be used for product improvement. The page says so next to the camera button and asks people to cover their name, address and account numbers. Contributor-tier models (cheaper, prompts used for training) weren't used.

## 3. Reliability & failure operations

### The check (`chithi/verify.py`, no model)
- Finds the quote in the letter text, exactly or as a near match (a reading slip), and from then on uses the letter's words, not the model's copy, so a misquoted amount can't vouch for itself.
- Reads every date and number in what the reader is told: Bengali and Devanagari digits, lakh and crore, `Rs.`/`₹`/`/-`, day-first dates, Hindi and Bengali month names. Each must be in the quoted words and in the second reading.
- A test button on the page changes one digit of one amount in the explanation, the kind of slip a model makes, and the page shows it held back with the reason in the reader's language.

### Error handling
- A failed SAM or model call fails the letter with a clear message; the page gives up after two minutes rather than spinning.

## 4. Evaluation & metrics

| run | letters | values shown | wrong shown | key facts told |
|---|---|---|---|---|
| clean photos, Oct 29 | 12 | 56 | 0 | (not counted yet) |
| hard photos, Nov 2 (after the prompt fix) | 8 | 27 | 0 | 16 / 16 |
| stand-in explainer, ~25% wrong on purpose | 40 | 147 | 0 (53 held back) | — |

"Key facts told" was added after a demo take where the Bengali explanation of a bank letter left out the total and the deadline. A missing point is invisible to the check, so it's now asked for in the prompt and measured.

## What the history shows (real decisions)

- **Asked Muse Spark for pixel boxes** to point at each amount on the photo. Pixel boxes were a line or more off, and 0–1000 normalised boxes were worse, so the page shows the smallest SAM region or strip whose separate reading contains the value instead. Always the right lines, sometimes a few more of them.
- **Fake progress timers replaced** with streamed steps after "the app is very mid"; the redesign put the answer (amount, date, days left, consequence) first and the evidence one tap away.

## Weak spots to own before they ask

- Synthetic letters only; real bills have stamps, logos, handwriting and two languages on one page.
- The check compares values with the quoted passage, not meaning: if one sentence holds two dates and the explanation pins the wrong one to the deadline, it passes.
- Both readings come from the same model; a shared misreading would pass.

## Sources

The repo README, `eval/results-*.json`, `demo/README.md`, and [DSProjects #40](https://github.com/JannetEkka/DSProjects/issues/40).
