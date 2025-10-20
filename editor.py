import webuiapi
from PIL import Image
import matplotlib.pyplot as plt

class Editor():

    def __init__(self, gradio_link):
        self.gradio_link = gradio_link  
        self.api = webuiapi.WebUIApi(host=self.gradio_link , port=7860, baseurl=f"{self.gradio_link}/replacer")
        # create API client with custom host, port
        # api = webuiapi.WebUIApi()

    def replacer(self, image_path, detection_prompt, positive_prompt, negative_prompt = "cartoon, unrealistic proportions, blurry edges, low detail, overexposed lighting, distorted shapes", extra_include= ["mask"]):

        # load image 
        img = Image.open(image_path)

        result = self.api.replacer(input_image=img,
                                    detection_prompt= detection_prompt,
                                    positive_prompt= positive_prompt,
                                    negative_prompt= negative_prompt,
                                    extra_include= extra_include,
                                    mask_blur= 10,
                                    cfg_scale= 10,
                                    denoise= 1,
                                    steps= 40,
                                    use_hires_fix= True,
                                    
                    )

        return result.image, result.extra_images[0]
