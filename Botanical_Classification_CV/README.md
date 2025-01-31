# MultiModel Botanical Image Classification

## Project Overview
This project implements multiple machine learning approaches to classify plant species across two datasets: plant seedlings and Oxford flowers. It compares traditional ML, deep learning, and transfer learning techniques.

## Directory Structure
- `models/`: Contains saved models for different approaches (CNN, NN, RF, SVM)
- `data/`: Stores raw and processed datasets
- `notebooks/`: Jupyter notebooks with implementation and analysis

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

## Usage

### Data Preparation
The data is processed in batches and saved as .npy files. The final processed datasets are:
- final_X.npy and final_Y.npy for seedlings
- flowers_X.npy and flowers_Y.npy for flowers

### Running the Models
Open and run the Jupyter notebooks in the notebooks/ directory:
1. Plant Seedlings Classification Final.ipynb

## Model Performance

### Plant Seedlings Dataset
- CNN achieved the best performance with 83.79% accuracy
- Model particularly effective at identifying Loose Silky-bent
- Data augmentation and batch normalization were key to performance

### Oxford Flowers Dataset
- Transfer learning with EfficientNet showed best results
- Basic CNN achieved 50.92% accuracy
- Neural Network performance limited by dataset complexity
