# Car Detection and Classification Project

This project implements deep learning-based car identification to detect and classify cars based on their make, model, and year. The system uses various CNN architectures including both basic implementations and transfer learning approaches, culminating in a Fast R-CNN implementation for object detection.

## Dataset
The dataset comes in the following files:
1. `Car Images.zip` (2 GB) - Contains car images split into training and testing sets
   - Available at: [Google Drive Link](https://drive.google.com/file/d/1PQfQhlsZWp0mMe02aYSGF16UAOVd4USX/view?usp=sharing)
   - Note: Due to large file size (>1.9GB), the image dataset is hosted separately
2. `Annotations.zip` (170 KB) - Contains annotation files with bounding box coordinates and class labels
3. `Car names and make.csv` (5 KB) - Contains the mapping of class names and makes
4. `Problem Statement - CV 2 - Car detection.pdf` (330 KB) - Detailed problem statement and requirements

### Dataset Statistics
Original Dataset:
- Total images: 16,185 across 196 classes
- Training set: 8,144 images
- Testing set: 8,041 images
- Images per class: 24-68 (imbalanced distribution)
- Training/Testing split: ~50-50 per class
- Classes defined at Make, Model, Year level (e.g., "Volkswagen Golf Hatchback 2012")

Working Dataset (Due to Computational Constraints):
- Subset of 16 classes out of 196
- ~650 training images and 642 testing images
- ~29 samples per class after balancing
- Applied balancing techniques to handle class imbalance
- Maintained 50-50 train-test split per class

## Code Structure
The project is implemented across two main notebooks:

### Milestone 1 Notebook
- Initial data processing and EDA
- Basic CNN model implementations
- Initial model training and evaluation

### Milestone 2 Notebook
- Model fine-tuning
- Advanced architectures (ResNet50, MobileNetV2, VGG16)
- Fast R-CNN implementation
- Final model evaluation

## Models Implemented
1. Basic CNN (Baseline)
2. VGG16
3. ResNet50
4. MobileNetV2
5. EfficientNetV2B0
6. Fast R-CNN (with MobileNetV2 and ResNet50 backbones)
7. YOLOv3 (Transfer Learning for Object Detection)

## Results
Best performing models (on 16-class subset):
- For Classification: ResNet50 with fine-tuning achieved 69.20% validation accuracy
- For Object Detection: Fast RCNN with MobileNetV2 backbone achieved 58.59% validation accuracy and 58.05% test accuracy

Note: Due to computational constraints, the models were trained and evaluated on a subset of 16 classes instead of the full 196 classes. While this affected the overall performance metrics, it allowed us to thoroughly experiment with different architectures and approaches. We opted for Fast RCNN as our final object detection model as it provided the best balance of performance and implementation feasibility.

## Setup and Requirements
1. Unzip the data files:
   ```bash
   unzip "Car Images.zip"
   unzip Annotations.zip
   ```

2. Required Python libraries:
   - TensorFlow
   - OpenCV
   - NumPy
   - Pandas
   - Matplotlib
   - Seaborn
   - tqdm

3. Run the notebooks in order:
   - First run Milestone 1 notebook for initial setup and basic models
   - Then run Milestone 2 notebook for advanced implementations

## Project Structure
```
.
├── data/
│   ├── Car Images.zip
│   ├── Annotations.zip
│   └── Car names and make.csv
├── notebooks/
│   ├── load_data.ipynb
│   ├── Milestone_1.ipynb
│   └── Milestone_2.ipynb
├── reports/
│   ├── Problem Statement - CV 2 - Car detection.pdf
│   ├── Interim_Report.pdf
│   └── Final_Report.pdf
├── requirements.txt
├── README.md
└── .gitignore
```

## Model Performance Summary
| Model Version | Parameters | Training Time (min) | Best Train Acc (%) | Best Val Acc (%) |
|--------------|------------|---------------------|-------------------|-----------------|
| Basic CNN    | 532,176    | ~25                | 26.50            | 7.59            |
| VGG16        | 14,987,600 | ~60                | 98.74            | 51.62           |
| ResNet50     | 24,647,056 | ~45                | 99.09            | 62.20           |
| MobileNetV2  | 2,924,112  | ~27                | 99.82            | 59.17           |

## Challenges and Limitations

### Technical Constraints
- Memory constraints with free resources limited our ability to process the full dataset
- Processing speed considerations led to batch processing implementation
- Used only 16 classes out of 196 due to computational limitations

### Dataset Challenges
- Original dataset had class imbalance (24-68 images per class)
- Image quality variations across the dataset
- Storage and processing of 2GB image dataset required careful memory management

### Model Limitations
- Basic CNN showed limited generalization capability
- Transfer learning models performed better but still showed room for improvement
- Implementation complexity increased significantly with advanced architectures like Faster R-CNN

## Future Improvements
- Scale the implementation to handle all 196 classes
- Explore additional data augmentation strategies
- Implement more advanced backbone architectures
- Better handling of class imbalance

## Authors and Acknowledgments

### Authors
- Jannet Akanksha Ekka
- Adari Pooja

### Individual Contributions

#### Jannet Akanksha Ekka
1. Data Processing & Infrastructure
   - Created foundational data preprocessing pipeline
   - Implemented chunking system for efficient handling of large dataset
   - Developed image normalization and encoding procedures
   - Created class mappings and annotation processing
   - Built separate data loading notebook for team use

2. Model Development (Milestone 1)
   - Implemented Basic CNN architecture
   - Developed base MobileNet implementation
   - Created VGG16 base model implementation
   - Collaborated on interim report writing

3. Advanced Object Detection (Milestone 2)
   - Implemented Fast R-CNN architecture
   - Developed Fast R-CNN with multiple backbones (ResNet, MobileNet)
   - Integrated YOLO transfer learning for improved accuracy and speed
   - Contributed to final report

#### Adari Pooja
1. Model Development (Milestone 1)
   - Implemented EfficientNet model
   - Developed ResNet50 transfer learning implementation
   - Led interim report documentation
   - Created final notebook for milestone 1

2. Advanced Implementations (Milestone 2)
   - Fine-tuned base models
   - Worked on Fast R-CNN with MobileNet and VGG backbones
   - Led final report documentation
   - Created final notebook for milestone 2

### References
- 3D Object Representations for Fine-Grained Categorization, Jonathan Krause, Michael Stark, Jia Deng, Li Fei-Fei
- 4th IEEE Workshop on 3D Representation and Recognition, at ICCV 2013 (3dRR-13). Sydney, Australia. Dec. 8, 2013

## License
This project was completed as part of the Computer Vision coursework by Great Learning. All rights reserved.