# Same model, same bugs, two formats: a paper on Gemma 4 coding agents

**Kaggle Gemma 4 Developer Agent, Paper Track, Nov 2026.** Brief 11-11/12, study run on Kaggle 11-12/13, Writeup submitted by Jannet before Nov 13, 05:29 IST. Result: pending when written (11-16).
**Paper:** [Kaggle Writeup](https://www.kaggle.com/competitions/gemma-4-developer-agent-paper/writeups/same-model-same-bugs-two-formats) · **Data, notebook and text:** [`hackathons/gemma4-paper/`](../hackathons/gemma4-paper/) · tracker [DSProjects#100](https://github.com/JannetEkka/DSProjects/issues/100)

## The 30-second version

A common belief: small local models do better writing actions as plain-text shell commands than as JSON tool calls, because structured calls break. I tested only that. Gemma 4 12B (untuned), the competition's public bug-fix tasks, one shell-command capability, the same model file, server settings, prompt (one line differs), budget and checker. **Tool calls fixed 3 of 68 and bash blocks fixed 3 of 68.** The format changed how the budget was spent: bash-block replies ran to the output cap in 22% of turns, and tool-call turns often had no thinking. Cutting the reply after the first bash block fixed 11.

## 1. Method (what an interviewer will ask)

- **Tasks:** started from 114 tasks marked sound by a public audit, in a fixed order (SHA-256 of the task id) set before any run. A checker gate (the reference patch must pass, the empty patch must fail) kept 68.
- **Arms:** `json` (two tools via vLLM's `gemma4` tool-call parser), `text` (one fenced bash block per turn), and `text_stop` (added after the pilot: the same as `text`, but the stream is closed after the first complete block).
- **Settings:** `gemma-4-12b-it-qat-w4a16-ct` on vLLM as in the host's starter notebook, Kaggle 4× L4, temperature 0.2, 50 turns and 15 minutes per task. `json` and `text` runs of a task started together on the same server so both saw the same load.
- 204 runs, no harness errors. Every turn is in `results/turns.jsonl`.

## 2. Results

| 68 tasks, one run per arm | Tool calls | Bash blocks | Bash, cut after first block |
|---|---|---|---|
| Tasks fixed | 3 | 3 | 11 |
| Malformed turns | 30 of 2,403 | 4 of 637 | 7 of 1,380 |
| Turns that ran to the output cap | 23 | 141 | 7 |
| Turns with no thinking text | 1,442 of 2,403 | 2 of 637 | 40 of 1,380 |

- Paired json vs text: 4 disagreements, exact sign test p = 1.0. With 3 fixes per arm, only a large difference could have been detected.
- Format errors were rare in every arm, so "structured calls break" did not hold with two tools and the server's own parser.
- What it lets an agent builder do: handle the failure they'll actually get (a turn that doesn't end, or a model that stops thinking) instead of the one they expect.

## Weak spots to own before they ask

- One run per arm, one model size, a bare loop (low fix rates). `text_stop` ran afterwards in its own notebooks, not alongside the other two, so its server load differed slightly (22.9 vs 20.6–21.2 output tokens/s).
- I can't tell whether the missing thinking after tool results is the model's habit, the chat template or the reasoning parser.
- The checklist item "Jannet explains the results back" was not done before submitting.

## Sources

`hackathons/gemma4-paper/writeup.md` (method and results), `results/tables.md`, DSProjects#100.
