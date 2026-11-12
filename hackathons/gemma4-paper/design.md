# Design brief: Does the action format matter? (Gemma 4 Developer Agent, Paper Track)

**Process (Jannet, 11-08), compressed for a one-day entry:** a discussion session wrote this brief on 11-12 (https://claude.ai/code/session_016VDQokX44Dxof4NVDJTy8N). Jannet picked Option A in that session and asked for a separate build session, which starts from the build prompt in section 10. Tracking issue: [#100](https://github.com/JannetEkka/DSProjects/issues/100). The main track is a different entry with its own session and issue ([#95](https://github.com/JannetEkka/DSProjects/issues/95)); files for it go in `hackathons/gemma4/`, not here.

## 0. The hackathon, in one screen

- **What:** Google's Gemma 4 Developer Agent **Paper Track** on Kaggle: https://www.kaggle.com/competitions/gemma-4-developer-agent-paper. Jannet joined on 11-11.
- **Deadline:** **Nov 13, 05:29 IST** (Nov 12, 23:59 UTC), confirmed on Kaggle's page. It can't be moved. A saved draft doesn't count: the Writeup must be **submitted**. Our own target is submitted by **Nov 12, 23:30 IST**, so Jannet isn't submitting at 5 in the morning.
- **Deliverable:** one Kaggle Writeup, **3,000 words maximum**, original and unpublished, with a title and subtitle, abstract, introduction, methods and experiments, related work and citations. A public notebook with the code is optional; we attach one, because one of the five criteria is verifiability.
- **Judging:** five criteria, each scored 0 to 5, equal weight, averaged: **novelty** ("new insights... or highlight important properties of existing methods"), **quality** (does it generalise beyond the competition), **relevance**, **verifiability**, **clarity**. One named judge. Prizes: $15,000 best paper, $10,000 best new resource, $10,000 best new application.
- **What the rules force:**
  - Tuning results are not required. "Any related research, as long as it is unpublished" is eligible.
  - External data and models must be public and free or cheap for everyone.
  - Open-source code we use needs an OSI licence that allows commercial use.
  - The competition's data must not be passed on to people outside the competition. We publish our code and our result tables, not the task texts.
- **Money:** none of ours. Kaggle's free GPU quota only. No card anywhere; see [../cards.md](../cards.md).
- **Training:** this paper has **no training rounds**. There isn't time before the deadline, and the question below doesn't need any. Post-training belongs to #95, whose deadline is Dec 2.

## 1. The idea

**One sentence:** for anyone building a coding agent on a small offline model, we measure whether Gemma 4 fixes more bugs when it writes each action as a plain-text shell command than when it must write it as a JSON tool call, with nothing else changed.

**Terms:**
- An **agent** here is a loop: the model reads the bug report, asks to run a command, sees the output, and repeats until it has edited the code and says it's done.
- An **action** is one such request. The **action format** is the shape the model must write it in.
- A **JSON tool call** is a structured message, for example `{"name": "run_command", "arguments": {"command": "pytest tests/test_x.py"}}`. The server has to parse it, and a missing brace or a wrong field name makes it unusable.
- A **plain-text command** is the same request written as a fenced `bash` block, which our code picks out with a simple rule.

**Why it's not the obvious study (lessons 0 and 1).** The obvious studies already exist, checked on 11-12:

| Study | What it has | Link |
|---|---|---|
| Gemma 4 26B on SWE-bench Lite | 116 of 300 solved, with notes on what failed | [ai-muninn, Apr 17](https://ai-muninn.com/en/blog/swe-bench-lite-gemma4-26b-38-percent) |
| Size ladder and agent designs on the competition's tasks | Per-task results for E4B, 12B and 31B; 8 agent designs on 70 tasks; 114 of 129 public tasks verified as valid | [dmitriigluzdov's notebook](https://www.kaggle.com/code/dmitriigluzdov/gemma-4-task-soundness-serving-and-evaluation), [dataset](https://www.kaggle.com/datasets/dmitriigluzdov/gemma-4-task-soundness-and-local-results) |
| Thinking on or off | 23 tasks solved with thinking off, 48 to 51 with it on | [zhukovoleksiy's walkthrough](https://www.kaggle.com/code/zhukovoleksiy/gemma-4-walkthrough-findings-submission) |

**The closest existing work to ours** is [ai-muninn's Apr 13 post](https://ai-muninn.com/en/blog/swe-bench-local-models-framework-matters): Gemma 4 26B made 40+ errors in OpenHands (JSON tool calls) and fixed a bug in 9 steps in SWE-agent (text commands). That was one task per framework, a different task in each, with whole frameworks swapped. The author calls it "a feasibility test, not a full benchmark". Nobody has changed only the format and counted. The competition's own harness accepts only JSON tool calls, so competitors had no reason to test it.

**What ours does differently:** one small agent loop, the same tasks, the same model, the same prompt, the same budget. The only difference between the two arms is the paragraph that tells the model how to write an action, and the code that reads it.

**The other ideas we considered:**
- A size ladder with the host's harness unchanged. Dropped: dmitriigluzdov's dataset already has it.
- A failure analysis of public run logs, with no GPU. Dropped: the same dataset already sorts failures by stage.
- Skipping the track. This was the discussion session's recommendation once the public work was read; Jannet chose to go ahead with Option A.

## 2. The measured comparison (decided before building)

- **Arms:** `json` (the model calls tools through the server's tool-call parser) and `text` (the model writes one fenced `bash` block per turn).
- **Same in both arms:** the model file, the server and its settings, the task list, the system prompt apart from the format paragraph, thinking on with the same budget, temperature, seed, step limit, time limit per task, how long outputs are cut, and the message sent after a malformed action.
- **Model:** `gemma-4-12b-it-qat-w4a16-ct` first. Then `gemma-4-e4b-it-qat-w4a16-ct` on the same tasks if the GPU quota allows, so we can say whether the effect depends on size. These are two of the four models the main track allows.
- **Tasks:** the competition's public tasks, limited to the ones verified as valid in dmitriigluzdov's `task_soundness.csv` (CC BY 4.0, credited). A 10-task pilot first, then as many valid tasks as the quota allows, chosen by a fixed rule written down before the run (for example, every second task in sorted order), never by looking at results.
- **Grading:** the competition's own checker (`swegemma`'s verification), so "fixed" means what it means on the leaderboard.
- **Numbers we report, each with its count:**
  1. Tasks fixed per arm, and the paired view: tasks only `text` fixed, tasks only `json` fixed, tasks both fixed, tasks neither fixed.
  2. Malformed actions per arm: turns where no usable action could be read, out of all turns.
  3. Turns and seconds per task.
  4. Why each unfixed task failed, sorted by fixed rules (section 4).
- **Test:** an exact sign test on the tasks where the arms disagree. We say plainly that it is a rough guide: tasks from one repository aren't independent, and public work measured identical runs differing by up to 6 of 58 tasks. If quota allows, a second seed shows how much one arm moves against itself.
- **A good result** is a clear difference in either direction, or a clear "no difference" with enough tasks to mean something. **If it isn't good** (too few tasks, or differences inside the noise), the paper says so in the abstract, reports the counts and what sample would be needed, and still publishes the harness. We don't invent a baseline or an improvement (writing rule, 10-31).

## 3. What a judge sees in the first 10 seconds

- **Headline (six words):** "Same model, same bugs, two formats."
- The first screen of the Writeup is one small table: per arm, tasks fixed out of N and malformed actions out of all turns, and under it one sentence that says what the difference means for someone choosing how to build an agent on Gemma 4.
- One figure: a paired chart of tasks (fixed by both, only `text`, only `json`, neither). Use the `dataviz` skill for it.
- The look is a plain research note. No decoration.

## 4. Architecture

```
Kaggle notebook (free GPU, internet off)
 ├─ vLLM server ── Gemma 4 QAT model (from Kaggle Models, attached as input)
 ├─ task loader ── competition data (attached as input): tasks.jsonl, snapshots
 ├─ our agent loop ──┬─ arm "json": tools = run_command, submit → server's gemma4 tool parser
 │                   └─ arm "text": one ```bash block per turn → our regex
 ├─ workspace ── one fresh copy of the repo per (task, arm, seed); commands run there
 ├─ checker ── swegemma verification on the resulting patch
 └─ outputs ── results.csv (one row per task, arm, seed), turns.jsonl (one row per turn), summary tables
```

- **Model judgment vs fixed rules (lessons 4).** The model decides one thing: the next action. Everything else is code:
  - what counts as a usable action;
  - when a run stops (the model submits, the step limit, the time limit);
  - whether the patch fixed the bug (the competition's tests);
  - which failure type an unfixed task gets.
- **Failure types, decided by rules over the logs, in this order:** harness error; no patch (the repository was never changed); stuck on format (at least half the turns malformed); ran out of steps or time with a patch; patch submitted but tests fail. A human reading of a sample of logs can add colour to the paper, labelled as a reading.
- **One agent, no roles.** Several agents would add variables, and the question is about one variable.
- **Services:** Kaggle notebooks, free GPU quota (30 hours a week when full). Use the L4 machine the starter notebook uses if the account gets it; otherwise T4 x2. The run goes up with `kaggle kernels push` and runs unattended. Cost: none.

## 5. The flow, step by step

1. Start the server with the model, with the same settings as the host's starter notebook (`tool_call_parser='gemma4'`, `reasoning_parser='gemma4'`, context of 32,768 tokens).
2. For each task, arm and seed: make a fresh workspace from the task's snapshot.
3. Send the system prompt (shared text plus that arm's format paragraph) and the bug report.
4. Read the model's reply. If it holds a usable action, run it in the workspace and send back the output, cut to a fixed length. If not, record a malformed turn and send the same fixed correction message in both arms. Either way the turn counts toward the step limit.
5. Stop when the model submits, or at the step or time limit.
6. Take the workspace's diff as the patch, with test files stripped the way the host's harness strips them, and run the competition's checker.
7. Write the row. A crash in our own code is a `harness error` row, never a silent "unfixed".
8. After all rows: build the tables and the paired chart from `results.csv` only. Nothing in the paper is typed by hand from memory.

**What blocks a "done" claim (lessons 8, 9):** before the main run, the pilot must show that (a) the checker passes the reference patch and fails the empty patch on the pilot tasks, (b) both arms produce at least one usable action on every pilot task, and (c) the two prompts differ only in the format paragraph (a diff of the two prompts is saved with the outputs).

## 6. Decisions settled now

- **Thinking is on in both arms**, with the harness default budget of 4,096 tokens, because public work found it more than doubles the solve rate.
- **One capability in both arms:** run a shell command (reading, searching, editing and testing all go through it), plus a way to say "done". This keeps the arms equal. It also means our `json` arm is not the host's nine-tool agent, and the paper says so.
- **Budget per task:** 30 turns and 5 minutes, fixed before the run. Change it only after the pilot and only for both arms.
- **What we publish:** the notebook, `results.csv` with task ids, and turn-level counts. Not the task texts or raw transcripts, since those carry the competition's data.
- **Kaggle token:** done. Jannet created a new token on 11-12 and saved it through the secure form. It is a network secret for `www.kaggle.com` on the SMT environment, shared by #100 and #95. No environment variable holds it and no session ever sees it. `KAGGLE_API_TOKEN` (another entry's) is not used.
  - Plain HTTPS calls to `https://www.kaggle.com/api/v1/...` work as they are.
  - The `kaggle` CLI (2.2.5) needs three changes in a scratch virtualenv: in `kagglesdk/kaggle_env.py` point `PROD` at `https://www.kaggle.com`; in `kagglesdk/kaggle_http_client.py` make `_get_request_url` always use `f"{self._endpoint}/api"`; in `kaggle/api/kaggle_api_extended.py` make `_introspect_token` return the account name. Then run it with `KAGGLE_API_TOKEN=proxy-injected`. Never put a real token in a variable or a file.
- **The models need no sign-up.** The four QAT models are on Kaggle Models under Apache 2.0, and the account can already list their files (checked 11-12).
- **Two things only Jannet can check:** that the Kaggle account is phone-verified (GPUs need it), and how much GPU quota is left this week.

## 7. Acceptance conditions

- [ ] The pilot's three checks in section 5 pass, and their output is posted on #100.
- [ ] `results.csv` has exactly one row per (task, arm, seed) that was planned; missing rows are listed with a reason.
- [ ] Every number in the Writeup is produced by a notebook cell from `results.csv` or `turns.jsonl`, or carries a link to its source.
- [ ] The Writeup has all the required sections, is under 3,000 words (counted, with the count posted on #100), names the closest existing work with links, and has a limitations section.
- [ ] The first screen has the table and the one-sentence meaning (section 3); the paired chart is readable in light and dark.
- [ ] The public notebook runs top to bottom on Kaggle with the competition data and model attached.
- [ ] Jannet has explained the result and two failure cases back in her own words (section 9) before the Writeup is submitted.
- [ ] Submitted, not only saved, and the Writeup's link is on #100.

## 8. Demo plan

There's no video. The Writeup is the demo. Draft it with the `human-voice` skill, in Jannet's voice, plain and specific, with every number sourced. No UI, so no design canvas step.

**Checkpoints (IST, Nov 12). At each one, post on #100. If one is missed, tell Jannet what is cut.**

| Time | What must be true |
|---|---|
| 13:30 | One task runs end to end on Kaggle in both arms, and the checker gives a verdict |
| 15:30 | The 10-task pilot is done and its numbers are on #100; the main run is started |
| 19:00 | Main run done, or stopped. From here we write up what exists, labelled as partial if it is |
| 20:00 | Results and failure cases explained to Jannet; she explains them back |
| 21:30 | Draft Writeup with Jannet |
| 23:30 | Submitted by Jannet. Hard stop for edits is Nov 13, 04:30 IST |

If nothing usable exists at 19:00, say so plainly and recommend not submitting. The harness and what we learned still go to #95.

## 9. Jannet's check

Questions Jannet answers in her own words, in the build session, once the pilot numbers exist:

1. What is the one thing that differs between the two arms, and what is kept the same?
2. What makes an action "malformed" in each arm?
3. Who decides whether a bug is fixed: the model, our code, or the competition's tests?
4. Take one task that one arm fixed and the other didn't. What happened, turn by turn?
5. Why can't we say "text is better" from a 2-task difference?
6. What does this paper not show? (Other models, the host's nine-tool agent, tuned models.)

- **Option A chosen:** Jannet, 11-12, in the discussion session ("start the option A").
- **Explained back and signed off:** _pending; happens in the build session before submission._

## 10. The build prompt

> You are the **build session** for the Kaggle Gemma 4 Developer Agent **Paper Track**. Tracking issue: JannetEkka/DSProjects#100 (read it and its comments first). The design brief is `hackathons/gemma4-paper/design.md` on the branch you start from; it is your specification. Read it fully, then `.claude/CLAUDE.md` and `hackathons/lessons.md`.
>
> **The job:** measure whether untuned Gemma 4 fixes more of the competition's public bug-fix tasks when it writes actions as plain-text `bash` blocks than as JSON tool calls, with nothing else changed, on Kaggle's free GPUs. Then draft a Writeup of at most 3,000 words for Jannet to submit. **Deadline: Nov 13, 05:29 IST, fixed. Our target: submitted by Nov 12, 23:30 IST.** Follow the checkpoint table in section 8 and post on #100 at each one.
>
> **Order of work:**
> 1. Set up Kaggle access as section 6 describes (the token is already injected for `www.kaggle.com`; never use `KAGGLE_API_TOKEN`'s real value, never ask for a key in chat).
> 2. Pull the host's starter notebook (`ryanholbrook/getting-started-gemma-4-developer-agent`) and `HARNESS_README.md` from the competition `gemma-4-developer-agent`. Read how `swegemma` builds a workspace from a snapshot and how it verifies a patch, so you reuse those and replace only the agent loop.
> 3. Write the notebook: server start copied from the starter, our loop with the two arms, the pilot checks, the outputs in section 4. Push it with `kaggle kernels push` (GPU on, internet off, competition data, the wheelhouse dataset and the model attached, as in the starter's `kernel-metadata.json`). Keep it private until Jannet submits.
> 4. Run the 10-task pilot, post the numbers, then the main run.
> 5. Explain the results and two failure cases to Jannet in plain language; she answers the questions in section 9.
> 6. Draft the Writeup with the `human-voice` skill; Jannet reviews and submits.
>
> **Responsibilities:** the model chooses the next action. Code decides everything else: what a usable action is, when to stop, whether the bug is fixed (the competition's checker), and the failure type. Don't add agents, tools or prompt tricks; one variable only.
>
> **Rules:** no training in this entry. No own money and no card. Don't publish the competition's task texts. Every repo change goes through a PR for Jannet; never push to `main`. Every number in the paper comes from a notebook cell or a cited source; never invent a baseline or an improvement. If the first GPU push fails because the account isn't phone-verified or the quota is gone, stop and tell Jannet exactly what to click. Meet the acceptance conditions in section 7. Keep this chat log raw from this message on.
