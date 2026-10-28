# SQL Noir: Zetaris Demo Challenge script (Jannet narrates)

A new recording for Zetaris's $10,000 demo prize, built around how it's judged. About 4 minutes. The rules don't give a maximum length yet, so the edit stays at 4 minutes or less. Progress: [#67](https://github.com/JannetEkka/DSProjects/issues/67).

**Deadline: Tuesday 3 November** (the email of 10-28). The rules give the time as 23:45 UTC, so to be safe, upload by **Monday 2 November, evening IST**.

The words in quotes are a guide, so say them your way. Record each scene as its own clip if that's easier; Claude joins them, cuts the waits and adds captions.

## What the judges score, and where it's shown

| Points | Criterion (the email's wording) | Where in the video |
|---|---|---|
| 25 | Meaningful use of Zetaris: central to the solution and shown working live | Scenes 2–6: Docker, the Zetaris console, then the game asking Zetaris for every check, case file, error and answer |
| 15 | How it helped you: specific moments count more than general praise | Scene 6 (it failed two of my own cases) and the required segment (scene 7) |
| 15 | Problem and impact: a real problem with clear value for a business or user | Scene 1 (learners) and scene 8 (a company's own data) |
| 15 | Technical execution: it works, and the build has depth | Scenes 3–6: the REST API, the validator's checks, value-by-value grading |
| 15 | Working with SpaceXSI: how well Zetaris combines with SpaceXSI's coding agents | Scene 6: Cursor's agent, running Grok, adds a case, and Zetaris has to pass it |
| 10 | Creativity and originality | Scene 1 and the noir game itself |
| 5 | Video quality and storytelling | Claude's edit: waits cut, captions, sound levelled |

**SpaceXSI** is SpaceX's AI business. It owns Grok, and it bought Cursor in August 2026, so "SpaceXSI's coding agents" means Cursor's agent and Grok. SQL Noir itself was built with Claude Code and run from Cursor. In the video, only what Cursor's agent really does on camera is shown as its work.

## Before you record (15 min)

1. Restart Windows. Close everything you don't need: memory is tight.
2. Start **Docker Desktop**. In **Ubuntu**:
   ```bash
   cd ~/zetaris-platform
   docker compose start
   docker compose ps
   ```
   Wait until all four containers (postgres, driver, api, ui) say healthy.
3. Start **Nightshift** with only the NVIDIA cloud lanes on (no local lanes). Scene 5 needs it, for Nemo grading your explanation.
4. In **Cursor's terminal**, in `D:\code\sql-noir`:
   ```powershell
   git pull
   Remove-Item -Recurse .data
   npm start
   ```
   Don't run `npm run validate:cases` yourself. Scene 3 needs the first case to be checked live, and the agent runs the validator in scene 6.
5. **Check Cursor's agent works on the free plan:** open the Agent panel, pick a Grok model, and send a one-line test ("say hi"). If the free plan has no agent requests left, skip the agent part of scene 6 and run `npm run validate:cases` yourself instead. No paid plan.
6. Open **http://localhost:3000** (the Zetaris console) and **sign in before you start recording**, so your email and password never appear. Open its SQL editor and type this query in, but don't run it yet:
   ```sql
   SELECT r_reason_id, r_reason_desc FROM TPCDS_DB.reason
   ```
7. Open **http://localhost:4321** (the game) in a second tab. Hide the bookmarks bar (Ctrl+Shift+B).
8. **Never on camera:** the `.env` file, Zetaris's Management → API Tokens page, or Nightshift's Console (it shows your runtime token).
9. Clipchamp → Record & create → Screen recording, with your microphone.

## Scenes

**1. The problem (0:00–0:15).** The game's welcome screen ("New in town, detective?").
> "This is SQL Noir, a detective game where you learn SQL by cracking cases. Most SQL practice tells you you're wrong, but not why. Here, every answer is checked against real data in Zetaris, so the game can't bluff."

**2. Zetaris, live on my laptop (0:15–0:45).** Ubuntu terminal: run `docker compose ps`, then `docker stats --no-stream`. Switch to the Zetaris console: show the TPCDS_DB and NY_TAXI databases, then run the query you typed in the SQL editor.
> "Zetaris runs right here, in Docker under Ubuntu: four containers, on a 16 GB laptop, with no cloud account. It comes with two sample databases, a retail benchmark and New York taxi data. This is the reasons table my first case is built on, in Zetaris's own SQL editor."

**3. The game asks Zetaris first (0:45–1:15).** Switch to the game. Point at "Zetaris connected" in the header. Click **Take your first case**. While the spinner runs, point at the trace lines at the bottom. When "Damaged goods" opens, point at **The files** under the question.
> "The game talks to Zetaris over its REST API. Before I see a case, the validator runs the case's own answer on Zetaris and checks it: it only reads, it has an answer, the answer is small, it's the same twice, and there's no tie at a cut-off. The case file comes from Zetaris too: a DESCRIBE for the columns, and three sample rows."

**4. Zetaris's errors, then the evidence (1:15–1:45).** Type `SELECT r_reason_desk FROM TPCDS_DB.reason` (misspelled on purpose) and press Ctrl+Enter. Point at the error with Zetaris's suggestion. Then type `SELECT * FROM TPCDS_DB.reason` and run it. Point at the red verdict and the Evidence panel.
> "If I misspell a column, Zetaris's own error comes straight back, with its suggestion, and it costs me nothing. Now a real mistake: I forget the filter. The grader compares my rows with the answer's, value by value: thirty-five rows, and the case wants one. These are the rows that shouldn't be there."

**5. Case closed (1:45–2:05).** Type the right query (click the column names in The files to put them in):
```sql
SELECT r_reason_id, r_reason_desc FROM TPCDS_DB.reason WHERE lower(r_reason_desc) LIKE '%damage%'
```
Run it. When it asks why, type something like: *"I pick the id and the description, as the case asks. WHERE keeps only the reasons whose description contains damage, and lower() makes the match ignore capitals."* Click **Close the case**, and let the stamp land.
> "I add the filter, and the rows match. I explain why my query proves it, Nemo, my partner on NVIDIA Nemotron, grades that, and the case is closed."

**6. Cursor's agent writes a case, and Zetaris checks it (2:05–2:50).** In Cursor, open the Agent panel with a Grok model and paste this prompt:
```
Add one new case to SEED_CASES in src/game/seed-cases.ts, on NY_TAXI.taxi_zones (its columns are listed in schemaText in src/game/engine.ts). Make it level 1, practising select and filter: a two-sentence noir story, a precise question, an answerSql that is one read-only SELECT on NY_TAXI.taxi_zones returning at most 25 rows and 6 columns, orderMatters false, two hints that don't give the answer away, databases ["NY_TAXI"], origin "seed", and a new id starting with "seed-". Follow the style of the existing cases. Then run npm run validate:cases, and if the new case fails, fix it and run it again until it passes.
```
Let it work (Claude speeds this part up). If Cursor asks to run the command, click **Run**. Point at the PASS line for the new case and at "8/8 seed cases are ready to play". If its first try fails, keep it on camera: the validator's FAIL and the agent's fix are the best part.
> "Zetaris keeps my coding agent honest too. This is Cursor's agent, running Grok, adding a new case on the New York taxi data. It doesn't get a free pass: the validator runs its answer on Zetaris, like every case in the game. The first time I ran this validator, it failed two of my own cases, a tie and a join too heavy for my laptop. The agent's case passes, so it's ready to play."
(If the agent's case failed first, say so: "It failed once, the agent fixed it, and now it passes.")

**7. Why Zetaris was amazing (2:50–3:45). Required: 40–60 seconds.** Voice-over is allowed, so read it over any of the footage (Claude lays it over the console, `docker compose ps`, the PASS lines and the stamp), or say it to the camera if you prefer.
> "Why was Zetaris amazing for this? Because a detective game needs a referee that can't bluff. With Zetaris on my laptop, one REST call runs a player's query on real data and sends back the rows, so right and wrong come from the data. The moment it clicked was when the validator failed my own cases: a tie I hadn't noticed, and a join my laptop couldn't finish. What surprised me was how much of the game it gave me: a DESCRIBE and three sample rows became the case file, and its error messages were clear enough to show a beginner as they are. And it all ran locally, with no cloud bill."

**8. Close (3:45–4:00).** Back to the game, with the stamped case in view.
> "SQL Noir. Point it at a company's own data in Zetaris, and new analysts learn SQL on the tables they'll really use. The answers come from the data, so the game can't bluff. The code is on GitHub at JannetEkka slash sql-noir."

## The write-up

The email asks for one line in the write-up but doesn't say where the write-up goes, and Dropbox only takes files. So upload a short text file next to the video, with the same name (`SMARTIES_DDMMYY.txt`), and put the one-liner on the video's last frame too.

```
SQL Noir (team SmarTies, Jannet Ekka) is a detective game that teaches SQL on real data. Every check, every player query and every case file comes from Zetaris, running locally in Docker: the validator runs each case's answer on Zetaris before a player sees it, the case file is a DESCRIBE plus three sample rows, and the grader compares the player's rows with the answer's, value by value. Nemo, the coach on NVIDIA Nemotron through Meterless Nightshift, explains the evidence, and the Meterless H-MEM engine remembers what each player gets wrong. In the demo, Cursor's agent (Grok) adds a new case, and it has to pass the validator on Zetaris first.

In one sentence, why did you think it was amazing? With Zetaris, every answer in my game is checked against real data, and it even caught mistakes in my own cases.

Code: https://github.com/JannetEkka/sql-noir
```

## After recording

1. Put the clips on Google Drive with "anyone with the link" and tell Claude. Claude edits them, adds captions and the end card, and names the file `SMARTIES_DDMMYY` with the date you'll upload.
2. If the agent's case passed, copy it from `src/game/seed-cases.ts` and send it to Claude, so the repo matches the video.
3. Upload the video and the write-up file to the [shared Dropbox folder the organisers gave on 10-28](https://www.dropbox.com/scl/fo/xvv3sj5bdk622i56k5j19/AKi8lHTh63XEx8896HTNTds?rlkey=0wsmdx70l0spn1dlv4j062ctj&st=z3afr9ie&dl=0).
4. Set the Drive clips back to Restricted.
