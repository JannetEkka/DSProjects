# Same model, same bugs, two formats

**Subtitle:** What changes when Gemma 4 12B writes each action as a bash block instead of a tool call, measured on the competition's public tasks

> DRAFT. Numbers marked [A] come from half A only (35 tasks) and are replaced when the other notebooks finish.

## Abstract

I ran one small agent loop on the competition's public bug-fix tasks twice per task: once with Gemma 4 12B calling tools through the server's tool-call interface, and once with the same model writing one fenced `bash` block per turn. The model file, server settings, prompt (apart from one line), budget and checker were the same. On 35 tasks [A] the tool-call arm fixed 2 and the text arm fixed 1 [A], so I can't claim either format fixes more bugs: with this loop and a 15-minute budget, both sit near zero. What the format did change is how the model spends its budget. Format errors were rare in both arms (12 of 1,186 turns and 1 of 298 [A]). In the text arm the model kept writing after its command in 70 of 298 turns [A], and those turns took 80% of its output tokens [A]. In the tool-call arm the model stopped producing thinking text: every first turn had some, and 587 of 690 turns from turn 16 onward had none [A]. A third arm that cuts the text reply after its first command block [RESULT B]. Code, per-task results and per-turn counts are in the attached notebooks.

| | Tool calls (`json`) | Bash blocks (`text`) |
|---|---|---|
| Tasks fixed | 2 of 35 [A] | 1 of 35 [A] |
| Malformed turns | 12 of 1,186 [A] | 1 of 298 [A] |
| Turns that ran to the output cap | 9 [A] | 70 [A] |
| Turns with no thinking text | 697 of 1,186 [A] | 0 of 298 [A] |

For someone building an agent on Gemma 4: the choice of action format did not show up as broken syntax. It showed up as where the turn ends and whether the model thinks first, and both need handling in the loop.

## 1. Introduction

The competition's harness (`swegemma`) gives the agent tools and reads the model's actions as tool calls. That is one of two common ways to build a coding agent. The other is to let the model write a shell command in plain text and pick it out with a pattern, as SWE-agent's later "mini" variant and CodeAct-style agents do [1, 2, 3].

There is a standing belief that small local models do better with text actions, because structured calls break. The closest test I found is a pair of blog posts by ai-muninn: Gemma 4 26B made more than 40 errors in OpenHands, which uses tool calls, and fixed a bug in 9 steps in SWE-agent, which uses text commands [4]. That was one task per framework, a different task in each, with the whole framework swapped. The author calls it "a feasibility test, not a full benchmark".

This paper changes only the format and counts. The question: with the same model, tasks, prompt and budget, does Gemma 4 fix more bugs when it writes its action as a `bash` block than as a tool call?

The answer I can support is narrower than the one I set out for. On fix rate, the two arms are too close to zero to separate. On behaviour, they differ a lot, in two ways I did not expect, and neither is "the JSON was malformed".

## 2. Method

### 2.1 Tasks and checker

The tasks are the competition's public ones (`tasks.jsonl`, 129 tasks from fastapi, rich, requests and httpx). I started from the 114 that dmitriigluzdov's `task_soundness.csv` marks as sound [5], and put them in a fixed order: sorted by the SHA-256 of the task id. The order was written into the notebook before any run, so no task was chosen by looking at results.

Workspaces and grading are the host's. Each run gets a fresh workspace built by `swegemma`'s own setup functions (snapshot extraction, editable install, test configuration, baseline commit), using its subprocess sandbox as the starter notebook does. The patch is the workspace's `git diff` against the baseline with test files stripped by `swegemma`'s `strip_protected_files_from_patch`. A task counts as fixed only if `swegemma`'s `verify_task` says so: the patch applies in a clean workspace and the task's tests pass.

Before a task is run, the same notebook checks the checker. `verify_task` must pass the task's reference patch and fail the empty patch. If not, the task is skipped and listed in `controls.csv`. This gate mattered: in half A it passed 35 of 57 tasks [A] (rich 18 of 23, fastapi 17 of 32, requests 0 of 2). These tasks are sound in [5], so the failures come from my environment, Kaggle's subprocess sandbox without the per-repository dependency repairs that [5] describes. A task whose reference patch fails cannot be scored, so it is left out.

### 2.2 The loop

The agent is one loop with one capability: run a shell command in the workspace. Reading, searching, editing and testing all go through it. The model can also say it is done.

Each turn, the model's reply is read for an action. If there is one, the command runs and its exit code and output go back, cut to 4,000 characters. If there is none, the turn is counted as malformed and a fixed correction message goes back. If the reply holds more than one action, only the first runs and the model is told so. A run stops when the model submits, after 50 turns, or after 15 minutes.

