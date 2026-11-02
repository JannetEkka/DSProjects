# Applied Statistics and Hypothesis Testing

**PGP in AI/ML (UT Austin McCombs), May – Jun 2024.** Notebook and data in [`Applied_Statistics_Project/`](../Applied_Statistics_Project/).

> ⚠️ **Correct the card.** It said "manufacturing quality control **identifying** a 5% defect rate". The 5% defect rate is **given** in the problem; the notebook computes binomial probabilities from it (e.g. P(no defective items) = 59.87%, P(≤2 defective) = 98.85%). Fixed in this update.

## The 30-second version
Statistical foundations on three datasets:
- **Probability models:** binomial quality control at a 5% defect rate; Poisson weekly car sales (P(selling some cars in a week) = 95.02%; P(2 ≤ sales < 5) = 61.61%); order-recognition probabilities (P(all three recognised) = 65.4%).
- **Hypothesis testing:** car-purchase behaviour and a basketball-team performance dataset (`DS - Part2 - Basketball.csv`) and a company dataset (`CompanyX_EU.csv`), with tests such as one reported **p-value of 0.256** (fail to reject the null at 5%).

## The four FDE angles
1. **Architecture:** SciPy and pandas in a notebook. No system to architect. The value is knowing which test fits which question.
2. **Data & security:** course datasets.
3. **Reliability:** state assumptions before using a test (independence for binomial, constant rate for Poisson, normality or a non-parametric alternative for t-tests).
4. **Evaluation:** this is the root of every evaluation answer in the other write-ups. A p-value of 0.256 means "no evidence of a difference", not "no difference", and that distinction is what stopped SmartDesk from shipping a reranker.

## Sources
Notebook outputs (probabilities, p-value 0.2557); `Applied_Statistics_Project/README.md`; data files in the folder.
