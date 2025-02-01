# MultiModel Botanical Image Classification

## Project Overview
This project implements multiple machine learning approaches to classify plant species across two datasets: plant seedlings and Oxford flowers. It compares traditional ML, deep learning, and transfer learning techniques.

## Project Structure
```
MultiModel-Botanical-Classification/
├── data/
│   ├── raw/
│   │   ├── plant-seedlings-classification.zip  # Link to GDrive
│   │   └── Prediction.jpg
│   └── processed/
│       ├── flowers_X.npy  # Link to GDrive
│       └── flowers_Y.npy
├── notebooks/
│   └── Plant Seedlings Classification Final.ipynb    # Link to GDrive
├── .gitignore
├── Requirements.txt
└── README.md
```

## Required Data Files
Due to size limitations, some files are hosted on Google Drive:
1. Plant Seedlings Dataset:
   - plant-seedlings-classification.zip: [GDrive](https://drive.google.com/file/d/1dSPHaArHtB3umPxFrvxxWlxwjZTz1M3a/view?usp=sharing)
2. Processed Data:
   - flowers_X.npy: [GDrive](https://drive.google.com/file/d/1--0jwzKVV8vp7g7aZB2LTJe-MuhrkI5j/view?usp=sharing)
   - flowers_Y.npy: [Included in repo as it's small]
3. Test Image:
   - Prediction.jpg: [Included in repo]

## Data Processing
The project processes data in batches to handle memory efficiently:
- Images are split into 17 batches
- Each batch has corresponding image and label numpy files
- Final processed data is stored in final_X.npy and final_Y.npy

## Models Implemented
1. Plant Seedlings Classification:
   - CNN (83.79% accuracy)
   - Random Forest (48.55% accuracy)
   - SVM (56.99% accuracy)

2. Oxford Flowers Classification:
   - Base CNN (50.92% accuracy)
   - Neural Network (~24% accuracy)
   - Transfer Learning with EfficientNet

## Setup Instructions
1. Clone this repository
2. Download the required data files from Google Drive links
3. Place the downloaded files in their respective directories as shown in project structure
4. Install required packages:
   ```bash
   pip install -r Requirements.txt
   ```
5. Open and run Plant Seedlings Classification Final.ipynb in Google Colab

## Model Performance

### Plant Seedlings Dataset
- CNN achieved the best performance with 83.79% accuracy
- Model particularly effective at identifying Loose Silky-bent
- Data augmentation and batch normalization were key to performance

### Oxford Flowers Dataset
- Transfer learning with EfficientNet showed best results
- Basic CNN achieved 50.92% accuracy
- Neural Network performance limited by dataset complexity

## Notes
- The Oxford Flowers dataset is automatically downloaded using tensorflow_datasets
- Most model files and intermediate data are generated during notebook execution
- Batch processing is used to handle memory efficiently