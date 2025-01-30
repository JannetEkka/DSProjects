# New-Wheels Performance Analytics: Transforming Customer Feedback and Sales Data into Strategic Business Insights

## Project Overview
This project analyzes the performance metrics of New-Wheels, a vehicle resale company, focusing on customer satisfaction, sales trends, and operational efficiency. The analysis aims to address declining sales and customer feedback issues by providing actionable insights through comprehensive data analysis.

## Business Context
New-Wheels operates in the pre-owned vehicle market, offering end-to-end services from vehicle listing to delivery through their platform. The company has faced challenges with:
- Declining sales trends
- Decreasing customer satisfaction
- Reducing new customer acquisition

## Objectives
1. **Customer Analysis**
   - Analyze geographical distribution of customers
   - Track customer satisfaction trends
   - Identify vehicle preferences across regions

2. **Sales Performance**
   - Monitor quarterly sales trends
   - Analyze revenue patterns
   - Evaluate order volumes

3. **Operational Efficiency**
   - Assess shipping performance
   - Analyze discount strategies
   - Review credit card usage patterns

## Data Structure
The project utilizes four main tables:
- **customer_t**: Customer demographics and payment information
- **order_t**: Order details, shipping information, and customer feedback
- **product_t**: Vehicle specifications and pricing
- **shipper_t**: Shipping partner information

## Key Metrics
- Total Customers: 994
- Overall Customer Satisfaction: 3.06/5
- Total Revenue: $1.25B
- Average Shipping Time: 21.5 days
- Percentage of Good Feedback: 98%

## Key Findings

### Customer Insights
- California, Texas, and Florida are the top markets by customer count
- Customer satisfaction shows a declining trend across quarters
- Chevrolet, Ford, and Toyota are the most preferred vehicle makers

### Revenue Patterns
- Consistent decline in quarterly order volumes
- Revenue shows correlation with order volume trends
- Significant variations in quarter-over-quarter performance

### Operational Metrics
- Uniform discount distribution across credit card types
- Shipping times vary by quarter
- Regional preferences for specific vehicle brands

## Technical Implementation
The analysis utilizes:
- SQL for data extraction and transformation
- Python for data analysis
- Libraries: pandas, matplotlib, seaborn
- MySQL database for data storage

## Recommendations

### Market Strategy
1. Focus on retention in high-density markets (CA, TX, FL)
2. Develop targeted expansion plans for underserved states
3. Align inventory with regional brand preferences

### Customer Experience
1. Implement robust feedback collection system
2. Develop customer engagement programs
3. Enhance after-sales support

### Operational Improvements
1. Optimize shipping timelines
2. Review discount strategy effectiveness
3. Strengthen partnerships with popular vehicle makers

## Project Structure
```
project/
├── data/
│   ├── new_wheels_sales.txt
│   └── new_wheels_dumpfile.sql
├── sql/
│   └── analysis_queries.sql
├── python/
│   └── visualization_notebook.ipynb
├── reports/
│   └── quarterly_business_report.pdf
├── diagrams/
│   └── ER-Diagram.pdf
├── README.md
├── requirements.txt
├── .gitignore
```

## Quarterly Business Report
The comprehensive business report includes:

### Executive Summary
- Overview of company performance
- Key statistics and metrics
- Strategic recommendations

### Detailed Analysis
1. **Customer Metrics**
   - Distribution across states
   - Average customer ratings
   - Customer satisfaction trends
   - Vehicle maker preferences

2. **Revenue Metrics**
   - Quarter-wise purchase trends
   - Revenue change analysis
   - Order volume analysis

3. **Shipping Metrics**
   - Credit card discount analysis
   - Shipping time analysis

### Strategic Insights
- Detailed analysis of market concentration
- Customer satisfaction decline patterns
- Regional preferences and opportunities
- Revenue and order correlation analysis

### Action Items
- Customer engagement strategies
- Market penetration recommendations
- Operational improvement suggestions
- Innovation and growth opportunities

## Setup and Usage
1. Import the database dump file
2. Execute SQL queries for analysis
3. Run Python notebook for visualizations
4. Generate quarterly reports

## Future Scope
- Real-time dashboard development
- Predictive analytics for sales forecasting
- Customer churn prediction
- Automated reporting system

## Contributors
- Jannet Akanksha Ekka (Project Lead & Analysis)

## License
This project is proprietary and confidential to New-Wheels.