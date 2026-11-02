# MultiModel Botanical Classification: plant seedlings and Oxford flowers

**PGP in AI/ML (UT Austin McCombs), Jun – Jul 2024.** Notebook in [`MultiModel_Botanical_Classification_CV/`](../MultiModel_Botanical_Classification_CV/).

## The 30-second version
Classify plant species from images and compare traditional ML, deep learning and transfer learning. **Plant seedlings (4,750 images, 12 species; 3,800 train / 950 test at 224×224): a CNN reached 83.79% test accuracy**, against Random Forest 48.55% and SVM 56.99% on the same task. On **Oxford Flowers** the base CNN reached 50.92% and a deeper network ~24%.

## What the notebook shows that the card didn't
- **The transfer-learning runs on the flowers set failed:** loss went to `nan` and accuracy sat at ~4.5% (chance level), for both the transfer model and the fine-tuned model. A later cell also hit a Keras deserialisation error (`batch_shape`) loading a saved model. So "transfer learning" on this project isn't a success story. The honest takeaway: NaN loss usually means a learning rate too high or unnormalised inputs. I'd check input scaling and lower the LR, and watch for NaN early with a callback.

## The four FDE angles
1. **Architecture:** Colab, Keras CNN vs scikit-learn RF/SVM on flattened or engineered features. The CNN wins because spatial features matter for leaves; RF/SVM on raw pixels can't use them.
2. **Data & security:** public datasets; no personal data. A real agritech deployment means farm imagery (location metadata can be sensitive) and on-device inference in the field.
3. **Reliability:** the NaN failure is the reliability lesson. In production I'd add a training guard (terminate on NaN) and model-loading tests across library versions (the `batch_shape` error is a Keras version mismatch).
4. **Evaluation:** test accuracy on a held-out 20%. For 12 imbalanced species I'd report per-class recall too (weeds vs crop seedlings is the costly confusion).

## Sources
`MultiModel_Botanical_Classification_CV/README.md`; notebook outputs (dataset size 4,750; train/test shapes; "Test accuracy: 0.8379"; flowers model losses).
