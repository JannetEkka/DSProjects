# Chithi

Photograph an official Indian letter (an electricity bill, a bank notice, a tax demand) and get it explained in Bengali, Hindi or English. Before a date or a rupee amount is shown, a program checks it against the letter. Points that fail the check are shown apart, under "check these yourself", never as fact.

*Chithi* (চিঠি, चिट्ठी) means "letter".

Built for the Meta Global AI Developer Hackathon (Cerebral Valley, October–November 2026), Indie developer track, problem statement "Build for Your World".

**Status (Oct 27):** the check, the pipeline, the synthetic test letters, the evaluation and the web page work. Meta's models are wired in from their docs but not yet called with a key; until then the app runs in demo mode on the sample letters, with a stand-in explainer.

## Why

In India, these letters arrive in formal English or official Hindi. Many people who get them can't read that register, and ask a neighbour or a grandchild. An AI explanation helps, but a wrong due date or amount in it is worse than no explanation. Chithi is built so that nothing with a number in it reaches the reader unchecked.

## How it works

Chithi is a verifiable agent: the model writes claims, each claim carries its evidence (the letter's own words), and a deterministic verifier decides what the reader sees.

1. **Find the page.** SAM 3.1 segments the sheet of paper in the photo, and Chithi crops to it.
2. **Find the parts that matter.** SAM 3.1 finds tables, stamps and boxed text on the page.
3. **Read the page.** Muse Spark transcribes the whole page, exactly as printed.
4. **Read it again.** Muse Spark reads each SAM region, and the page in three overlapping strips, zoomed in. This second reading is done separately from the first.
5. **Explain.** Muse Spark writes 3 to 7 points in the reader's language. Each point has what to tell the reader and the exact words of the letter it rests on.
6. **Check.** For each point, [`chithi/verify.py`](chithi/verify.py):
   - finds the quoted words in the letter (exactly, or nearly, to allow for a small reading slip) and from then on uses the letter's words, not the model's copy;
   - reads every date and number in what the reader will be told, in English, Hindi or Bengali, with Indian and native digits, lakh and crore, and day-first dates;
   - requires each one to be in those words of the letter, and in the second reading.
7. **Repair once.** Points that failed go back to Muse Spark with the reasons. The rewritten points are checked again.
8. **Show.** Verified points as fact, each with the letter's words under it. The rest under "check these yourself", with the reason.

No model takes part in step 6. The page shows every step, which model ran it and how long it took.

Spoken questions in Bengali or Hindi go through Muse Voice Transcribe, and the answer goes through the same check.

### Meta models used

| Model | What for | Why this one |
|---|---|---|
| SAM 3.1 | Finding the page in the photo; finding tables, stamps and boxes on it | Crops let the reader zoom in on the parts with amounts; the boxes are drawn on the photo |
| Muse Spark 1.3 | Reading the page, reading the crops again, explaining, repairing | Reads images, writes Bengali and Hindi, and returns JSON to a schema |
| Muse Voice Transcribe | Spoken questions | Hindi and Bengali are among its 25 languages |
| Muse Spark Open (Baseten) | The explainer, as an option (`CHITHI_EXPLAINER=spark-open`) | An open-weight model for the same job, measured the same way |

Chithi uses the standard Muse Spark tier, not the cheaper contributor tier, because contributor-tier prompts may be used for training and these are people's letters.

## Measured

The test set is 40 synthetic letters ([`letters/generate.py`](letters/generate.py)): electricity bills, bank EMI reminders and tax demands in English, and property-tax notices in Hindi. All senders and people are made up, and every page says "SYNTHETIC SAMPLE". Each letter is rendered as a clean page and as a phone photo (tilted, shaded, on a table), and comes with its true text and every date and amount on it.

[`eval/run.py`](eval/run.py) explains each letter in Bengali, Hindi or English and counts the dates and numbers shown to the reader as verified that are not on the letter. It compares them with the generator's true text, so a misreading of the photo counts as an error too.

**With Meta's models:** not measured yet (needs the API key).

**The check alone**, with a stand-in explainer that gets about a quarter of its values wrong on purpose (`--backend mock --no-repair`):

| letters | points | verified | held back | values shown | wrong values shown | wrong values held back |
|---|---|---|---|---|---|---|
| 40 | 200 | 147 | 53 | 147 | 0 | 53 |

This measures the check, not the models: every planted error was held back.

### What the check can't catch

- It checks values against the quoted passage, not meaning. If one sentence of the letter holds two dates and the explanation pins the wrong one to the deadline, both are "in the quote" and the point passes.
- If both readings of the photo get the same digit wrong, the check can't know. The two readings are separate calls on different crops, which makes this less likely, but they come from the same model.
- Points without numbers pass when their quote is found; the wording around the quote is the model's.

## Run it

```
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
pytest
uvicorn chithi.app:app --reload        # http://localhost:8000
```

Without a key the app runs in demo mode on the sample letters. With `META_HACK_API_KEY` set, it calls Meta's models and takes any photo. `META_HACK_BASETEN_API_KEY` with `CHITHI_EXPLAINER=spark-open` switches the explainer to Muse Spark Open on Baseten.

Regenerate the letters (needs Chromium through Playwright): `python letters/generate.py --n 40`.

## Built during the hackathon

All the code here was written from scratch during the event, from October 27, 2026. The idea comes from my earlier project [Klarbrief](https://github.com/JannetEkka/klarbrief), which does a similar check for Swiss official letters on a different model. No code from it is used here.

The sample letters are synthetic and were made for this project. The fonts in `letters/fonts` are Noto (SIL Open Font License).

## Limits

Chithi doesn't give legal or financial advice, and it says so. It is not meant for medical letters. It has been tested only on synthetic letters.

MIT licence.
