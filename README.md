# V-CECE: Visual Counterfactual Explanations via Conceptual Edits

**by [Nikolaos Spanos](https://github.com/NickSpanos55), [Maria Lymperaiou](https://scholar.google.com/citations?user=YNikyhIAAAAJ&hl=el), [Giorgos Filandrianos](https://scholar.google.com/citations?user=oPIyXYcAAAAJ&hl=en), [Konstantinos Thomas](https://scholar.google.com/citations?hl=en&user=pa0XbysAAAAJ), [Athanasios Voulodimos](https://www.ece.ntua.gr/en/staff/492) and [Giorgos Stamou](https://www.ece.ntua.gr/en/staff/174)**


### This repository contains the code required to run the paper V-CECE: Visual Counterfactual Explanations via Conceptual Edits. Please check back for more updates.

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

## Setting up the Editor
1. Our editor runs through a pipeline used in AUTOMATIC1111. Based on your running distribution, you need to follow the instructions
listed in this repository on how to set up the API. https://github.com/AUTOMATIC1111/stable-diffusion-webui

2. On the *webui* folder, you need to swap the line of COMMAND_LINE_ARGS on webui-user.bat with: set COMMANDLINE_ARGS=--share --listen --api. When running the API, this will provide a link in the terminal in the form of: https://410cd4097cee909591.gradio.live 

3. Once you have setup AUTOMATIC1111, either through the browser page or by manually downloading, you will need to install the Replacer extension: https://github.com/light-and-ray/sd-webui-replacer. This extensions allows to accurately handle the editing processes. 

4. For running the editor, three checkpoints are required:

https://huggingface.co/botp/stable-diffusion-v1-5-inpainting (/webui/models/Stable-diffusion)

https://huggingface.co/lkeab/hq-sam/tree/main (sam_hq_vit_h.pth) (/webui/extensions/sd-webui-segment-anything/models/sam)

https://github.com/IDEA-Research/GroundingDINO/releases/tag/v0.1.0-alpha2 (groundingdino_swib_cogcoor.pth) (/webui/extensions/sd-webui-segment-anything/models/grounding_dino)

5. A Python environment needs to be setup with the requirements listed in the folder. Mostly, you will require the WebUIAPI package https://github.com/mix1009/sdwebuiapi. We provide in the folder the modified version in order to handle package requests for the extension.

6. We provide the code for setting up the editor. The editor requires the gradio link mentioned in step 2. An example script of showcasing the results in 
placed in the example_run.py. Paths to images and gradio-links need to be modified accordingly.

## Metrics
1. We provide the parser codes for managing the counterfactual image. Once images are generated they are split into source and counterfactual images
so the metrics can be evaluated.

2. All the metrics we used are listed in https://github.com/guillaumejs2403/ACE. For the S3 it is required
you follow the instructions of setting up the models in the repository. For FID, sFID we follow the instructions in the same repository.
For CMMD we follow the instructions for setup and run in the original repository: https://github.com/sayakpaul/cmmd-pytorch

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
 
