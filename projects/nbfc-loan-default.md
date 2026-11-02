# NBFC Loan Default Prediction (Great Learning hackathon)

**Great Learning hackathon, Feb 2025** (portfolio card); the repo was created Jan 17, 2025 with one commit.
**Code:** [github.com/JannetEkka/NBFC-Loan-Default](https://github.com/JannetEkka/NBFC-Loan-Default)

> ⚠️ **What's actually in the repo:** four Word documents (`EDA_and_Preprocessing.docx`, `Model_Development.docx`, `Final_Prediction.docx`, `Utils.docx`) holding **Colab notebook code pasted as text**: Drive mount, EDA and feature engineering, a TensorFlow dense network (`hidden_units: [256, 128, 64]`) with custom `ModelCheckpoint` / `EarlyStoppingWithPatience` utilities, and a submission writer. There's **no score, no dataset description and no results in the repo.** Fill in from memory (metric, leaderboard position) or keep this one light in interviews.

## The 30-second version
A binary classifier predicting whether a non-banking financial company's client will default, built under hackathon time limits: preprocessing (scaling, label encoding), a dense neural net with early stopping and checkpointing, and a submission file.

## The four FDE angles, honestly
1. **Architecture:** Colab notebooks + Google Drive storage; TensorFlow/Keras; scikit-learn preprocessing. A batch modelling task: no service, no database. If asked "why a neural net for tabular credit data?", the honest answer is that gradient-boosted trees are usually the stronger baseline on tabular data, and I'd benchmark XGBoost/LightGBM first today.
2. **Data & security:** loan applicants' financial data is sensitive. In a real NBFC deployment: data stays in the lender's environment, PII is minimised before modelling, and protected attributes are checked for **disparate impact** (credit decisions are regulated, and RBI guidance on fair lending applies in India).
3. **Reliability:** checkpointing and early stopping are the only failure handling (training-time). In production: model versioning, input-schema validation, and drift monitoring on applicant features.
4. **Evaluation:** the metric isn't recorded in the repo. For default prediction, ROC-AUC plus precision/recall at the lender's operating threshold, and the cost asymmetry (a missed default costs more than a rejected good client) should set the threshold.

## Weak spots to own
- Code in .docx files is not reproducible; no results recorded. I'd convert it to notebooks and add the score before showing it.

## Sources
The repo's four .docx files (text extracted) and its single commit (2025-01-17); `_portfolio_src/data.py` card.
