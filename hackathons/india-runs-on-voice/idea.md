# India Runs on Voice — Round 1 texts: Mera Hisaab

Picked by Jannet on 11-16 (idea 1 of 3). The functional design is in [design.md](design.md). Tracking issue: #89.

**How to use this file:** these are talking points to **say** through Wispr Flow, in your own words, not a script to read. Facts marked **(say exactly)** are the ones to keep word for word, because they're sourced. Then read what Flow typed, fix anything it misheard, and submit. The quality check gives feedback, and you can edit and resubmit.

Word limit for Activity 1: 50–500. Speaking these points naturally lands around 250–350 words.

---

## Activity 1 — Idea (submit as soon as possible; Activity 2 is locked until this is in)

### 1. The problem
- A domestic worker who cooks or cleans in four homes is paid by each one at month end.
- Each employer decides the "leave cut" from memory. She remembers 2 leaves; they remember 4. Nobody wrote anything down.
- So she can only argue from memory, against someone who pays her. Most of the time she just takes the lower amount.
- A day they told her not to come gets counted as her leave. That mix-up is where the money goes.

### 2. Who has it, where, how often
- Live-out domestic workers in Indian cities: maids, cooks, cleaners, who work in several homes each.
- **(say exactly)** "A 2020 WIEGO survey of 176 domestic workers in Delhi NCR found 74 percent worked live-out for several employers, and almost none had a written contract."
- It happens every month, in every home she works in. You'll find it in almost any city housing society.

### 3. The product, step by step (Mera Hisaab, "my account")
- Once, for each home, she says it: "Sharma ji, three thousand a month, Sunday off, two leaves free."
- Every evening the app asks, "Did you go to every house today?" She says "haan", and the day is logged for every home.
- If something was different, she says it: "Mehra ji's house was locked." "Gupta ji told me not to come yesterday." "Took 500 advance from Sharma ji."
- It reads every entry back, house, date and what happened, and saves nothing until she says "haan".
- At month end she asks, "Sharma ji ka hisaab?" It answers out loud: how much, her leave dates, and the days they cancelled, which aren't her leave.
- If a day is missing from the record, it asks her to fill it before it gives any total. A wrong total is worse than none.
- She can send the employer a short summary with the dates, in the employer's language, on WhatsApp.
- Works in Hindi, Bengali, and mixed speech.

### 4. Why voice comes first
- Her hands are busy or wet all day, and many workers read little. A form with dates and dropdowns would never get filled in.
- She already talks to her employers through WhatsApp voice notes. Speaking one line a day fits how she already works.
- Apps for this already exist, like ApnaStaff, but they are for the employer, are tapped, and keep the employer's version. Mera Hisaab is the worker's own record, kept by talking.

---

## Activity 2 — Prompt (opens after Activity 1 is submitted)

The task: turn the idea into a prompt an AI app builder could use for a prototype. This is the functional prompt; UI polish comes later. Dictate it in sections; it's fine to say "next section". Roughly 350 words spoken.

> Build a mobile-first web app called Mera Hisaab, for a domestic worker who works in several homes and wants her own record of every day, kept by voice.
>
> **Voice in, voice out.** Every action is spoken: a big microphone button, and every reply is read aloud. Support Hindi, Bengali and English, including mixed speech.
>
> **Houses.** She sets up each home by voice: name, monthly pay, weekly day off, free leaves per month, and whether this home cuts pay when it tells her not to come. Read the card back and save only after she says yes.
>
> **Daily log.** Each evening, ask "Did you go to every house today?" Yes marks all houses as worked. Otherwise she describes the day. Day types: worked, her leave, told not to come, house closed, half day, weekly off, extra work with an amount, advance with an amount.
>
> **Use the AI only to turn her words into fields:** house, a date phrase like today, yesterday, day before yesterday, a weekday, a date or a range, the day type, and an amount. Turn the date phrase into a calendar date in code, not with the AI. If the house, date or amount is unclear, ask one short question. Never guess.
>
> **Read back every entry** with house, date and type, from a fixed sentence template, and save only after she says yes. Never edit a saved entry; a correction adds a new entry and keeps the old one in the history. Mark entries logged on a later day as late.
>
> **Month end.** When she asks for a house's account, first check every day of the month has an entry for that house. If any are missing, list them and give no total. Otherwise calculate in code: per-day rate is monthly pay divided by 30; leave cut is her leaves minus free leaves, never below zero, times the per-day rate; half day counts as half a leave; employer-cancelled days are not cut unless that house's setting says so; subtract advances, add extras; round to whole rupees at the end. Speak the total, her leave dates and the employer-cancelled dates, and show the month as a calendar.
>
> Every number or date the app speaks must come from the calculation.
>
> **Share.** Make a short summary for the employer in their language, to send on WhatsApp.
>
> Keep all data on the phone. Include a demo month with three houses to test with.

---

## Activity 3 — Impact (opens Nov 20)

Three questions: who benefits, what changes for them, how you'd know. Draft talking points; we'll tighten them on Nov 20.

### Who benefits
- Live-out domestic workers working in several homes in Indian cities. **(say exactly)** The WIEGO figure above: of 176 domestic workers surveyed in Delhi NCR in 2020, 74 percent worked live-out for several employers, and almost none had a written contract. One region and a small sample, so say it as that.
- Employers too: one dated record ends the month-end argument for both sides.
- Size, only if we can cite it: e-Shram has about 2.89 crore registrations under domestic and household work, according to a secondary summary of the Labour Ministry's March 2025 data. **Not verified yet; check against the official PIB annexure before saying it.**

### What changes for them
- Before: she argues from memory against someone who pays her, and usually takes the lower amount.
- After: she has dated entries for every day in every home, a total worked out the same way every month, and her leave kept apart from the days they cancelled.
- Example from our own worked case (design.md section 3): Sharma ji counted 4 leaves and would have paid ₹2,800. Her record shows 2 leaves, both free, so ₹3,000. This is a worked example, not a measured result; say it that way.

### How you'd know
- **We measure it ourselves:** (1) of about 40 spoken log lines in Hindi, Bengali and mixed speech, how many the app gets fully right before her confirmation; (2) on a synthetic month for 3 houses with a known true amount, rupees off per house for an AI asked alone vs our calculator.
- **In a pilot:** a month with a few workers, comparing what each house paid with what her record says, and counting how many times she raised a dispute with dates in hand, and how many of those got paid.
- **What we don't claim:** how much workers lose today. Nobody we found has measured it; the pilot is how we'd find out.

---

## Sources
- WIEGO Policy Brief No 21, "Domestic Workers, Risk & Social Protection in Delhi National Capital Region" (Nov 2020), survey of 176 workers in Delhi, Faridabad and Gurgaon; verified 11-16: https://wiego.org/wp-content/uploads/2021/02/WIEGO_PolicyBrief_N21%20Delhi%20for%20web.pdf
- e-Shram registration totals (Labour Ministry via PIB): https://labour.gov.in/sites/default/files/pib2109828.pdf ; domestic-work breakdown (secondary, unverified): https://www.sightsinplus.com/news/survey-report/over-30-crore-unorganised-workers-registered-on-e-shram
- Closest existing products: ApnaStaff https://mwm.ai/apps/apnastaff/6761162442 · Househelp https://peerlist.io/piyushh/project/househelp--track-attendance--manage-staff · ADDA https://ind.adda.io/staff-management · Shram Setu (concept) https://solve.mit.edu/solutions/58106
