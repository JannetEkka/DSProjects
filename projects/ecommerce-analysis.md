# E-commerce analysis: product scraper, price analysis and dashboard data

**Personal project:** started Jun 12–13, 2024 (scraper, SQL DB, EDA), resumed Jan 14–25, 2025 (restructure, sample data for Tableau, raw data collection, price processing).
**Code:** [github.com/JannetEkka/ecommerce-analysis](https://github.com/JannetEkka/ecommerce-analysis)

> ⚠️ **The portfolio card overstates it.** It says the dashboard turns "raw event and transaction data into merchandising decisions". The repo holds an **Amazon product scraper** (with a rate limiter, data validator and checkpoint combiner), a **price analyser**, generated **sample** products and sales CSVs for a Tableau dashboard, and an empty README. There's no user-event data and no dashboard file in the repo. The card is reworded in this update.

## The 30-second version
A data pipeline for e-commerce price analysis: scrape product listings (headless, 10 s timeout, 3 retries, 2 s between requests, 20 requests/minute, 5 concurrent: `config/scraping_config.yml`), validate and checkpoint the records, process prices, and export to CSV/SQL for a Tableau dashboard; sample data was generated to design the dashboard before real data existed.

## The four FDE angles, honestly
1. **Architecture:** Python modules split by stage (`data_collection`, `data_processing`, `analysis`, `data_utils`), YAML config per concern (Amazon, database, scraping), a SQL database for the scraped data (2024), a CI workflow file. A batch ETL fits here: scraping is slow and rate-limited, so you run it on a schedule and analyse offline.
2. **Data & security:** scraping a marketplace raises **terms-of-service and robots.txt** questions, which I'd raise first with a client. Built-in politeness: rate limiting, delays, retries, no proxies (`proxies.enabled: false`). No personal data collected (product and price data only).
3. **Reliability:** checkpoints (`combine_checkpoints.py`) so a long scrape can resume after a failure without starting over; a `data_validator.py` to reject malformed records; retries with a cap.
4. **Evaluation:** nothing measured (no dashboard KPI, no data-quality report). If asked: scrape success rate, validation reject rate, and freshness of the price data.

## Weak spots to own
- An empty README; a `venv/` folder committed; the overstated card (fixed).

## Sources
Repo tree, `config/scraping_config.yml`, `src/` module names, `project-structure.txt`, git log (Jun 2024, Jan 2025); `_portfolio_src/data.py` card.
