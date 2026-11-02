# Signal Quality and SVHN Digit Classification (neural networks)

**PGP in AI/ML (UT Austin McCombs), Aug – Sep 2024.** Notebook in [`Signal_Classification_Digit_Recognition_NNDL/`](../Signal_Classification_Digit_Recognition_NNDL/).

> ⚠️ **Correct the card.** It said "90% accuracy on signal-quality prediction and 85% on SVHN". The notebook's outputs show **signal quality: best test accuracy 64.95%** (variants ranged 58.1%–64.95%) and **SVHN: 87.09% test accuracy** (18,000 test images). Fixed in this update.

## The 30-second version
- **Part A, signal quality:** a telecom manufacturer wants to predict signal strength from 11 signal parameters (1,599 records). A dense neural network with batch normalisation and dropout, tuned across several variants. **Best ~65% test accuracy**: an ordinal multi-class target with few examples of the extreme classes is hard, and a tree ensemble would be the baseline to try.
- **Part B, SVHN:** digits from Google Street View house numbers (32×32 grayscale). A deeper network with batch normalisation, dropout and learning-rate reduction. Accuracy climbed from ~53% (early variants) to **87.1%**, with per-digit F1 around 0.86–0.90.

## The four FDE angles
1. **Architecture:** Keras dense networks; `ReduceLROnPlateau`-style learning-rate decay (the logs show the LR stepping down to 1.5625e-05). Why a dense net on SVHN instead of a CNN: that was the course module (NN fundamentals). A CNN is the right tool and would beat 87%.
2. **Data & security:** public datasets; nothing sensitive.
3. **Reliability:** regularisation (dropout, batch norm) against overfitting; validation tracked each epoch (val accuracy ~0.87 tracking train ~0.84, so no overfit on SVHN).
4. **Evaluation:** a held-out test set, a classification report per digit. For signal quality I'd add a confusion matrix and a "within one class" accuracy, since an ordinal target makes near-misses less costly.

## Sources
Notebook `INN-Project.ipynb` outputs (cells 35–47: signal test accuracies; cells 74–82: SVHN test accuracies and the per-class report); `README.md` (dataset sizes).
