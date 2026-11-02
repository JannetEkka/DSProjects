# Customer Churn Prediction (telecom, ensemble techniques)

**PGP in AI/ML (UT Austin McCombs / Great Lakes), Oct – Nov 2024.** Notebook in [`Customer_Churn_Prediction_ET/`](../Customer_Churn_Prediction_ET/).

## The 30-second version
Predict which telecom customers will cancel so retention can target them. Two datasets merged on `customerID`. Four models (**Decision Tree, Random Forest, AdaBoost, Gradient Boosting**), each first with defaults and then tuned with **GridSearchCV**. **Best: Random Forest with grid search, 84.59% train / 81.48% test accuracy.** (The portfolio card said "comparing Bagging, AdaBoost and Gradient Boosting"; the README lists DT, RF, AdaBoost and GB. Card corrected.)

## The four FDE angles
1. **Architecture:** scikit-learn pipelines in a notebook. Why ensembles: tabular data with mixed categorical and numeric features is where tree ensembles do well with little tuning.
2. **Data & security:** customer-level telecom data is personal data. In a real deployment it stays in the operator's environment; model features shouldn't include protected attributes, and retention offers driven by a model raise fairness questions (who gets discounts).
3. **Reliability:** batch scoring (monthly) is the natural fit, with drift monitoring on tenure and contract mix, and retraining on a schedule.
4. **Evaluation:** **accuracy is the wrong headline for churn**, because churners are the minority class. I'd report recall on churners, precision at the retention budget (e.g. top 10% riskiest), and lift vs random targeting, which is the number that converts to retained revenue. The project reports accuracy; I'd say that and give the better metric.

## Sources
`Customer_Churn_Prediction_ET/README.md` (models, two-stage tuning, best model and accuracies).
