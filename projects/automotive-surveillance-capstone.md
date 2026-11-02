# Automotive Surveillance System (capstone): car make/model/year classification and detection

**PGP in AI/ML capstone (UT Austin McCombs × Great Lakes), Dec 2024 – Jan 2025.** Notebooks and interim/final reports in [`Automotive_Surveillance_System_Capstone/`](../Automotive_Surveillance_System_Capstone/).

> ⚠️ **Correct the headline.** The dataset (Stanford Cars) has **16,185 images across 196 classes**, but because of compute limits **the models were trained on a 16-class subset** (~650 train / 642 test images, ~29 per class after balancing). The 69.2% is on that subset. The portfolio card said "69.2% … across 16,185 images spanning 196 classes"; it's corrected in this update.

## The 30-second version
Classify a car's make, model and year from an image, and detect it with a bounding box. Classification compared a basic CNN, **VGG16, ResNet50, MobileNetV2 and EfficientNetV2B0** with transfer learning; detection used **Fast R-CNN with MobileNetV2 and ResNet50 backbones**. Best classification: **ResNet50 fine-tuned, 69.20% validation accuracy**. Best detection: **Fast R-CNN + MobileNetV2, 58.59% validation / 58.05% test accuracy**.

## The four FDE angles
1. **Architecture:** Colab + TensorFlow/Keras; images chunked for memory ("chunking system for efficient handling of large dataset"); annotations (bounding boxes) from CSVs. Why transfer learning: ~29 images per class can't train a CNN from scratch, so pretrained ImageNet features carry it.
2. **Data & security:** a public academic dataset (images on Google Drive because of size). For a real surveillance use, **privacy is the first question**: number plates and faces are personal data, which means retention limits, purpose limitation, and DPDP Act obligations in India. I'd raise that before any model work.
3. **Reliability:** training-time only. Production questions I'd raise: camera-angle and lighting drift, unseen car models (open-set: the model must say "unknown" rather than force one of 16 labels), and latency at the edge (why MobileNetV2 matters: 2.9M parameters vs ResNet50's 24.6M).
4. **Evaluation:** overfitting was the main finding. Training accuracy ~99% for VGG16/ResNet50/MobileNetV2 vs validation 52–62% in the comparison table (VGG16 51.62%, ResNet50 62.20%, MobileNetV2 59.17%), improved to 69.2% with fine-tuning. The honest result: too little data per class. More data or stronger augmentation would matter more than a bigger backbone.

## Sources
`Automotive_Surveillance_System_Capstone/README.md` (dataset statistics, working subset, model table, results), the notebooks and the two reports in `reports/`.
