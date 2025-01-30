# Stock Market Sentiment Analysis and Automated News Summarization: A Machine Learning Approach to Financial Market Intelligence

## Project Overview
This project implements an AI-driven sentiment analysis system that processes financial news articles to gauge market sentiment and generate automated weekly summaries to enhance stock price predictions and optimize investment strategies. The system combines natural language processing (NLP), machine learning, and large language models to provide actionable insights for financial analysts.

## Business Context
Stock prices of companies listed on global exchanges are influenced by various factors, including financial performance, innovations, collaborations, and market sentiment. With the vast volume of news and opinions from diverse sources, investors and financial analysts often struggle to stay updated and accurately interpret market impacts. This project addresses this challenge by leveraging artificial intelligence to analyze and summarize stock-related news.

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

## Installation and Dependencies
```python
# Required Libraries
pandas
numpy
matplotlib
seaborn
nltk
scikit-learn
xgboost
llama-cpp-python
huggingface-hub
sentence-transformers
```

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

## Project Structure
```
stock_market_sentiment/
├── data/
│   ├── raw/
│   │   └── stock_news.csv
│   └── processed/
│       ├── stock_news_processed.csv
│       ├── weekly_summaries_complete.csv
│       └── embeddings/
│           ├── all_embeddings_results.npz
│           └── glove.6B.200d.word2vec.txt
│
├── models/
│   └── sentiment_models/
│       ├── best_sentiment_model.joblib
│       └── ensemble_sentiment_model.joblib
│
├── notebooks/
│   └── NLPProject5.ipynb
```

### Getting Started with the Project Structure

1. **Initial Setup**
   - Clone the repository
   - Create a virtual environment
   - Install dependencies: `pip install -r requirements.txt`
   - Copy `.env.example` to `.env` and configure

2. **Data Processing**
   - Raw data is stored in `data/raw/`
   - Processing scripts are in `src/data/`
   - Processed data goes to `data/processed/`

3. **Model Development**
   - Model implementation in `src/models/`
   - Training scripts in `scripts/`
   - Trained models saved in `models/`

4. **Analysis and Visualization**
   - Follow notebooks in order (01 to 05)
   - Visualization code in `src/visualization/`
   - Output figures in `outputs/figures/`

5. **Testing and Documentation**
   - Unit tests in `tests/`
   - Documentation in `docs/`
   - Configuration in `configs/`

## Future Improvements
1. Incorporate real-time news feeds
2. Enhance sentiment analysis with aspect-based approaches
3. Develop automated trading signals based on sentiment indicators
4. Implement cross-asset correlation analysis
5. Add market microstructure features

## Download Required Files
Due to size limitations, some large files are not included in this repository. Please download them from the following sources:

1. GloVe Embeddings:
   - Download from: https://nlp.stanford.edu/data/glove.6B.zip
   - Extract and place `glove.6B.200d.txt` in `data/processed/embeddings/`

2. Trained Models:
   - Download from [your preferred file hosting service]
   - Place in `models/` directory
   
## License
MIT License

## Contributors
Jannet Akanksha Ekka - Great Learning

## Contact
jannetekka96@gmail.com