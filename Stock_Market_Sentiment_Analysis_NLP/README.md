# Stock Market Sentiment Analysis and Automated News Summarization: A Machine Learning Approach to Financial Market Intelligence

## Project Overview
This project implements an AI-driven sentiment analysis system that processes financial news articles to gauge market sentiment and generate automated weekly summaries to enhance stock price predictions and optimize investment strategies. The system combines natural language processing (NLP), machine learning, and large language models to provide actionable insights for financial analysts.

## Business Context
Stock prices of companies listed on global exchanges are influenced by various factors, including financial performance, innovations, collaborations, and market sentiment. With the vast volume of news and opinions from diverse sources, investors and financial analysts often struggle to stay updated and accurately interpret market impacts. This project addresses this challenge by leveraging artificial intelligence to analyze and summarize stock-related news.

## Required Files

### Source Files
The following files are required to run the project:
1. `data/stock_news.csv` - Main dataset with stock prices and news
2. `embeddings/glove.6B.100d.txt` - GloVe embeddings file
   - Download from: https://drive.google.com/file/d/1O7USNidW4RNfk8DirwNgESo6rqLAVJ6H/view?usp=sharing 

The Mistral LLM model will be automatically downloaded during notebook execution.

### Generated Files
The following files will be generated during notebook execution:
1. Processed Data:
   - `stock_news_processed.csv`
   - `sample_weekly_summaries.csv`
   - `weekly_summaries_batch_*.csv`
   - `weekly_summaries_complete.csv`

2. Model Outputs:
   - `all_embeddings_results.npz`
   - `balanced_training_data.npz`
   - `best_sentiment_model.joblib`
   - `ensemble_sentiment_model.joblib`

3. Converted Embeddings:
   - `glove.6B.200d.word2vec.txt`

## Project Structure
```
stock_market_sentiment/
├── data/
│   └── stock_news.csv
├── embeddings/
│   └── glove.6B.100d.txt
├── notebooks/
│   └── NLPProject5.ipynb
├── .gitignore
├── LICENSE.md
└── README.md
```

## Installation

### Dependencies
```bash
pip install -r requirements.txt
```

### Getting Started
1. Clone the repository
2. Download required files:
   - Place `stock_news.csv` in the `data` directory
   - Download GloVe embeddings and place `glove.6B.100d.txt` in the `embeddings` directory
3. Run the notebook `NLPProject5.ipynb`

## Features
- Sentiment Analysis of financial news articles using advanced NLP techniques
- Automated weekly news summarization using Large Language Models
- Stock price movement correlation analysis
- Trading volume pattern analysis
- Data visualization and statistical analysis
- Class-balanced machine learning models

## Technical Implementation

### Data Processing Pipeline
1. Text preprocessing using NLTK
2. Feature engineering for price and volume metrics
3. Word embeddings (Word2Vec, GloVe, SBERT)
4. Class imbalance handling using SMOTE and SMOTETomek

### Models and Performance
- Individual Models:
  - RandomForest: Val F1 0.5067, Test F1 0.2958
  - GradientBoosting: Val F1 0.4817, Test F1 0.3480
  - XGBoost: Val F1 0.4610, Test F1 0.3784
- Ensemble Model:
  - Validation F1: 0.52
  - Test F1: 0.3661

### Weekly Summarization
- Implemented using Mistral-7B LLM
- Structured JSON output format
- Categorized positive and negative market events
- Market context analysis

## Key Findings

### Return Patterns
- Average daily returns typically ranged from -2.5% to -3.0%
- Highest negative returns coincided with major tech sector events
- Recovery periods showed positive momentum despite negative returns

### Sentiment Analysis Results
- Mixed sentiment throughout the analyzed period
- Weak correlation between sentiment and returns (-0.051)
- Market showed stronger reactions to negative news

### Market Themes
- Tech sector volatility
- 5G technology developments
- Supply chain impacts
- Semiconductor industry trends
- Global economic influences

## Dataset Structure
- Date: Trading date
- News: News article content
- Open: Opening stock price
- High: Highest price of the day
- Low: Lowest price of the day
- Close: Closing price
- Volume: Trading volume
- Label: Sentiment polarity (-1: negative, 0: neutral, 1: positive)

## Actionable Recommendations

### Investment Strategy
- Focus on companies with strong fundamentals regardless of market sentiment
- Consider semiconductor sector opportunities
- Monitor 5G-related investment opportunities showing resilience

### Risk Management
- Implement stop-losses due to high market volatility
- Diversify across tech subsectors
- Monitor global economic indicators affecting the tech sector

### Opportunity Areas
- Track semiconductor demand as a leading indicator
- Watch for oversold conditions in quality tech stocks
- Consider entry points during high-volume negative sentiment days

## Future Improvements
1. Incorporate real-time news feeds
2. Enhance sentiment analysis with aspect-based approaches
3. Develop automated trading signals based on sentiment indicators
4. Implement cross-asset correlation analysis
5. Add market microstructure features

## License
[MIT License](LICENSE.md)

## Contributors
Jannet Akanksha Ekka - Great Learning

## Contact
jannetekka96@gmail.com