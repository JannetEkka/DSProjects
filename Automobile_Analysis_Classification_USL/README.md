# Automobile Analysis and Classification: A Dual Study using K-Means Clustering and PCA-Enhanced SVM

## Project Overview
This project consists of two comprehensive analyses in the automobile domain:
1. Vehicle Segmentation using K-Means Clustering
2. Vehicle Classification using PCA-Enhanced Support Vector Machines (SVM)

## Part A: Vehicle Segmentation Analysis

### Dataset Description
- **Source**: Car attributes and specifications dataset
- **Features**: 
  - Discrete: cylinders, model year, origin
  - Continuous: MPG, displacement, horsepower, weight, acceleration
  - Identifier: car name

### Objectives
- Segment vehicles into distinct categories using K-means clustering
- Analyze relationships between various vehicle attributes
- Identify optimal number of vehicle segments

### Methodology
1. Data Preprocessing:
   - Missing value treatment
   - Duplicate handling
   - Feature standardization
   
2. Exploratory Data Analysis:
   - Multivariate analysis using pairplots
   - Feature relationship visualization
   - Distribution analysis

3. K-Means Clustering:
   - Implementation of clustering for k=2 to k=10
   - Elbow method for optimal cluster determination
   - Cluster visualization and interpretation

## Part B: Vehicle Silhouette Classification

### Dataset Description
- **Source**: Vehicle silhouette measurements
- **Features**: Geometric features extracted from vehicle silhouettes
- **Classes**: Multiple vehicle types (bus, van, cars)

### Objectives
- Implement dimensionality reduction using PCA
- Build and optimize an SVM classifier
- Compare model performance with and without PCA

### Methodology
1. Data Preprocessing:
   - Data cleaning and standardization
   - Train-test splitting
   - Missing value treatment

2. PCA Implementation:
   - Analysis with 10 principal components
   - Variance threshold analysis (90%)
   - Feature dimensionality optimization

3. Model Development:
   - Baseline SVM implementation
   - PCA-enhanced SVM modeling
   - Hyperparameter tuning

## Technologies Used
- Python
- Key Libraries:
  - pandas
  - numpy
  - scikit-learn
  - matplotlib
  - seaborn

## Key Findings
1. Vehicle Segmentation:
   - Optimal cluster number determined through elbow method
   - Clear segmentation based on vehicle characteristics
   - Strong correlation between weight, displacement, and fuel efficiency

2. Classification Analysis:
   - PCA significantly reduced feature dimensionality while maintaining information
   - Enhanced model performance through hyperparameter tuning
   - Successful classification of vehicle types based on silhouette features

## Installation and Usage
```bash
# Clone the repository
git clone [repository-url]

# Install required packages
pip install -r requirements.txt

# Run the notebooks
jupyter notebook
```

## Project Structure
```
.
├── data/
│   ├── Car-Attributes.json
│   ├── Car name.csv
│   └── vehicle.csv
├── Unsupervised_Learning_Project_Jannet.ipynb
├── README.md
└── requirements.txt
```

## Future Work
- Implementation of additional clustering algorithms
- Deep learning approaches for classification
- Integration of additional vehicle attributes
- Real-time prediction system development

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Dataset providers
- Project mentors and reviewers
- Great Learning Academy