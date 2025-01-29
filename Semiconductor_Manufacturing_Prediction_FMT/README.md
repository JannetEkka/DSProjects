# Feature Selection and Classification Model Development for Semiconductor Manufacturing Yield Prediction

## Project Overview
This project focuses on developing a machine learning solution for predicting pass/fail yields in semiconductor manufacturing processes. Through feature selection and advanced modeling techniques, we aim to identify the most relevant signals from manufacturing sensor data to optimize quality control processes.

## Business Context
In modern semiconductor manufacturing, processes are monitored through numerous sensors and measurement points. While extensive data is collected, not all signals contribute equally to predicting manufacturing outcomes. This project aims to:
- Identify the most relevant signals for yield prediction
- Enable process engineers to determine key factors affecting yield
- Increase process throughput and reduce per-unit production costs
- Decrease time-to-learning in the manufacturing process

## Dataset Description
- **Source**: Manufacturing process sensor data
- **Size**: 1,567 samples with 591 features
- **Target Variable**: Binary classification (Pass/Fail)
  - -1: Pass
  - 1: Fail
- **Features**: Sensor measurements and process variables

## Technical Implementation

### Data Preprocessing
1. Null Value Handling
   - Removed features with >20% null values
   - Mean imputation for remaining null values
   
2. Feature Selection
   - Removed constant value features
   - Handled multicollinearity
   - Applied dimensionality reduction techniques

3. Data Cleaning
   - Standardization of features
   - Class imbalance correction using SMOTE
   - Train-test split with statistical validation

### Modeling Approach
Implemented and compared multiple classification algorithms:
- Support Vector Classifier (SVC)
- Random Forest
- Gradient Boosting
- Logistic Regression

### Model Optimization
- Cross-validation techniques
- Hyperparameter tuning using GridSearchCV
- Feature importance analysis
- Model performance enhancement through PCA

## Results
- Best performing model: Support Vector Classifier (SVC)
- Achieved test accuracy: 99.20%
- Robust performance across precision, recall, and F1-score metrics

## Project Structure
```
├── data/
│   └── signal-data.csv
├── Final_FMTProject.ipynb
├── finalized_model.sav
└── README.md
└── requirements.txt
└── .gitignore
```

## Technical Requirements
- Python 3.8+
- Key Libraries:
  - pandas
  - numpy
  - scikit-learn
  - imbalanced-learn
  - seaborn
  - matplotlib

## Usage
1. Clone the repository
2. Install required packages: `pip install -r requirements.txt`
3. Run the notebooks in sequence

## Future Improvements
1. Feature Engineering
   - Explore advanced feature selection methods
   - Investigate domain-specific feature creation
   
2. Model Development
   - Experiment with deep learning approaches
   - Implement ensemble methods
   
3. Production Deployment
   - Develop API for model serving
   - Implement model monitoring and retraining pipeline

## Contributors
- Jannet Akanksha Ekka
- Shelton Maharesh

## License
Proprietary content. ©Great Learning. All Rights Reserved. Unauthorized use or distribution prohibited.