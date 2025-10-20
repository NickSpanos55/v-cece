import webuiapi
import matplotlib.pyplot as plt
from PIL import Image

api = webuiapi.WebUIApi()

# create API client with custom host, port
api = webuiapi.WebUIApi(host=<GRADIO-PART>, port=7860,baseurl=<GRADIO-LINK>)

image_path = <PATH-TO-IMAGE>

# Load the image using PIL
to_edit = Image.open(image_path)

result1 = api.replacer(input_image=to_edit,
                    detection_prompt= "",
                    positive_prompt= '',
                    negative_prompt= "",
                    extra_include= ["mask"] #Returns the mask of the object
                    )

image1 = result1.image #Edited Image
image2 = result1.extra_images[0] #Mask of the original object

fig, axes = plt.subplots(1, 3, figsize=(10, 5))  # 1 row, 2 columns

axes[0].imshow(bed)
axes[0].axis('off')  # Hide axis
axes[0].set_title('Original Image')

axes[1].imshow(image1)
axes[1].axis('off')  # Hide axis
axes[1].set_title('Altered Image')

axes[2].imshow(image2)
axes[2].axis('off')  # Hide axis
axes[2].set_title('Mask')

plt.tight_layout()
plt.show()