# Automobile Analysis and Classification: K-Means segmentation and PCA-enhanced SVM

**PGP in AI/ML (UT Austin McCombs), Apr – May 2024.** Notebook in [`Automobile_Analysis_Classification_USL/`](../Automobile_Analysis_Classification_USL/).

> ⚠️ **Correct the card.** It said "across 102 features". The data is **398 cars × 8 attributes** (mpg, cylinders, displacement, horsepower, weight, acceleration, year, origin) for the clustering, and **846 vehicle silhouettes × 18 geometric features** for the SVM. Fixed in this update.

## The 30-second version
- **Part 1, segmentation:** K-Means for k = 2–10, choosing k by the elbow method and silhouette (**silhouette 0.586 at k = 3**, 0.580 at k = 4), then interpreting the segments (e.g. economy vs heavy, powerful cars).
- **Part 2, classification:** classify vehicles (car / bus / van) from silhouette features with an SVM, with and without **PCA (10 components, ~90% variance threshold)**. Test accuracy across the variants: 0.96 for the best, and 0.81 / 0.73 for others. PCA trades a little accuracy for a much smaller feature space.

## The four FDE angles
1. **Architecture:** scikit-learn; standardise → PCA → SVM. Why PCA before SVM: correlated geometric features (compactness, circularity, elongation) carry redundant information, and fewer dimensions train faster and generalise better.
2. **Data & security:** public datasets; nothing sensitive.
3. **Reliability:** scaling must be fitted on train only and saved with the model; the cluster labels aren't stable across reruns (fix `random_state`) or across new data (refit changes segment meaning).
4. **Evaluation:** silhouette for the clusters, accuracy and classification report for the SVM. I'd add per-class recall (vans are the minority).

## Sources
Notebook outputs (silhouette scores; classification reports, support 676 train / 170 test); `data/` files (`vehicle.csv` 846 rows × 19 columns; `Car-Attributes.json` 398 records × 8 fields); `README.md`.
