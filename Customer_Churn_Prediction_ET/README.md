# Customer Churn Prediction in Telecom: A Comparative Analysis of Ensemble Learning Techniques

## Project Overview

This project focuses on developing machine learning models to predict customer churn for a telecom company using historical customer data. The goal is to identify customers with a high probability of churning, enabling the company to implement targeted retention strategies.

## Business Context

Customer churn is a critical challenge in the telecom industry. By leveraging machine learning to predict potential churners, the company can:
- Proactively identify at-risk customers
- Understand patterns and pain points leading to churn
- Develop focused customer retention programs
- Reduce customer acquisition costs
- Maintain competitive advantage in the market

## Dataset Description

The dataset comprises customer information including:
- Demographic data (gender, age range, partner status, dependents)
- Services subscribed (phone, internet, security, streaming)
- Account information (tenure, contract type, payment method)
- Billing details (monthly charges, total charges)
- Churn status

## Technical Implementation

### Data Preprocessing
- Merged two separate datasets using customerID as the key
- Handled missing and unexpected values
- Converted continuous variables to float type
- Performed categorical feature encoding
- Applied data normalization/standardization

### Models Implemented
1. Decision Tree
2. Random Forest
3. AdaBoost
4. Gradient Boosting

Each model was implemented in two stages:
- Initial implementation with default parameters
- Optimized implementation using GridSearchCV for hyperparameter tuning

### Model Performance Summary

#### Best Performing Model: Random Forest with Grid Search
- Training Accuracy: 84.59%
- Testing Accuracy: 81.48%

Key factors contributing to its success:
- Ensemble learning approach
- Effective feature randomness
- Robust handling of complex relationships
- Resistance to overfitting
- Stability across different data subsets

### Insights and Conclusions

The analysis revealed that:
1. Hyperparameter tuning significantly improved model performance
2. Random Forest demonstrated superior generalization ability
3. Ensemble methods generally outperformed single decision trees
4. Grid search optimization helped reduce overfitting

## Project Structure

```
customer_churn_prediction/
├── data/
│   ├── TelcomCustomerChurn_1.csv
│   └── TelcomCustomerChurn_2.csv
├── Ensemble_Techniques_Project_Jannet.ipynb   # main notebook
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
└── .gitignore                    # Git ignore file
```

## Technical Requirements

- Python 3.x
- Required packages:
  - pandas
  - numpy
  - scikit-learn
  - matplotlib
  - seaborn

## Acknowledgments

This project was completed as part of the Machine Learning curriculum at Great Learning. The dataset and project structure were provided by the institution.