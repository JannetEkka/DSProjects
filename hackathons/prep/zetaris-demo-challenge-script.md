# SQL Noir: Zetaris Demo Challenge script (Jannet narrates)

A new recording for Zetaris's $10,000 demo prize, built around how it's judged. About 3:50, which stays under the hackathon's 4-minute limit until the organisers say what this prize allows. Progress and open questions: [#67](https://github.com/JannetEkka/DSProjects/issues/67).

The words in quotes are a guide, so say them your way. Record each scene as its own clip if that's easier; Claude joins them, cuts the waits and adds captions.

## What the judges score, and where it's shown

| Points | Criterion | Where in the video |
|---|---|---|
| 25 | Meaningful use of Zetaris, **shown live** | Scenes 2–6: Docker, the Zetaris console, then the game asking Zetaris for every check, case file, error and answer |
| 15 | How it helped you | Scene 6 (it caught my own broken cases) and the required segment |
| 15 | Problem and impact | Scene 1 |
| 15 | Technical execution | Scenes 3 and 6: the REST API, the validator's checks, value-by-value grading |
| 15 | Working with SpaceXSI's coding agents | **Waiting on the organisers** (see the slot after scene 6) |
| 10 | Creativity and originality | Scene 1 and the noir game itself |
| 5 | Video quality and storytelling | Claude's edit: waits cut, captions, sound levelled |

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
   Don't run `npm run validate:cases` yet. Scene 3 needs the first case to be checked live, and scene 6 runs it on camera.
5. Open **http://localhost:3000** (the Zetaris console) and **sign in before you start recording**, so your email and password never appear. Open its SQL editor and type this query in, but don't run it yet:
   ```sql
   SELECT r_reason_id, r_reason_desc FROM TPCDS_DB.reason
   ```
6. Open **http://localhost:4321** (the game) in a second tab. Hide the bookmarks bar (Ctrl+Shift+B).
7. **Never on camera:** the `.env` file, Zetaris's Management → API Tokens page, or Nightshift's Console (it shows your runtime token).
8. Clipchamp → Record & create → Screen recording, with your microphone.

## Scenes

**1. The problem (0:00–0:15).** The game's welcome screen ("New in town, detective?").
> "This is SQL Noir, a detective game where you learn SQL by cracking cases. Most SQL practice tells you you're wrong, but not why. Here, every answer is checked against real data in Zetaris, so the game can't bluff."

**2. Zetaris, live on my laptop (0:15–0:50).** Ubuntu terminal: run `docker compose ps`, then `docker stats --no-stream`. Switch to the Zetaris console: show the TPCDS_DB and NY_TAXI databases, then run the query you typed in the SQL editor.
> "Zetaris runs right here, in Docker under Ubuntu on WSL: four containers, on a 16 GB laptop with no cloud account. It comes with two sample databases, a retail benchmark and New York taxi data. This is the reasons table my first case is built on, queried in Zetaris's own SQL editor."

**3. The game asks Zetaris first (0:50–1:25).** Switch to the game. Point at "Zetaris connected" in the header. Click **Take your first case**. While the spinner runs, point at the trace lines at the bottom. When "Damaged goods" opens, point at **The files** under the question.
> "The game talks to Zetaris over its REST API, one SQL statement per call. Before I see a case, the validator runs the case's own answer on Zetaris and checks it: it only reads, it has an answer, the answer is small, it's the same twice, and there's no tie at a cut-off. The case file comes from Zetaris too: a DESCRIBE for the columns and types, and three sample rows."

**4. Zetaris's errors, then the evidence (1:25–2:00).** Type `SELECT r_reason_desk FROM TPCDS_DB.reason` (misspelled on purpose) and press Ctrl+Enter. Point at the error with Zetaris's suggestion. Then type `SELECT * FROM TPCDS_DB.reason` and run it. Point at the red verdict and the Evidence panel.
> "If I misspell a column, Zetaris's own error comes straight back to me, with its suggestion, and it costs me nothing. Now a real mistake: I forget the filter. Zetaris runs it, and the grader compares my rows with the answer's, value by value. Thirty-five rows came back, and the case wants one. These are the rows that shouldn't be there."

**5. Case closed (2:00–2:25).** Type the right query (click the column names in The files to put them in):
```sql
SELECT r_reason_id, r_reason_desc FROM TPCDS_DB.reason WHERE lower(r_reason_desc) LIKE '%damage%'
```
Run it. When it asks why, type something like: *"I pick the id and the description, as the case asks. WHERE keeps only the reasons whose description contains damage, and lower() makes the match ignore capitals."* Click **Close the case**, and let the stamp land.
> "I add the filter, and now the rows match. I explain why my query proves it, Nemo, my partner on NVIDIA Nemotron, grades that, and the case is closed."

**6. Every case, tested on Zetaris (2:25–2:55).** Switch to Cursor's terminal and run:
```powershell
npm run validate:cases
```
Let it print a PASS line per case and "7/7 seed cases are ready to play" (Claude trims the wait).
> "Every case in the game goes through that validator on Zetaris. The first time I ran this, two of my own cases failed: one had a tie at the cut-off, and one join was too heavy for my laptop. Zetaris caught both before any player did."

**Slot: working with SpaceXSI's coding agents (15 points).** Leave this out until the organisers say what it means. SQL Noir was built with Claude Code and run from Cursor, so we only show what was actually used.

**7. Why Zetaris was amazing (2:55–3:45). Required: 40–60 seconds.** Voice-over is allowed, so read it over any of the footage (Claude lays it over the console, `docker compose ps`, the PASS lines and the stamp), or say it to the camera if you prefer.
> "Why was Zetaris amazing for this? Because a detective game needs a referee that can't bluff. With Zetaris on my laptop, one REST call runs a player's query on real data and sends back the rows, so right and wrong come from the data. The moment it clicked was when the validator failed my own cases: a tie I hadn't noticed, and a join my laptop couldn't finish. What surprised me was how much of the game it gave me: a DESCRIBE and three sample rows became the case file, and its error messages were clear enough to show a beginner as they are. And it all ran locally, with no cloud bill."

**8. Close (3:45–3:55).** Back to the game, with the stamped case in view.
> "SQL Noir. The answers come from the data in Zetaris, so the game can't bluff. The code is on GitHub at JannetEkka slash sql-noir."

## The one-line write-up

```
With Zetaris, every answer in my game is checked against real data, and it even caught mistakes in my own cases.
```

## After recording

1. Put the clips on Google Drive with "anyone with the link" and tell Claude. Claude edits them, adds captions and names the file `SMARTIES_DDMMYY` with the date you'll upload.
2. Upload the file to the [shared Dropbox folder from the rules page](https://www.dropbox.com/scl/fo/xvv3sj5bdk622i56k5j19/AKi8lHTh63XEx8896HTNTds?rlkey=402k4lda7feylyrwqnkfymfjt&st=e9pzur2i&dl=0), and add the one-line write-up wherever the organisers say it goes.
3. Set the Drive clips back to Restricted.
