# Business Analytics Portfolio: used-car pricing and HR attrition (supervised learning)

**PGP in AI/ML (UT Austin McCombs), May – Jun 2024.** Notebook in [`Business_Analytics_Portfolio_SL/`](../Business_Analytics_Portfolio_SL/).

> ⚠️ **Correct the card.** It said "86% accuracy on used-car price prediction". Price prediction is **regression**, scored by **R²: 0.647 → 0.869** after improvements (the "86%" was an R², not an accuracy). On attrition, a logistic/default model scored **84% test accuracy**, and the tuned tree model **96.6%** (with 100% training accuracy, so check for overfitting). Fixed in this update.

## The 30-second version
- **Part A, Cars4U (used-car pricing):** linear regression on car attributes (age, mileage, engine, power, brand…), with feature engineering and log-transformed price taking R² from 0.647 to **0.869**.
- **Part B, employee attrition (healthcare HR data):** classification of who leaves. Test accuracy 0.84 for the baseline and 0.97 (`Test Set Accuracy with Best Parameters: 0.966`) for the grid-searched model.

## The four FDE angles
1. **Architecture:** scikit-learn regression and classification in a notebook, GridSearchCV for tuning.
2. **Data & security:** **HR attrition data is sensitive personal data.** A real deployment needs consent and purpose limits, exclusion of protected attributes, and a policy that the model informs retention conversations, never decisions about individuals.
3. **Reliability:** a perfect training score (1.00) next to 0.97 test is a mild overfitting signal; cross-validated scores are more trustworthy than one split.
4. **Evaluation:** attrition is imbalanced (most employees stay), so accuracy flatters. Report recall on leavers and precision at the HR team's capacity. For pricing, R² plus error in rupees (MAE/RMSE on the original scale) is what a dealer understands.

## Sources
Notebook outputs (`R-squared: 0.6474`, `R-squared: 0.8690`; classification reports with test support 588; `Test Set Accuracy with Best Parameters: 0.9659863945578231`); `README.md`.