The model decides one thing, the next action. Code decides what a usable action is, when a run stops, and the failure type of an unfixed run. The checker decides whether the bug is fixed.

### 2.3 The two arms

- **`json`**: the request carries two tool definitions, `run_command(command)` and `submit()`. The server parses the model's tool-call tokens (vLLM with `tool_call_parser='gemma4'`) and returns structured calls. A turn is usable if the first call names one of the two tools and its arguments parse into an object with a non-empty `command`. Gemma 4 does not literally emit JSON; it emits its own tool-call tokens, which the server converts. I call the arm `json` because JSON is what the agent builder writes and reads, and it is the interface the competition's harness uses.
- **`text`**: no tools are sent. The model is told to write one fenced block starting with ```` ```bash ````. A turn is usable if the reply contains such a block; the first one is the action. A block containing only the word `submit` ends the run.

The system prompts differ in one line, the paragraph that says how to write an action. The notebook asserts this and saves the diff (`prompt_diff.txt`). The user message (bug report plus a three-level file listing), the correction message and the output format are produced by the same code for both arms. One difference comes with the format itself: in `json` the command output returns as a tool message, in `text` as a user message.

### 2.4 Settings

Model: `gemma-4-12b-it-qat-w4a16-ct`, one of the four the competition allows, untuned. Server: vLLM as configured in the host's starter notebook (context 32,768 tokens, `reasoning_parser='gemma4'`), on Kaggle's 4× L4. Sampling: temperature 0.2, top-p 0.95, thinking on with a 4,096-token budget, as in the host's sample submission. Output cap: 6,144 tokens per turn. Seed 0. Thinking text is not sent back in later turns, in either arm.

Both arms of a task run at the same moment against the same server, with 20 runs in flight, so the two arms see the same load. Under that load the server produced about 20 output tokens per second per run [A].

### 2.5 What changed after the pilot

A 10-task pilot with 30 turns and 5 minutes fixed nothing in either arm and no run submitted, so it could not compare fix rates. It also showed the reference patch failing on 5 of its 10 tasks. Before the main run I raised the budget to 50 turns and 15 minutes for both arms and added the checker gate. I also added a third arm, described in section 3.4, because of what the pilot's text arm did. None of these changes was made after looking at main-run results.

## 3. Results

Main comparison: [N] tasks that passed the gate, one run per arm, [ROWS] rows, no harness errors [A].

### 3.1 Bugs fixed

`json` fixed 2 of 35 and `text` fixed 1 of 35 [A]. No task was fixed by both. On the 3 tasks where the arms disagree, an exact sign test gives p = 1.0 [A]. That is no evidence of a difference, and with fix rates this low the study could not have detected anything but a very large one.

[FIGURE: paired chart]

Why so low? This loop is deliberately bare: one tool, no file-edit helper, no code graph, no retrieval. Public work on the same tasks reports far more with the host's nine-tool agent and longer budgets [5, 6]. Only 1 of 70 runs submitted [A]; the rest ran out of time or turns.

### 3.2 Format errors are rare in both arms

Malformed turns: 12 of 1,186 in `json` and 1 of 298 in `text` [A]. Of the 12, 9 were replies that hit the output cap before any tool call and 3 were replies with no tool call [A]. No turn in either arm had an unknown tool name or arguments that failed to parse. No run was "stuck on format" (half or more of its turns malformed).

So the belief that structured calls break did not hold for this model and server. The server's parser turned Gemma 4's tool-call tokens into valid calls essentially every time.

### 3.3 What the format changed: where the turn ends, and whether the model thinks

**Text: the turn does not end.** In 70 of 298 `text` turns the reply ran to the 6,144-token cap [A], against 9 of 1,186 in `json`. Those 70 turns took 430,080 of the arm's 538,940 output tokens (80%) [A], and they happened in 33 of 35 tasks [A]. In 81 turns the reply held more than one `bash` block [A]. Reading the pilot's transcripts (a reading of 7 cut-off turns, labelled as such): after its first command the model either wrote dozens more commands (46, 78 and 279 blocks in three replies) or wrote the command's output itself, such as a traceback or a grep listing that never happened, and carried on from it. A tool call ends the turn by construction. A code fence does not.

The cost is time. Every `text` run hit the 15-minute limit [A], after a median of 7 turns [A].

**Tool calls: the thinking goes away.** Thinking was on in both arms with the same budget. In `text`, every turn had thinking text. In `json`, every first turn did, but 697 of 1,186 turns overall had none [A], and from turn 16 onward 587 of 690 had none [A]. The model fell into short replies (median 38 output tokens [A]) that call a tool straight away. It ran 584 `grep` and 316 `cat` commands [A] and hit the 50-turn limit in 15 of 35 runs [A], 20 of them [CHECK] without ever changing a file.

I can't say from this data whether that is the model's habit after tool results or something in the chat template or reasoning parser. Either way it is what an agent builder gets from this model and the competition's server settings.

The two arms end up failing differently. `json` took 4 times as many turns [A] and left a patch in 15 runs against 9 [A], but mostly searched without reasoning. `text` reasoned every turn and wasted most of its tokens after the action.

### 3.4 Cutting the text reply after its first block

[SECTION FROM NOTEBOOK B: text_stop results]

## 4. Related work

SWE-bench introduced the task form used here: a repository, an issue, and hidden tests that decide whether a patch resolves it [7]. SWE-agent showed that the interface given to the model changes results on those tasks [1], and its authors' later mini-SWE-agent uses plain bash blocks with no tool-calling interface [2]. CodeAct argued for code as the action format over JSON tool calls, across several models [3]. Tam et al. found that forcing structured output can reduce reasoning quality on other tasks [8]; the fading of thinking in my `json` arm points the same way, though I did not test their setting.

On Gemma 4 and this competition: ai-muninn reports 116 of 300 on SWE-bench Lite for Gemma 4 26B [9] and the two-framework comparison described above [4]. dmitriigluzdov's notebook and dataset give per-task results for three model sizes, eight agent designs on 70 tasks, and the soundness list I started from [5]. zhukovoleksiy's walkthrough reports 23 tasks solved with thinking off against 48 to 51 with it on [6], which is why the fading of thinking in the tool-call arm matters. None of these changes only the action format.

## 5. Limitations

- **Floor effect.** With 2 and 1 fixes [A], the fix-rate comparison has almost no power. The behavioural counts rest on hundreds of turns; the fix counts do not.
- **One model, one seed.** Only the 12B model, seed 0. Public work measured the same submission scoring 0.12, 0.10 and 0.06 on reruns [6], so single fixes here are within noise.
- **My loop is not the host's agent.** The `json` arm has two tools, where the host's sample agent has nine. Results say nothing about the leaderboard.
- **Time is measured under load.** The 15-minute limit ran with 20 runs sharing the server. A faster server would give the `text` arm more turns, though the share of tokens wasted would not change.
- **Tasks are not independent.** They come from four repositories, and [N] after the gate come from two or three.
- **The gate removes tasks.** About 4 in 10 sound tasks failed my environment's reference-patch check. They are listed, with exit codes, in `controls.csv`.
- **The output cap and the turn limit shape the result.** A lower cap would make run-on turns cheaper; a higher turn limit would let `json` search longer.

## 6. What this means for building on Gemma 4

Measured here, for the 12B model on the competition's server settings:

1. Don't choose text actions to avoid broken tool calls. Tool calls were malformed in about 1% of turns [A].
2. If you use text actions, end the turn yourself. Without that, 80% of output tokens went to text after the action [A].
3. If you use tool calls, check that the model is still thinking after the first few turns. Here it mostly was not, and public results say thinking roughly doubles the solve rate [6].

What I did not measure is whether fixing either problem raises the fix rate. Section 3.4 is a first look at the second.

## Reproducing

Notebooks (code, logs and outputs): [LINKS]. Each writes `results.csv` (one row per task, arm and seed), `turns.jsonl` (one row per turn: counts only, no task text), `controls.csv` and `prompt_diff.txt`. Task texts and transcripts are not published, as the competition's rules require.

## References

1. Yang et al., "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering", NeurIPS 2024. https://arxiv.org/abs/2405.15793
2. mini-SWE-agent. https://github.com/SWE-agent/mini-swe-agent
3. Wang et al., "Executable Code Actions Elicit Better LLM Agents", ICML 2024. https://arxiv.org/abs/2402.01030
4. ai-muninn, "SWE-bench with local models: the framework matters", Apr 13 2026. https://ai-muninn.com/en/blog/swe-bench-local-models-framework-matters
5. dmitriigluzdov, "Gemma 4: task soundness, serving and evaluation" (notebook) and "Gemma 4 Task Soundness and Local Results" (dataset, CC BY 4.0). https://www.kaggle.com/code/dmitriigluzdov/gemma-4-task-soundness-serving-and-evaluation and https://www.kaggle.com/datasets/dmitriigluzdov/gemma-4-task-soundness-and-local-results
6. zhukovoleksiy, "Gemma 4 | Walkthrough, Findings & Submission". https://www.kaggle.com/code/zhukovoleksiy/gemma-4-walkthrough-findings-submission
7. Jimenez et al., "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?", ICLR 2024. https://arxiv.org/abs/2310.06770
8. Tam et al., "Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models", 2024. https://arxiv.org/abs/2408.02442
9. ai-muninn, "SWE-bench Lite with Gemma 4 26B", Apr 17 2026. https://ai-muninn.com/en/blog/swe-bench-lite-gemma4-26b-38-percent
