# RSNA Knee Abnormality Detection (Kaggle): a lean MRI model and a label-quality check

**Kaggle code competition, Oct 6–22, 2026.** Joined Oct 6; final picks ticked Oct 21. **Result: not placed** (10-27). Final picks: a public notebook copy at **0.958** public AUC (uses outside data, a grey zone) and **our own model at 0.918 with no outside data**.
**Code:** `JannetEkka/rsna-knee-2026` (private while the competition ran: the rules forbid private code sharing outside the team) · experiment log `docs/log.md` · tracker [DSProjects#22](https://github.com/JannetEkka/DSProjects/issues/22)

## The 30-second version

The task: 12 knee abnormalities (ACL, MCL, menisci, OA compartments, effusion, synovitis, Baker's cyst, contusion, fracture) from knee MRI, scored by macro ROC AUC, run on Kaggle with internet off and a 9-hour limit. The catch: **only 58 of 4,407 training studies (1.3%) had hand labels.** The rest had only a free-text radiology report in a dozen languages, so labels had to be extracted from reports.

What I'd talk about in an interview is the **label-quality check**: I scored the public LLM-extracted label sets against the 58 hand labels before training on them. Macro AUC vs hand labels: pilkwang (the labels everyone used) **0.870**, stevenleehans v4 **0.893**, JEV **0.904** (but JEV was tuned on these same 58, so it's optimistic), a blend **0.894**. The blend became the training target.

Our clean model's public AUC went 0.896 (one EfficientNet-B0 fold, 6 epochs) → **0.918** (a mix of B0 and ConvNeXt-nano folds trained on different label sets). The top of the board was 0.966. Two and a half weeks against medical-imaging teams made the main prizes unlikely from the start; the efficiency award was the realistic lane.

## 1. Architectural reasoning

### Database / storage
- **No database. The competition data can't leave Kaggle** (the rules forbid redistribution), so everything ran as Kaggle kernels, and git holds only code and aggregate numbers.
- **A preprocessing cache as a Kaggle output:** 3 planes × 12 slices × 256² per study (later 4 inputs, adding sagittal PD), ~10 GB. Train ≈ 819K slices, ~490 GB of DICOM, so reading the raw tree every epoch was out.
- **Weights as a private Kaggle dataset** (`rsna-knee-weights`), because a kernel's output keeps only its latest version, and `kaggle kernels output owner/slug/N` silently ignores N. Found the hard way; `tools/kg.py voutput` fetches old versions.

### Compute & hosting
- **Kaggle notebooks only, free** (30 GPU-hours a week on 2×T4), with AMD Developer Cloud credits in reserve, never used. Internet off at inference; the GPU limit is 9 h.
- **Where the runtime goes:** the recon kernel measured ~10 ms per slice decode and 2.25 s per study on one core, so decoding every test series would take ~49 min on one core. A benchmark found **headers dominated** (0.31 s/study vs 0.09–0.20 s decode), so a fast header parser (matching pydicom on 2,000 files) cut cache build from 1.49 to 0.61 s/study/core. "The efficiency lever is reading fewer series and fewer slices."

### Frameworks & libraries
- PyTorch + timm (EfficientNet-B0, ConvNeXt-nano), the Kaggle CLI driven by `tools/kg.py` (push, wait, fetch output, submit, list scores).
- **Why two small backbones instead of one big one:** with 2×T4 and a 30 GB memory cap, a big model wasn't trainable, and mixing two kinds of model beat five folds of one (below).

## 2. Data & security pipelines

### Authentication & access control
- The Kaggle CLI reads `KAGGLE_API_TOKEN` from the environment; there are no credentials in git or chat. The repo stayed private for the rules' sake.

### Data ingestion & flows
- **Batch pipeline of kernels:** recon (profile) → cache (CPU, decode and resize) → labels (LLM scores + 58 hand labels → `labels.csv`) → train (GPU, per fold) → weights dataset → infer (submission).
- **Training labels from reports:** reports exist only for train (en 1,733 · nl 658 · tr 546 · el 321 · fr 304 · de 265 · ru 220 · es 209 …), so reports are only a label source, never an input.

### Privacy & compliance
- **Outside data was the compliance question.** The host allows outside data only if free and obtainable without institutional sign-off. OAI (behind an NDA data-use agreement), fastMRI+ and SKM-TEA are disputed, and the #1 team read them as not allowed. So the final picks **hedged**: one public copy for score (it uses those weights) plus our own model with no outside data. Teacher labels from the outside-data models were generated and then **set aside** for the clean model.
- Public notebooks were forked unchanged under Apache-2.0, with a `SOURCE.md` per fork.

## 3. Reliability & failure operations

### State management
- Each kernel version is immutable on Kaggle; the log records every version with what changed. Weights moved to a versioned dataset so a later training run couldn't wipe the weights an inference kernel needed.

### Error handling & fallbacks (debugging, mostly)
- **A run of failures, each isolated by elimination:**
  - train v1: a recursive glob over the DICOM tree took 14 min, then OOM.
  - v2–v5: failed at start with an empty log and no GPU time charged. "Hello" kernels showed GPU and image were fine and each input alone was fine, but **all three inputs together failed**. Fix: one input (the cache carrying `labels.csv`).
  - v6–v8: OOM in epoch 0. cgroup memory telemetry showed host memory leaking ~80–90 MB per step to the 30 GB cap. **DataParallel was the leak** (v10 on one GPU stayed flat at 12.7 GB).
  - v9: CUDA OOM at batch 8 on one T4, so batch 4.
- **Validator caught on real data:** a 2-plane case was handled by feeding each model its own planes, recorded in `weights.json`.

### Logging & observability
- `docs/log.md`: every kernel version with what, score, runtime and notes. It's the single source of truth for what was tried.
- Lost time is recorded too: the session was down Oct 8 ~22:10 → Oct 12 17:04 UTC (3.8 days), and Oct 15–17 had no activity (3 days).

## 4. Evaluation & optimisation metrics

### Performance benchmarking

| Version | What | Public AUC |
|---|---|---|
| baseline | an unchanged public 2×T4 stack | 0.943 (>94 min) |
| lean v1 | B0, fold 0, 6 epochs | 0.896 (~4.8 min submit→scored) |
| lean v3 | B0 + ConvNeXt, fold 0 each | 0.915 |
| lean v4 | 5 ConvNeXt folds | 0.906 |
| C+ (final clean pick) | 5-fold B0 + 5-fold ConvNeXt (blend labels, 4 inputs) + older 3-input folds on old labels | **0.918** |
| helios2 copy (final pick) | heliosli's public notebook, unchanged | **0.958** |

- **What helped:** mixing two kinds of model, and models trained on different labels, helped more than better labels or the fourth input alone. **What didn't:** five folds of one backbone (0.906) didn't beat two backbones' single folds (0.915).
- **Honesty about noise:** about 390 public-test studies means differences of ±0.003 are noise. "All of these differences are within the public board's noise."
- **Efficiency lane:** lean v1's efficiency score was ≈ −1.918 vs the baseline's −1.854 (0.943 at >90 min). That's a smaller model at a fraction of the runtime.
- OOF validation was measured against the noisy LLM labels *and* the 58 hand labels, and both are reported.

### Cost & resource efficiency
- ₹0: Kaggle's free GPUs. The AMD credits weren't needed. Inference for the lean models ran in minutes rather than the baseline's 90+.

### System constraints
- 2×T4 with a 30 GB memory cap and 9 h per run; 2 GPU batch sessions at once (shard 2 of the teacher run was refused until one finished); 5 submissions a day.
- 58 hand labels is too few to validate per-label reliably. The JEV number is optimistic because it was tuned on them.

## What the history shows (real decisions)
- 10-06: recon before modelling: label scarcity, report languages, series and planes, decode cost.
- 10-07–10-08: two days of start-failures and memory leaks before the first completed run (v10).
- 10-13: tried a public 0.957 notebook (0.956); built teacher labels from it; 10-18 found the outside-data dispute and pivoted the clean model to public report-label sets plus a sagittal PD input (the ACL reads best there; ACL OOF was 0.82, one of the weakest).
- 10-19/20: label-quality check → blend labels → 4-input folds → C+ at 0.918.

## Weak spots to own before they ask
- Not placed; my best clean model is 0.04 below the top.
- The 0.958 pick is someone else's public notebook, run unchanged. I'd say that first.
- About 7 days of the 16 were lost to session outages and gaps, which the log records.
- Built with Claude Code driving Kaggle kernels from a cloud session; I made the outside-data and final-pick decisions.

## Sources
`README.md`, `docs/log.md`, `docs/recon.md`, `docs/rules.md` of `JannetEkka/rsna-knee-2026`; [DSProjects#22](https://github.com/JannetEkka/DSProjects/issues/22) final-picks comment (10-20) and result (10-27).
