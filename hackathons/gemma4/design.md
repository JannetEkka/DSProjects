# Design brief: a measured baseline for the Gemma 4 Developer Agent (main track)

**Process (Jannet, 11-08), compressed for 5 days:** this is the short brief Jannet asked for on 11-27 when she chose to do both (a) and (b) from the 11-23 comment on [#95](https://github.com/JannetEkka/DSProjects/issues/95). There is no separate discussion session: the Nov 16 and Nov 23 comments on #95 were the discussion. No GPU hours are spent on (a) until Jannet signs off section 9 in chat. The earlier Paper Track study is in `../gemma4-paper/` ([#100](https://github.com/JannetEkka/DSProjects/issues/100)); this brief reuses its checker control and its findings.

## 0. The hackathon, in one screen

- **What:** Google DeepMind's Gemma 4 Developer Agent competition on Kaggle, main track: https://www.kaggle.com/competitions/gemma-4-developer-agent. We're entered (API: `userHasEntered: true`).
- **Deadline:** final submissions **Dec 3, 05:29 IST** (Dec 2, 23:59 UTC), from Kaggle's API. Entry and team merging closed Nov 26.
- **Submissions:** 1 a day, up to 2 finals (Jannet picks them). A submission is a `submission.zip`: `agent.yaml` (Google ADK config) plus optional prompts, sub-agents, skills, `eval_config.yaml` and LoRA adapters, under 3 GiB. Declarative only, no Python entry point. One base model per submission, from `gemma-4-{31b,12b,e4b,e2b}-it-qat-w4a16-ct`.
- **Scoring:** resolution rate on about 120 hidden tasks from private repos, split between the public and private boards. A task counts as resolved only if its hidden tests pass with our patch; edits to test files and runner configs are stripped first (harness README, section 8).
- **Money:** none of ours. Kaggle's free GPU quota only (30 h a week; L4×4 uses it at 2×). Next refresh **Nov 28, 05:30 IST**. No card anywhere; see [../cards.md](../cards.md).

### 0a. Every point on the table

| Source | Points or prize | What it takes from us | Taking it? | If not, why |
|---|---|---|---|---|
| Main board, Overview | $37K / $18K / $10K for the top 3 | a top score on the private board | entered, not expected | the top 20 are all at 0.24 with public recipes; we joined to learn (#95) |
| "$10K for the best E2B or E4B submission", Overview | $10K | **one of our 2 finals must be an E4B or E2B submission** | **yes**: an E4B config as one final | |
| Kaggle competition points and medals (`awardsPoints: true`) | profile points | any scored submission | yes, by default | |
| Paper Track ($35K) | separate competition | the Writeup | done (#100, submitted 11-13) | |

Nothing in the rules conflicts with our own rules: no money, no card, no cloud account.

### 0b. Where the field is
- **Main board (11-27):** 19 of the top 20 at 0.24, one at 0.22. 6,961 teams.
- **Small-model board** (host's [daily notebook](https://www.kaggle.com/code/ryanholbrook/gemma-4-developer-agent-small-model-leaderboard), read 11-16): best 0.12, then 0.10 (24 teams). In #100 one identical archive scored 0.12, 0.10 and 0.06, so on that board the noise is larger than the gaps.

## 1. The idea

**One sentence:** before changing anything, measure how the public 0.22 config actually behaves on E4B and 12B in the host's own harness, twice each, so every later change (a prompt line now, a LoRA later) is compared against a real number instead of a single noisy leaderboard score.

**Why not the obvious thing (lessons 0):** the obvious thing is to tweak a prompt and submit. Plenty of public notebooks do that ([bliverrigpdoge](https://www.kaggle.com/code/bliverrigpdoge/lb-0-22-3-tweaks-40-tool-calls-no-training), [verracodeguacas](https://www.kaggle.com/code/verracodeguacas/gemma-4-agent-budget-fit-single-agent), [flexonafft](https://www.kaggle.com/code/flexonafft/gemma-4-budget-aware-short-prompt)). The closest to ours is [denpugovkin's Repair Lab](https://www.kaggle.com/code/denpugovkin/gemma-4-repair-lab-compare-before-you-submit), which says outright that a real paired evaluation is "NOT_RUN". Nobody public reports paired, repeated runs of one config on the small models, or counts thinking per turn inside the host's harness.

**Other options considered (from #95):** a LoRA run (no time to train and then measure it properly before Dec 3); distilling from 31B (too costly, and it would overfit four public repos).

### 1a. The framing
- **One person and what it costs them:** a developer who can only run a small model offline, for example on one consumer GPU. E4B's weights are about 3 to 4 GB (harness README, section 3.1) against 16 to 18 GB for 31B. Today that choice costs half the solve rate: the best small-model score is **0.12** (host's small-model board) against **0.24** for 31B on the main board.
- **Real project, real data:** the competition's 129 public tasks from fastapi, rich, requests and httpx, graded by the host's own checker. Only the **68 tasks that passed #100's control** are used (reference patch passes, empty patch fails, `../gemma4-paper/results/controls.csv`).
- **The cheat it refuses:** a "fix" that edits the tests. The harness strips edits to test files and runner configs before grading, and our control drops any task whose tests pass with an **empty** patch (1 of 114 did in #100). Both are checked in the notebook's output, not assumed.
- **One end-to-end number:** from #100, 12B took a mean of **683 s per task** in its tool-call arm, with zero human touches once the notebook is pushed. This run reports the same for the submitted config, per model.

## 2. The measured comparison (decided before building)

**Stage 1, baseline (needs sign-off):**
- **Config:** exactly `submissions/01-public-baseline/`, with only `model:` swapped to E4B or 12B. Same prompt, sampling (temperature 0.2, top_p 0.95, `max_output_tokens` 8192, thinking budget 4096, thoughts kept), and budget (40 tool calls, 8 minutes, 80 turns, 240 s per command).
- **Runs:** 68 tasks × {E4B, 12B} × 2 repeats = **272 runs**, through the host's `swegemma` `Evaluator`, as in the host's Getting Started notebook.
- **Numbers reported, each with its count:**
  1. Tasks resolved per model per repeat, and how many tasks flip between the two repeats of the same model (the noise floor).
  2. **Thinking per turn index:** the share of model turns with non-empty thought text, in buckets (turn 1, 2–5, 6–15, 16+), from the harness traces. This tests #100's finding that 12B had thinking in 68 of 68 first turns but in only 197 of 1,418 turns from turn 16 on.
  3. How each run ended: submitted, out of tool calls, out of time, output cap hit, no patch.
  4. The run settings as the harness actually recorded them: turn limit, time limit, output cap, runs in flight, GPU count.

**Stage 2, one prompt-only change (proposed after stage 1, not before):** pick one change aimed at the largest failure count from stage 1 (for example, if thinking fades, one line asking for a short reason before each tool call). Run it on **E4B only**, same 68 tasks, 2 repeats, same seeds. It becomes a daily submission (E4B, so it also enters the $10K small-model race) only if it gains more than the repeat-to-repeat flips from stage 1 **and** the exact sign test on tasks that differ gives p < 0.05. With 68 tasks and fix rates of 5 to 25%, that needs roughly 8 more tasks fixed than lost; a gain of 3 or 4 tasks will be reported as noise.

**If it isn't good:** we post the counts as they are. A baseline with no gain is still the "before" number the learning goal needs. No invented baselines or improvements (writing rule, 10-31).

## 3. What Jannet sees in the first 10 seconds

One table on #95: rows E4B run 1, E4B run 2, 12B run 1, 12B run 2; columns resolved of 68, flips between repeats, share of turns with thinking at turn 1 and at 16+. Headline: "Same config, two runs, real noise."

## 4. Architecture

```
Kaggle notebook (free GPU, internet off; we push it with the patched kaggle CLI)
 ├─ wheelhouse + swegemma, installed as the host notebook does
 ├─ vLLM server (host settings: gemma4 tool and reasoning parsers, 32,768 context)
 ├─ control gate: reference patch must pass, empty patch must fail (code from ../gemma4-paper)
 ├─ swegemma Evaluator, our config, model swapped; N runs in flight
 ├─ outputs: task_results.jsonl, traces/, patches/ per (model, repeat)
 └─ summary cell: resolved counts, flips, thinking by turn bucket, stop reasons → results.csv
```

- **Model judgment vs fixed rules (lessons 4):** the model chooses each tool call. Everything else is code: which tasks run (the control's fixed list), when a run stops (the harness budget), whether it's resolved (the host's checker), what counts as "thinking" (non-empty thought text in the trace), and the stage-2 go/no-go rule above.
- **One agent, no roles.** The config is the public single-agent one; changing the agent design would confound the baseline.

## 5. The flow, step by step

1. Wait for the quota refresh (Nov 28, 05:30 IST) and Jannet's sign-off.
2. Push one notebook per model (E4B first), so a failure costs half the hours, not all of them.
3. The notebook prints the GPU count and settings, runs the control gate, and **stops** if fewer than 60 of the 68 tasks pass (a sign the environment differs from #100's).
4. Runs repeat 1, then repeat 2, writing results after every task so a timeout still leaves usable rows.
5. Summary cell builds every number from the saved files. Nothing is typed by hand.
6. Pull the outputs, commit the CSVs (not task texts or full traces: they carry competition data), post on #95 with GPU hours used.
7. Propose the stage-2 change to Jannet in one message; run it only on her OK.

## 6. Decisions settled now

- **Step (b) config:** the public 0.22 config, unmodified and credited, not the host's sample (whose 1-minute, 10-call budget and placeholder adapters make it a smoke test).
- **Runs in flight:** 8 (vLLM batches them; #100 ran 6). Recorded, and the same for every run.
- **GPU hours:** worst case 272 runs × 8 min ÷ 8 in flight ≈ 4.5 h, plus about 1 h for the control gate and two server starts: **about 5.5 h of runtime, or about 11 quota hours if the machine is L4×4 at 2×**. If the E4B notebook uses more than 6 quota hours, the 12B notebook runs one repeat, not two, and the post says so.
- **Kaggle access:** as in `../gemma4-paper/design.md` section 6 (proxy-injected token, patched CLI in a scratch venv). No token in any file or variable.
- **Finals:** not chosen here. Jannet picks the 2 finals; to be eligible for the $10K, one should be an E4B submission.

## 7. Acceptance conditions

- [ ] The control gate's counts are printed and posted (passes of 68; any empty-patch passes listed).
- [ ] `results.csv` has one row per planned (task, model, repeat); missing rows are listed with a reason.
- [ ] Every number in the #95 post comes from a cell over the saved files.
- [ ] The thinking-by-turn table uses the same buckets as #100, so the two can be compared.
- [ ] GPU hours used are reported from the notebook's own runtime.

## 8. Demo plan

None: there's no video or write-up in this track. The "demo" is the #95 post and its table.

## 8a. Before submitting: the points check
- [ ] Row "small-model $10K" in table 0a: is one of the 2 finals an E4B submission? Ask Jannet before Dec 2.
- [ ] Each submission's description credits any public work it uses.

## 9. Jannet's check

Before sign-off, in a sentence each:
1. Why run the same config twice before changing anything?
2. What would "thinking fades" look like in the table, and why might it matter?
3. Why does a prompt change need to beat the repeat-to-repeat flips, not just the baseline number?

- **Signed off:** _(Jannet, date)_

## 10. The build prompt

Not a separate session: the 11-27 session that wrote this brief builds and runs it after sign-off, following sections 2, 5 and 7.
