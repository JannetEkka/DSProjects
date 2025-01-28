# Business Analytics Portfolio: Predictive Modeling for Automotive Pricing and Healthcare HR Analytics

## Project Overview
This repository contains two comprehensive data science projects focusing on predictive modeling in the automotive and healthcare sectors:

1. **Used Car Price Prediction (Cars4U)**
   - Developed a pricing model for a budding tech startup to effectively predict used car prices
   - Analyzed market trends and pricing patterns in the Indian automotive market
   - Created models to support profitable pricing strategies

2. **Employee Attrition Prediction (McCurr Healthcare)**
   - Built predictive models to identify employees at risk of attrition
   - Analyzed patterns in employee characteristics and workplace factors
   - Provided data-driven recommendations for targeted retention strategies

## Technologies Used
- Python
- Pandas
- NumPy
- Scikit-learn
- Seaborn
- Matplotlib

## Part A: Cars4U Price Prediction

### Dataset Description
The dataset contains information about used cars including:
- Car specifications (brand, model, year, mileage)
- Performance metrics (engine size, power)
- Price indicators (new price, used price)
- Usage history (kilometers driven, ownership)
- 7,253 entries with 14 features

### Key Findings
- Significant correlation between car price and factors such as:
  - Age of the vehicle
  - Kilometers driven
  - Engine power
  - Brand reputation
- Automatic transmission vehicles command higher prices
- Diesel vehicles show higher average prices compared to petrol
- Location impacts pricing, with major cities showing distinct patterns

### Models Developed
1. **Linear Regression (Original Price)**
   - Standard price prediction
   - Performance metrics show moderate predictive capability

2. **Linear Regression (Log-transformed Price)**
   - Improved model performance
   - Better handling of price variations
   - More accurate predictions across price ranges

## Part B: McCurr Healthcare Attrition Analysis

### Dataset Description
Employee data including:
- Demographic information
- Work-related metrics
- Satisfaction indicators
- Career progression data
- Attrition status

### Key Insights
- Significant attrition factors identified:
  - Overtime work
  - Job satisfaction levels
  - Years in current role
  - Distance from home
  - Age and experience level

### Models Developed
1. **Logistic Regression**
   - Accuracy: 86%
   - Strong performance in predicting retention
   - Identified key attrition indicators

2. **K-Nearest Neighbors**
   - Improved accuracy after parameter tuning
   - Better at handling non-linear relationships
   - Strong performance on both classes

## Business Recommendations

### For Cars4U
1. Implement dynamic pricing strategies based on:
   - Vehicle age and condition
   - Market demand patterns
   - Regional pricing variations
2. Focus on high-demand segments
3. Consider seasonal pricing adjustments

### For McCurr Healthcare
1. Develop targeted retention programs focusing on:
   - Work-life balance improvements
   - Career development opportunities
   - Compensation package optimization
2. Implement early warning systems for attrition risk
3. Regular employee engagement monitoring

## Installation and Usage
```bash
# Clone the repository
git clone [repository-url]

# Install required packages
pip install -r requirements.txt

# Run the analysis notebooks
jupyter notebook
```

## Future Improvements
- Integration of more advanced machine learning models
- Real-time price prediction capabilities
- Enhanced feature engineering
- Implementation of deep learning models
- Development of web-based interfaces for predictions

## Contributing
Contributions, issues, and feature requests are welcome. Feel free to check issues page if you want to contribute.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.

## Contact
Your Name - Jannet Akanksha Ekka (jannetekka96@gmail.com)