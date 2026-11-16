# Design brief: India Runs on Voice (Scaler × Wispr Flow) — Mera Hisaab

Status: **draft, functional design only**. UI comes later (Jannet, 11-16: "make it functionally well made, then we work on UI/UX"). Not signed off yet. Tracking issue: #89. The Activity 1–3 texts are in [idea.md](idea.md).

## 0. The hackathon, in one screen

- **Link:** https://hackos.scaler.com/wispr/ · dashboard https://hackos.scaler.com/wispr/dashboard.html
- **Round 1 (text only), closes Nov 26:** Activity 1 Idea (open now), Activity 2 Prompt (opened Nov 13, locked until Activity 1 is in), Activity 3 Impact (opens Nov 20).
- **Round 2, Nov 27–29:** a build. The page says **one problem statement for everyone**, released Nov 27. So Mera Hisaab may not be what we build in Round 2; this brief is for Round 1 and for Round 2 if the statement fits.
- **Finale:** in person on campus, Dec 13. Travel would be our own money; Jannet decides later.
- **Rules that bind us:** submissions dictated through **Wispr Flow**, signed in with the registered email. Any Indian language. Solo or a team of up to 3.
- **Judging:** criteria and weights aren't published; the page says each round's criteria come with that round.
- **Money:** free to enter. Nothing in Round 1 needs a paid service.

## 1. The idea

**One sentence:** a domestic worker who cleans or cooks in several homes keeps her own record of every day, by speaking a line a day, so at month end she can say exactly what each house owes and on which dates.

