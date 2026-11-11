"""Load the 2024 project's data and rebuild its test split exactly.

The notebook (notebooks/NLPProject5.ipynb, the cell that prepares the split)
did this, on the 349 rows in file order:

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

A stratified split depends only on the labels, the row order and the seed, so
splitting the row numbers the same way gives the same test rows.
"""
from __future__ import annotations

import os

import pandas as pd
from sklearn.model_selection import train_test_split

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "..", "data", "raw", "stock_news.csv")

# Weighted F1 on the 2024 test split, from the notebook (see ../README.md).
BASELINE_2024 = {
    "Selected model (2024)": 0.366,
    "XGBoost": 0.378,
    "Gradient Boosting": 0.348,
    "Random Forest": 0.296,
}


def load() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    df["News"] = df["News"].astype(str).str.strip()
    df["id"] = [f"H{i + 1:03d}" for i in range(len(df))]
    # Same weekly grouping as the notebook: pd.Grouper(key='Date', freq='W'),
    # which labels each week by the Sunday that ends it.
    df["week"] = (df["Date"] + pd.offsets.Week(weekday=6, n=0)).dt.strftime("%Y-%m-%d")
    return df


def test_ids_2024(df: pd.DataFrame) -> list[str]:
    rows = list(range(len(df)))
    y = df["Label"]
    _, temp_rows, _, y_temp = train_test_split(
        rows, y, test_size=0.3, random_state=42, stratify=y)
    _, test_rows, _, _ = train_test_split(
        temp_rows, y_temp, test_size=0.5, random_state=42, stratify=y_temp)
    return [df["id"].iloc[i] for i in test_rows]


def weeks(df: pd.DataFrame) -> list[dict]:
    """One entry per week: its headlines and its daily price rows."""
    out = []
    for wk, g in df.groupby("week", sort=True):
        days = (g.drop_duplicates("Date").sort_values("Date")
                [["Date", "Open", "High", "Low", "Close"]])
        out.append({
            "week": wk,
            "headlines": [{"id": r.id, "date": r.Date.strftime("%Y-%m-%d"), "text": r.News}
                          for r in g.itertuples()],
            "prices": [{"date": r.Date.strftime("%Y-%m-%d"), "open": float(r.Open),
                        "high": float(r.High), "low": float(r.Low), "close": float(r.Close)}
                       for r in days.itertuples()],
        })
    return out


if __name__ == "__main__":
    d = load()
    t = test_ids_2024(d)
    w = weeks(d)
    print(len(d), "rows;", len(t), "test rows;", len(w), "weeks")
    print("test label counts:", d[d.id.isin(t)].Label.value_counts().to_dict())
