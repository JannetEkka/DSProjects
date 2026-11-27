# Orbit: elder care and medication, built in one day

**Catalyst: Solo AI Hackathon (Makers Need More × PromptWars, Hack2skill), Sun Nov 15, 2026.** Solo, one day: challenge revealed at 09:00, submitted on Hack2skill by 16:00 IST. **Result: top 8.2%, 33rd of 391 scored entries (32 scored higher); automated score 96.64 against the winner's 97.21; not placed.**
**Live:** [orbit-care.onrender.com](https://orbit-care.onrender.com) (free instance; first load can take a minute) · **Code:** [github.com/JannetEkka/orbit-care](https://github.com/JannetEkka/orbit-care) · tracker [DSProjects#109](https://github.com/JannetEkka/DSProjects/issues/109)

**Reminders switched off on 11-27:** the `reminder-tick` workflow was disabled and the Brevo key removed from Render, so no more emails go out. The site stays up as a demo.

## The 30-second version

Challenge: an elderly care and medication platform. Jannet's idea: a reminder app doesn't help a parent who can't use a phone; what helps is the people around them knowing whether someone actually gave the 1 pm dose. So the elder gets one big button by the bed that speaks at dose time and turns the screen into the tablet's colour, and the care circle (family, nurse, doctor) shares a record where every dose has a named giver. Not marked 30 minutes after it was due, it's missed and the giver is reminded; after 60, the whole family is told.

## 1. Architectural reasoning

- **One Python service** (FastAPI) serves the bedside, circle and doctor screens and the API. Render free plan with PostgreSQL; a tested Google Cloud path (Cloud Run, Firestore, Cloud Scheduler, Secret Manager) because the top 10 needed a Cloud Run link.
- **One storage interface, three backends:** PostgreSQL, Firestore (tested against the emulator) and in-memory for local runs.
- **The reminder check runs every 5 minutes:** the app itself on Render, with a GitHub Actions workflow as a second caller; Cloud Scheduler on GCP.
- **Email over Brevo's HTTPS API**, because Render's free plan blocks outgoing SMTP.

## 2. Data & security pipelines

- Passcode sign-in, as the challenge asked: an orbit code plus a 6–12 digit personal passcode, stored as a salted scrypt hash and compared in constant time. A keyed HMAC fingerprint finds the person, so sign-in runs one slow hash, not one per member. Weak codes refused; 15-minute lockout after 5 wrong tries; `__Host-` cookie, COOP/CORP headers.
- Roles decide access: doctor read-only; bedside can confirm a dose, answer "how are you" and call for help; family can change everything.
- Secrets live in the host's environment settings (Render or Secret Manager), none in the repo.

## 3. Reliability & failure operations

- **Fixed rules make every decision** (`app/rules.py`), each covered by a test. Gemini only writes words: the evening update, the pre-visit summary, suggested note tags. If its text contains a number that isn't in the record, the template is used instead. Without a Gemini key everything still works.
- Missed dose to the whole family knowing: at most 65 minutes with the defaults (60 + up to 5 until the next check); families can shorten it.

## 4. Evaluation & metrics

| | Attempt 1 | Attempt 2 (final) |
|---|---|---|
| Overall (automated) | 94.29 | **96.64** |
| Code quality | 88 | 88 |
| Security | 99 | 99 |
| Efficiency | 80 | 100 |
| Testing | 98 | 98 |
| Accessibility | 98 | 98 |
| Problem alignment | 100 | 100 |

- Between attempts: one slow hash per sign-in, cached Gemini answers, gzip and cache headers; WCAG AA contrast fixes (axe-core: 0 violations on 18 page states); tests from 65 to 106 (165 with Postgres), 92% line coverage.
- Gemini check: 18 of 20 real summaries passed the number check, 0 rejected, 2 timed out and fell back to the template; median reply 0.81 s.
- Ranking: 33rd of 391 scored entries (top 8.2%), 0.57 below the winner.

## What the history shows (real decisions)

1. 10:50 IST: built and pushed; waiting on Google Cloud. Moved to Render with Postgres for the live link and kept the Cloud Run path tested.
2. Dependabot opened 5 branches within a minute of being added, against the "one branch only" rule. Jannet deleted two before submitting. Lesson recorded: no Dependabot on a one-branch hackathon repo.

## Weak spots to own before they ask

- "As needed" and tapering doses aren't modelled. Email is the only alert channel; calls are tap-to-call buttons.
- Not a medical device; no real families used it.
- The automated score grades code; it says nothing about whether families would use it.

## Sources

The orbit-care README (rules table, security, measured); DSProjects#109 body and comments (scores, changes between attempts, ranking from Jannet, 11-16).
