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