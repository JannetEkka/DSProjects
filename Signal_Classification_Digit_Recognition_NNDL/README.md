# Signal Classifier Project

This project implements neural network solutions for two distinct machine learning problems in the domains of telecommunications and computer vision.

## Table of Contents
- [Project Overview](#project-overview)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Part A: Signal Quality Classification](#part-a-signal-quality-classification)
- [Part B: SVHN Digit Classification](#part-b-svhn-digit-classification)
- [Usage](#usage)
- [Results and Findings](#results-and-findings)
- [Dependencies](#dependencies)
- [License](#license)

## Project Overview

### Part A: Signal Quality Classification
A telecommunications equipment manufacturer needs to predict signal quality based on various signal parameters. This part implements a neural network classifier to determine signal strength using multiple input parameters.

**Dataset Details:**
- Source: Signal.csv
- Features: 11 signal parameters
- Target: Signal strength (categorical)
- Size: 1,599 records

### Part B: SVHN Digit Classification
Implementation of a digit classifier for the Street View House Numbers (SVHN) dataset, which contains digits from Google Street View images.

**Dataset Details:**
- Source: Autonomous_Vehicles_SVHN_single_grey1.h5
- Type: Grayscale images (32x32x1)
- Task: Single digit classification
- Complexity: More challenging than MNIST due to real-world conditions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/signal_classifier.git
cd signal_classifier
```

2. Create and activate a virtual environment:
```bash
# On Unix/macOS
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Data Setup:
- Place `Signal.csv` in the `data/` directory
- For Part B's SVHN dataset:
  - Download `Autonomous_Vehicles_SVHN_single_grey1.h5` from [Google Drive](https://drive.google.com/file/d/1gy5xaVH83ALiKMK55ObP87XpkkXKzQQA/view?usp=sharing)
  - Place the downloaded file in a location accessible to your notebooks
  - Update the file path in the SVHN classifier notebook accordingly:
    ```python
    file_path = "path/to/Autonomous_Vehicles_SVHN_single_grey1.h5"
    ```
  
Note: The SVHN dataset file is approximately 468MB. Make sure you have sufficient storage space before downloading.

## Project Structure
```
signal_classifier/
├── data/
│   ├── Autonomous_Vehicles_SVHN_single_grey1.h5    # Link to GDrive
│   └── Signal.csv          # Signal quality dataset
├── notebooks/
│   ├── INN-Project.ipynb
├── README.md              # This file
├── requirements.txt       # Project dependencies
├── .gitignore         # Git ignore rules
└── LICENSE.md            # MIT License
```

## Part A: Signal Quality Classification

### Implementation Details
- Data preprocessing:
  - Outlier detection and handling using IQR method
  - Feature normalization using StandardScaler
  - Label encoding for categorical target variable
- Neural Network Architecture:
  - Multiple dense layers with batch normalization
  - Dropout layers for regularization
  - ReLU and LeakyReLU activation functions
  - Softmax output layer for classification

### Key Findings
- Model achieves stable performance with minimal overfitting
- Uses early stopping and learning rate reduction for optimal training
- Successfully handles multi-class classification of signal strength

## Part B: SVHN Digit Classification

### Implementation Details
- Data preprocessing:
  - Image normalization (0-1 scaling)
  - Grayscale image handling
  - One-hot encoding of labels
- Neural Network Architecture:
  - Dense layers for feature extraction
  - Batch normalization for training stability
  - Dropout for regularization
  - Softmax output for 10-class digit classification

### Key Findings
- Effectively handles real-world digit recognition challenges
- Demonstrates robustness against varying image conditions
- Achieves good accuracy despite presence of distractors in images

## Usage

1. Start Jupyter Notebook:
```bash
jupyter notebook
```

2. Navigate to `notebooks/` directory and open notebook

3. Execute cells sequentially to:
   - Load and preprocess data
   - Train models
   - Visualize results

## Results and Findings

### Signal Quality Classification
- Successfully classified signal strength into multiple categories
- Model demonstrates good generalization capabilities
- Effective handling of various signal parameters

### SVHN Classification
- Robust digit recognition in real-world conditions
- Handles variations in lighting, orientation, and style
- Achieves competitive accuracy on street view numbers

## Dependencies

Major dependencies include:
- Python 3.8+
- TensorFlow 2.13.0
- NumPy 1.24.3
- Pandas 2.0.3
- Scikit-learn 1.3.0
- Matplotlib 3.7.2
- Seaborn 0.12.2
- h5py 3.9.0

See `requirements.txt` for complete list of dependencies.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

SVHN Dataset:
- Yuval Netzer, Tao Wang, Adam Coates, Alessandro Bissacco, Bo Wu, Andrew Y. Ng
- "Reading Digits in Natural Images with Unsupervised Feature Learning"
- NIPS Workshop on Deep Learning and Unsupervised Feature Learning 2011