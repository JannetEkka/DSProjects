# Semiconductor Yield Prediction (591 sensor signals)

**PGP in AI/ML (UT Austin McCombs), Sep – Oct 2024.** Notebook in [`Semiconductor_Manufacturing_Prediction_FMT/`](../Semiconductor_Manufacturing_Prediction_FMT/).

> ⚠️ **A leak in my own notebook, worth telling in an interview.** The README reports **SVC test accuracy 99.20%**. The notebook applies **SMOTE to the whole dataset (cell 25) *before* `train_test_split` (cell 27)**, so synthetic minority samples built from points that land in the test set are also in training, and the test set contains synthetic points too. **The 99.2% is inflated.** The right order is split first, then SMOTE on the training fold only (or `imblearn.pipeline.Pipeline` inside cross-validation). Don't quote 99.2%. Quote the leak and the fix.

## The 30-second version
Predict pass/fail yield from **1,567 production runs × 591 sensor and process features** (SECOM-style data: few failures, many noisy or constant signals). Feature selection removed features with >20% nulls and constant features, then standardisation, SMOTE for the imbalance, and PCA; models compared, with SVC the best.

## The four FDE angles
1. **Architecture:** scikit-learn + imbalanced-learn in a notebook. In a fab this is batch scoring per lot, close to the MES; the value is in **which signals matter**, which engineers can act on.
2. **Data & security:** fab process data is commercially sensitive (it reveals the process), so it stays on-premise. That's a strong argument for models that run inside the customer's environment.
3. **Reliability:** sensors drift and get recalibrated, so monitor feature distributions per tool and per recipe and retrain on drift. Nulls are structural (a sensor not on that tool), so imputation choices need process knowledge.
4. **Evaluation:** with rare failures, accuracy is meaningless (predicting "pass" for everything already scores ~93%). Report **recall on failures and precision at the review capacity**, on a test set that never saw SMOTE.

## Sources
`Semiconductor_Manufacturing_Prediction_FMT/README.md` (dataset size, preprocessing, SVC 99.20%); `Final_FMTProject.ipynb` cells 25 (SMOTE on X, y) and 27 (`train_test_split` on the resampled data).
