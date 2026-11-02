# YouTube AdView Analytics (Internship Studio ML internship)

**Machine Learning Internship, Internship Studio, Jul – Aug 2024** (certificate ID ISMAIL600552). Notebook, data and the saved model in [`YouTube_AdView_Analytics_ML/`](../YouTube_AdView_Analytics_ML/).

## The 30-second version
Predict how many ad views a YouTube video gets from its metrics (views, likes, dislikes, comments, duration, category, publish date) across **~15,000 videos**. Log transforms for skewed counts, temporal features from publish dates, then five regressors compared. **Best: Random Forest, R² = 0.252, MSE = 2.700** (Neural Network 0.208; Linear Regression 0.024; SVR −0.009; Decision Tree −0.475). The model is saved (`models/best_rf_model.pkl` + the training column list) for scoring new data.

**Say the number plainly:** R² 0.25 means the features explain a quarter of the variance in (log) ad views. It's a weak predictor. Useful as a ranking signal, not for forecasting a specific video's revenue.

## The four FDE angles
1. **Architecture:** a notebook with scikit-learn and Keras; the model pickled with its expected columns, so a scoring script can align new data. Packaging the column list with the model is the bit that makes it deployable.
2. **Data & security:** public video metadata; no personal data.
3. **Reliability:** a pickled scikit-learn model is tied to library versions (pin them); new categories at scoring time need handling; an input-schema check against `X_train_columns.pkl`.
4. **Evaluation:** a held-out test set with R² and MSE. The decision tree's negative R² shows a single tree overfitting badly; the forest averages that out. What I'd add: a baseline (predict the median), and error by category.

## Sources
`YouTube_AdView_Analytics_ML/README.md` (dataset, preprocessing, model comparison); `models/`, `data/processed/test_predictions.csv`; internship certificates in `certificates/`.
