# Stock Market Sentiment Analysis: financial-news NLP with Mistral-7B summaries

**PGP in AI/ML (UT Austin McCombs), Nov – Dec 2024.** Notebook and data in [`Stock_Market_Sentiment_Analysis_NLP/`](../Stock_Market_Sentiment_Analysis_NLP/).

## The 30-second version
Classify the sentiment of financial news (to relate it to stock moves) and write **weekly market summaries with an LLM**. Embeddings compared: **Word2Vec, GloVe (100d/200d), SBERT**. Classifiers: Random Forest, Gradient Boosting, XGBoost, with **SMOTE and SMOTETomek** for class imbalance. Weekly summaries come from **Mistral-7B-Instruct v0.1 (GGUF, Q4_K_M) run locally through llama.cpp** (`Llama(...)`, `n_ctx=512`).

**Results, honestly:** validation F1 around 0.46–0.52, but **test F1 0.30–0.38** (RF 0.296, GB 0.348, XGBoost 0.378; the selected model 0.366). The gap between validation and test says the validation set flattered the models. With a small, imbalanced dataset, sentiment from embeddings + trees is weak. (The interview-prep inventory once said "Mistral-7B embeddings"; it's summarisation, not embeddings.)

## The four FDE angles
1. **Architecture:** a notebook pipeline: clean → embed → resample → classify → aggregate by week → LLM summary. **Why a local quantised LLM:** Q4_K_M runs on a CPU/T4 notebook without an API key or per-token cost. The 512-token context limits how much news fits in one summary, so weekly batches.
2. **Data & security:** public news headlines. For a bank deployment, the summaries would be advisory and the source articles cited (the same rule as my later projects: every claim must point to its source).
3. **Reliability:** LLM summaries can invent facts. There's no grounding check here. Today I'd verify every company name and number in a summary against the week's articles before showing it, which is exactly what Klarbrief and Recourse do.
4. **Evaluation:** F1 (not accuracy) because of the imbalance, which is right. What's missing is a market-relevance test: does weekly sentiment predict next-week returns better than a "same as last week" baseline? That's the question SMT later answered for its own sentiment input (no skill at 24h).

## Sources
`Stock_Market_Sentiment_Analysis_NLP/README.md` (embeddings, imbalance handling, F1 table, Mistral); notebook `NLPProject5.ipynb` (model file `mistral-7b-instruct-v0.1.Q4_K_M.gguf`, `Llama(… n_ctx=512 …)`).
