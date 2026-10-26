# SQL Noir: demo video script (Jannet narrates)

About 3 minutes, inside the 1–4 minute limit. One take per scene is fine; trim the waits in Clipchamp afterwards. The words in quotes are a guide, so say them your way.

The organisers want the video to show: the main workflow end to end, how the agent solves Track 02, the key features, and how Zetaris and Meterless are integrated, including what's unusual about our use of them.

## Before you record (10 min)

1. Restart Windows if it's been on a while, then start **Docker Desktop**, Zetaris (`cd ~/zetaris-platform && docker compose start` in Ubuntu) and **Nightshift**. Close other apps: memory is tight.
2. In Cursor's terminal, in `D:\code\sql-noir`, start fresh so the validator runs live on camera:
   ```powershell
   git pull
   Remove-Item -Recurse .data
   npm start
   ```
3. Open **http://localhost:4321** in Chrome. Don't run `validate:cases` after the reset: then the first case is checked live on camera, which is the point of scene 2. Hide the bookmarks bar (Ctrl+Shift+B) and make the window full screen (F11).
4. Have these ready, but out of sight:
   - Cursor open on `D:\code\sql-noir`, with a second terminal where `npm run conformance:hmem` is typed in but not yet run;
   - Nightshift's **MONITOR** panel.
5. Open the Windows **Clipchamp** app → **Record & create** → **Screen recording** (with your microphone). Pick the Chrome window, then switch windows during the take for scene 7, or record that scene as a separate clip.
6. Do one practice run, then reset again (stop the game, `Remove-Item -Recurse .data`, `npm start`).

## Scenes

**1. Hook (0:00–0:15).** The page is open on the welcome ("New in town, detective?"), with "Rookie 0 pts" in the header.
> "This is SQL Noir, a detective game that teaches SQL on real data. You crack cases by writing queries. Every answer is checked against the data in Zetaris, and your partner Nemo, who runs on NVIDIA Nemotron through Meterless Nightshift, tells you why you're wrong, with evidence."

**2. A case that's been checked (0:15–0:45).** Click **Take your first case**. The spinner runs while the validator checks the case on Zetaris; trim most of the wait later. Point at the agent trace at the bottom.
> "The game master picks a case. Before I see it, the validator runs the case's own answer on Zetaris and checks it: read-only, it has an answer, the answer is small, it's the same twice, and there's no tie at a cut-off. That's every line in the trace. Earlier it threw out two of my own cases because of a tie and a query too heavy for a laptop."

Read the case on screen ("Damaged goods": list the return reasons that mention damage). Point at **The files** under the question.
> "The case file tells me which tables I need. Zetaris describes them: columns, types and a few sample rows. I click a name to drop it into my query."

**3. Wrong on purpose (0:45–1:15).** Type `SELECT * FROM TPCDS_DB.reason` and press Ctrl+Enter. Point at the red verdict and the Evidence panel.
> "My query runs on Zetaris, and the grader compares my rows with the answer, value by value. I returned 35 rows; the case wants one. These are rows of mine that shouldn't be there. That's evidence, not the model's opinion, and the answer itself stays hidden."

**4. Ask Nemo (1:15–1:40).** Click **Ask Nemo**. Point at the hint, then the trace line "critic … approved hint".
> "Nemo already looked at my attempt. A hint costs 15 points. Before I see it, a critic checks it doesn't give the answer away. If it does, Nemo has to rewrite it."

**5. Crack it and explain why (1:40–2:10).** Type `SELECT * FROM TPCDS_DB.reason WHERE lower(r_reason_desc) LIKE '%damage%'` and run it. When it asks why, type something like: *"WHERE keeps only reasons whose description has the word damage. lower() makes it ignore capitals."* Click **Close the case**. The stamp lands and the points fly.
> "Got it, and an extra column is fine. Now I have to explain why my query proves it, and Nemo grades that too. Case closed: points for the level, minus my mistake and the hint, plus a bonus for a solid explanation."

**6. It remembers (2:10–2:35).** Point at the **Memory** panel and click a note to open its trust ledger. Then click **Next case**. It should be "Excuses, excuses", another filtering case. Point at "Why this case: practises … filter, which memory says you've struggled with" and at "Recalled from memory".
> "Memory is the Meterless H-MEM engine. It wrote down what I got wrong, with a source and a confidence, and every change is in its trust ledger. It lives on my machine, so it's still here after a restart. The next case is picked to practise what I struggled with, and Nemo gets those notes before helping me."

**7. Under the hood (2:35–2:55).** Switch to Cursor and run `npm run conformance:hmem` in its terminal (13/13 checks pass). Then show Nightshift's **MONITOR**: Nemotron lanes, "via providers 100%".
> "I run the whole thing from Cursor on my laptop: pull, test, start. H-MEM passes its own conformance suite, 13 out of 13, on the engine the game uses. Every model call goes through Meterless Nightshift to NVIDIA Nemotron; here's the monitor. And Zetaris holds the data and runs every query, mine and the game's."

**8. Close (2:55–3:10).** Back to the game, with the stamped case and your score in view.
> "SQL Noir. Learn SQL by cracking cases, with a partner who shows you why. The answers come from the data, so the game can't bluff. The code is on GitHub at JannetEkka slash sql-noir."

## Optional, if time allows: Nemo writes a case

Click **Design a case**. It can take a minute or two; trim it. The trace shows Nemo drafting and the validator testing the draft on Zetaris, sending it back if it fails, then approving it. It's the strongest agent loop in the game, but rehearse it first: if Nemotron can't produce a fair case in three tries, the game says so instead of showing a broken case.
> "I can also ask Nemo to write a new case aimed at my weakest skill. The validator tests every draft on Zetaris and sends it back until it's fair."

## After recording

- In Clipchamp, cut the long waits (split the clip at the start and end of a wait and delete the middle), then export at 1080p.
- Upload to YouTube as **Unlisted** (or to Google Drive with "anyone with the link"). Paste the link into the HackOS form.