**The problem:** live-out domestic workers are paid monthly by each home, and each employer works out the "leave cut" from memory. There is no written contract and no shared record, so the worker can only argue from memory too. In a 2020 survey of 176 domestic workers in Delhi NCR, "most (74 per cent) domestic workers were employed in live-out, multiple-employer type arrangements … and almost none had written contracts" ([WIEGO Policy Brief No 21, Nov 2020](https://wiego.org/wp-content/uploads/2021/02/WIEGO_PolicyBrief_N21%20Delhi%20for%20web.pdf), wording checked 11-16).

**Why it's not the obvious idea:** the track example for small business is "voice bookkeeping for shopkeepers". Ours is bookkeeping for the person with the least paperwork in the arrangement, and its use is evidence in a pay conversation.

**Closest existing products (lessons 0, searched 11-16):**
- [ApnaStaff](https://mwm.ai/apps/apnastaff/6761162442), Aangan, [Househelp](https://peerlist.io/piyushh/project/househelp--track-attendance--manage-staff), [ADDA staff management](https://ind.adda.io/staff-management): attendance and salary for household staff, all used by the **employer**, tap-based. They hold the employer's version.
- [Shram Setu](https://solve.mit.edu/solutions/58106) (MIT Solve): a concept for multi-employer domestic workers, no build found.
- **What we do differently:** the worker owns the record, it covers all her homes in one place, and it's spoken in her language.

**Considered and not picked:**
- VB-G RAM G (ex-MGNREGA) work demand with a dated receipt and a 15-day countdown: strong civic case and no app found, but it takes a paragraph of law to explain in 500 words.
- "Did I already take it?" medicine log for elders: dropped under lessons 0; Medi-Mate, Echo Health, edesy and Alexa reminders are too close.

## 2. The measured comparison (decide before building)

Three measurements. Only the first two can be run by us; the third needs real workers.

1. **Does it hear the day right?** Jannet (and anyone willing) records about 40 spoken log lines in Hindi, Bengali and mixed speech, including relative dates ("parson"), ranges ("10 se 20 tak bahar hain"), advances and corrections. Report: entries where house, date, day type and amount are all correct, out of 40. Then: how many wrong entries would have been saved if she hadn't confirmed the read-back (by design 0 are saved without her "haan", so the number to report is how many read-backs she had to correct).
2. **Does it add up right?** A synthetic month for 3 houses with a known true amount owed by each. The same spoken log goes to (a) an LLM alone, asked "how much does each house owe?", and (b) Mera Hisaab's calculator. Report rupees off per house for each. If the LLM alone gets it right, we say so.
3. **Does it change the month-end conversation?** Not measured, and we don't claim it. How to measure: a one-month pilot with a few workers, comparing what each house paid with what the worker's record says, and counting disputes she raised with dates in hand.

No invented baseline: we will not say "workers lose ₹X a month" unless a source says it.

## 3. What a judge sees in the first 10 seconds

The worker asks out loud, "Sharma ji ka hisaab?", and hears back: "₹3,000, nothing to cut. You took 2 leaves, the 9th and the 21st, and 2 are free. On the 14th they told you not to come, so that's not your leave." Sharma ji counted 4 leaves and was going to pay ₹2,800. On screen, Sharma ji's month as a calendar with 2 days marked as her leave and 1 marked as theirs. (Worked with section 6: ₹3,000 ÷ 30 = ₹100 a day; 4 − 2 free = 2 × ₹100 = ₹200 cut on Sharma ji's count, ₹0 on hers.)

Headline (draft): **"Her days, her record."** Look and colour: later, in the UI pass.

## 4. Architecture

```
 voice ──► speech-to-text ──► PARSER (model) ──► VALIDATOR (code) ──► READ-BACK (code template)
                                                     │  unknown house / date / amount?     │
                                                     └── asks one question ◄───────────────┤
                                                                                           ▼ "haan"
                                                                               DAY LOG (append-only)
                                                                                           │
 "Sharma ji ka hisaab?" ──► QUERY PARSER (model) ──► CALCULATOR (code) ──► ANSWER (template, every number from the calculator)
                                                                                           │
                                                                               share note for the employer (text + voice)
```

**Model judgment vs fixed rules (lessons 4: let the model describe, let code decide):**

| Step | Who decides | Why |
|---|---|---|
| Turning speech into fields: which house, which day words, which day type, any amount | **Model** | Mixed languages, nicknames for houses, loose phrasing |
| Turning day words into a calendar date ("kal", "parson", "Tuesday", "10 se 20") | **Code** | A wrong date is the whole dispute; the model only names the phrase type |
| Whether the house exists, the date is in range, the amount is a number | **Code** | Validation; anything unknown becomes a question, never a guess |
| The read-back sentence | **Code template**, per language | So the confirmation can't say something the log doesn't |
| Pay, leave count, deductions, advances, extras | **Code** | Money |
| Polishing the spoken answer | Model allowed, then a guard: every number and date in it must match the calculator's output, or the template version is spoken | Same check as Chithi |

**Storage:** on the phone (local), one log per worker. Nothing leaves the phone unless she shares a month's summary.

**Services:** speech-to-text that handles Hindi, Bengali and code-mixing, and one LLM call per log line. Which provider: decide at build time, free tier only.

## 5. The flow, step by step

**Setup, once per house (spoken):**
1. She says: "Sharma ji, teen hazaar mahina, Sunday chhutti, do chhutti maaf." (₹3,000 a month, Sunday off, 2 leaves allowed a month.)
2. The app reads back the house card: name, monthly pay, weekly off, free leaves, and asks one setup question: "If Sharma ji tells you not to come, do they cut pay?" Default: no.
3. She says "haan" and the card is saved. Changing a card later keeps the old one for past months.

**Every day (about 10 seconds):**
4. At a time she picks, the app asks "Aaj sab ghar gayi?" A "haan" marks every house as worked today.
5. Or she says what was different: "Mehra ji ke ghar tala tha", "kal Gupta ji ne mana kiya", "Sharma ji se 500 advance liya", "Sunday ko Gupta ji ke yahan party thi, 300 extra".
6. The parser turns it into entries: house, day phrase, day type, amount.
7. The validator resolves the date and checks everything. An unknown house, a date it can't place or a missing amount becomes one short question.
8. The read-back: "Mehra ji, 14 November, ghar band. Theek hai?" Nothing is saved until she says "haan". "Nahi" lets her say it again.
9. Saved entries are never edited in place. A correction ("nahi, woh Gupta ji the") adds a new entry that replaces the old one, and both stay in the history with the time she said them. Entries logged days later are marked as late.

**Day types:** worked · her leave · told not to come (employer) · house closed / family away (employer) · half day · weekly off · extra work (with amount) · advance taken (with amount).

**Month end:**
10. She asks "Sharma ji ka hisaab?" (or "is mahine kitne chhutti li Sharma ji ke yahan?").
11. If any day in that month has no entry for that house, the app says how many and which, and asks her to fill them. **No total is given while days are unknown** (lessons 8).
12. The calculator works it out (rules below), the answer is spoken, and the calendar shows it.
13. If she wants, it makes a short message for the employer, in the employer's language: total, her leave dates, their cancelled dates, advances. She sends it on WhatsApp herself.

## 6. Decisions settled now (change any of these, Jannet)

- **Per-day rate** = monthly pay ÷ 30. A house can be set to ÷ days in the month instead.
- **Leave cut** = (her leaves in the month − free leaves, never below 0) × per-day rate.
- **Employer-caused days** (told not to come, house closed) are not cut, unless she said at setup that this house cuts them. They're always listed separately, because that's where disputes are.
- **Half day** = half a per-day rate, counted the same way as a leave.
- **Weekly off** isn't a leave.
- **Advances** are subtracted in the month she took them, unless she says they're being paid back over several months.
- **Extras** are added in the month they happened.
- **Joining or leaving mid-month:** pay for the days from the first to the last day she worked there, at the per-day rate.
- **Rounding:** whole rupees, at the end only.
- **Out of scope for now:** sharing the log with the employer live, several workers on one phone, government schemes, bank transfers.

## 7. Acceptance conditions (functional; UI conditions come with the UI pass)

- [ ] Setup works for 3 houses by voice in Hindi and in Bengali.
- [ ] "Aaj sab ghar gayi?" + "haan" logs every house for today.
- [ ] Relative dates resolve right for: aaj, kal (yesterday), parson, a weekday name, a date number, a range.
- [ ] Nothing is saved without a "haan" to a read-back that names house, date and type.
- [ ] Corrections keep history; late entries are marked.
- [ ] An unknown house or date leads to a question, never a guess.
- [ ] A month with any unknown day gives no total, and names the missing days.
- [ ] The calculator matches hand-worked totals on the synthetic month (all 3 houses, ₹0 off).
- [ ] Every number and date in a spoken answer equals the calculator's.
- [ ] The employer message has the total, her leave dates, their cancelled dates and advances.
- [ ] Measurements 1 and 2 from section 2 are run and reported, good or bad.

## 8. Demo plan

Later, after the Round 2 problem statement (Nov 27) and the UI pass.

## 9. Jannet's check

Before sign-off, in your own words:
- Why does code turn "parson" into a date, and not the model?
- Why does the app refuse to give a total when a day is missing?
- What's the difference between "her leave" and "told not to come", and why is it the heart of the product?
- Walk through Sharma ji's month end to end with the rules in section 6.
- What have we measured, and what have we only proposed?

**Signed off:** _not yet_

## 10. The build prompt

Not written yet. Round 2's problem statement comes out Nov 27; write this after reading it. The Activity 2 prompt in [idea.md](idea.md) is the Round 1 version.
