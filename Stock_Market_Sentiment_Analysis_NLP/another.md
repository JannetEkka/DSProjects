# Stock Market Sentiment Analysis and Automated News Summarization

## Project Overview
This project implements an AI-driven sentiment analysis system that processes financial news articles to gauge market sentiment and generate automated weekly summaries to enhance stock price predictions and optimize investment strategies. The system combines natural language processing (NLP), machine learning, and large language models to provide actionable insights for financial analysts.

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
- Sentiment Analysis of financial news articles
- Automated weekly news summarization using Mistral-7B LLM
- Stock price movement correlation analysis
- Trading volume pattern analysis
- Data visualization and statistical analysis
- Class-balanced machine learning models

## License
MIT License

## Contact
jannetekka96@gmail.com