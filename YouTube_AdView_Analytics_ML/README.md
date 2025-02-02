# YouTube AdView Analytics
## Predicting Advertisement Performance Using Video Metrics and Engagement Signals

This project was completed as part of the Machine Learning Internship at Internship Studio (July 8, 2024 - August 12, 2024).

## Project Overview
A machine learning approach to predict YouTube video advertisement views using engagement metrics like views, likes, dislikes, and comments. The project aims to help content creators and advertisers estimate potential ad performance based on video characteristics and user engagement patterns.

## Project Structure
```
youtube-adview-analytics/
│
├── data/
│   ├── raw/                      # Original datasets
│   │   ├── train_lyst1720633807653.csv           # Training dataset
│   │   └── test_lyst1720633807653.csv             # Test dataset
│   │
│   └── processed/               # Processed datasets
│       └── test_predictions.csv # Model predictions
│
├── models/
│   ├── best_rf_model.pkl        # Saved Random Forest model
│   └── X_train_columns.pkl      # Training columns reference
│
├── notebooks/
│   └── youtube_adview_analysis.ipynb  # Main analysis notebook
│
├── certificates/               # Internship certificates
│   ├── internship_completion.pdf     # Main internship certificate
│   └── training_completion.pdf       # Training completion certificate
│
├── requirements.txt             # Project dependencies
└── README.md                   # Project documentation
```

## Dataset
The dataset contains metrics for approximately 15,000 YouTube videos including:
- Video ID
- Advertisement views (target variable)
- Views, likes, dislikes, comments
- Publication date
- Video duration
- Video category

## Approach
1. **Data Preprocessing**
   - Handled missing values
   - Converted data types
   - Applied log transformation to handle skewed features
   
2. **Feature Engineering**
   - Extracted temporal features from publication dates
   - Converted duration to seconds
   - Created category dummy variables

3. **Model Implementation**
   - Experimented with multiple regression models:
     - Linear Regression
     - Support Vector Regression
     - Decision Trees
     - Random Forest
     - Neural Networks (Keras)
   - Performed hyperparameter tuning using RandomizedSearchCV

## Results
Model performance comparison:
- Random Forest: R² = 0.252, MSE = 2.700 (Best Performance)
- Neural Network: R² = 0.208, MSE = 2.859
- Linear Regression: R² = 0.024, MSE = 3.525
- Support Vector Regression: R² = -0.009, MSE = 3.643
- Decision Tree: R² = -0.475, MSE = 5.328

## Tools Used
- Python, Pandas, NumPy
- Scikit-learn
- TensorFlow/Keras
- Seaborn, Matplotlib

## Certification
Successfully completed Machine Learning Internship at Internship Studio and received certification for project implementation and training completion.