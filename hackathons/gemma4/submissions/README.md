# Submissions to the Gemma 4 Developer Agent main track

Each folder holds exactly the files that went into one `submission.zip` (zip the folder's contents, with `agent.yaml` at the root). Notes live here, not in the folders, so they never end up inside an archive.

| # | Folder | What it is | Model | Submitted | Public score |
|---|---|---|---|---|---|
| 1 | `01-public-baseline/` | **Not our work.** The unmodified public config from bliverrigpdoge, ["LB 0.22, 3 tweaks, 40 tool calls, no training"](https://www.kaggle.com/code/bliverrigpdoge/lb-0-22-3-tweaks-40-tool-calls-no-training), which builds on verracodeguacas's [Budget-Fit Single Agent](https://www.kaggle.com/code/verracodeguacas/gemma-4-agent-budget-fit-single-agent) (version 5). Bundle digest `a6c6460094d8` matches the author's. Purpose: get on the board, and serve as the baseline config for the measurement in `../design.md`. | 31B | waiting on Jannet's approval (11-27) | — |

Why not the host's `sample_submission` as is: its `eval_config.yaml` gives each task 1 minute and 10 tool calls, and its two LoRA adapters are placeholders (rank 4, one layer). It's a smoke test, not a baseline.

How it was built: `ast.literal_eval` on the `FILES` dict in the notebook's code cell (no notebook code was run), then the same sorted, deflated zip the notebook writes. The digest check is the notebook's own.
