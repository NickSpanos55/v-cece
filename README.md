# V-CECE: Visual Counterfactual Explanations via Conceptual Edits

**by [Nikolaos Spanos](https://github.com/NickSpanos55), [Maria Lymperaiou](https://scholar.google.com/citations?user=YNikyhIAAAAJ&hl=el), [Giorgos Filandrianos](https://scholar.google.com/citations?user=oPIyXYcAAAAJ&hl=en), [Konstantinos Thomas](https://scholar.google.com/citations?hl=en&user=pa0XbysAAAAJ), [Athanasios Voulodimos](https://www.ece.ntua.gr/en/staff/492) and [Giorgos Stamou](https://www.ece.ntua.gr/en/staff/174)**
**by [Nikolaos Spanos](https://github.com/NickSpanos55), [Maria Lymperaiou](https://scholar.google.com/citations?user=YNikyhIAAAAJ&hl=el), [Giorgos Filandrianos](https://geofila.github.io), [Konstantinos Thomas](https://scholar.google.com/citations?hl=en&user=pa0XbysAAAAJ), [Athanasios Voulodimos](https://www.ece.ntua.gr/en/staff/492) and [Giorgos Stamou](https://www.ece.ntua.gr/en/staff/174)**

### This repository contains the code required to run the paper V-CECE: Visual Counterfactual Explanations via Conceptual Edits. It remains currently under construction!

## How to Download the BDD100k Dataset

The BDD100k dataset is a diverse driving dataset for various automotive applications. Here are the steps to download the dataset:

### Step 1: Visit the Official Website
- Go to the [BDD100k official website](https://bdd-data.berkeley.edu/) where the dataset is hosted.

### Step 2: Create an Account
- You will need to create an account or log in if you already have one. Registration may require you to provide some basic information and agree to terms of use concerning the dataset.

### Step 3: Access the Download Section
- Once logged in, navigate to the download section where you can find links to download the dataset.

### Step 4: Choose the Data Format
- BDD100k offers several data formats and annotations. Select the specific format that suits your project needs:
  - Images
  - Videos
  - Labels
  - Drivable Areas
  - Lane Markings

## How to Run the Editor

#### 1. **Python Scripts**:
   - **BDD100k_classifier.py**: A Python script for classifying images in the BDD100k dataset.
   - **claude_predictor.py**: A script designed to predict outcomes using trained models, applicable to both the BDD100k and VG datasets.
   - **places365_classifier.py**: A Python script for classifying images in the Visual Genome dataset using a classifier trained on Places 365 dataset.
#### 2. **Jupyter Notebooks**: 
We provide the code as Jupyter notebooks to make it easy for users to run the code and manually inspect the results of the methods.

For the BDD100K dataset:
   - **V-CECE-Global-Local-BDD100K.ipynb**
   - **V-CECE-Global-bdd100k.ipynb**
   - **V-CECE-Local-BDD100K.ipynb**
  
For the Visual Genome Dataset:
   - **V-CECE-Global-VG.ipynb**
   - **V-CECE-Global-Local-VG.ipynb**
   - **V-CECE-LOCAL-VG.ipynb**
 