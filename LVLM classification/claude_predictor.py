from tqdm import tqdm
from collections import defaultdict
from multi_chat import *
import boto3
import os

bedrock_runtime_client = boto3.client(
    'bedrock-runtime'
)

#model_id = "anthropic.claude-3-haiku-20240307-v1:0"
model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"


# the largest digit image is the image produced in the final step, therefore the counterfactual for which the classifier 
# under consideration changes classes
def keep_largest_digit_image(folder_path):
    max_digit = -1
    largest_digit_file = None

    # Updated regex to capture digits at the end of filenames like 'step_x.jpg'
    pattern = re.compile(r'step_(\d+)\.jpg$')

    # Iterate over all files in the directory
    for filename in os.listdir(folder_path):
        match = pattern.search(filename)
        if match:
            # Convert the captured digit to an integer
            digit = int(match.group(1))
            # Check if this is the largest digit seen so far
            if digit > max_digit:
                max_digit = digit
                largest_digit_file = filename

    # If found, return the filename with the largest digit
    if largest_digit_file:
        #print(f"Largest digit image: {largest_digit_file}")
        return largest_digit_file
    else:
        #print("No matching files found.")
        return None

# predict image class using Claude as classifier
def predict_and_explain(image_names, counterfactual_names, classification_prompt, explain_prompt, prompt_analyze, text_prompt, analyze=False, explain=True):
    
    source_classes = defaultdict(list)
    counter_classes = defaultdict(list)
    source_explanations = defaultdict(list)
    counter_explanations = defaultdict(list)

    for name, counterfactual in tqdm(zip(image_names, counterfactual_names)):    
        if counterfactual:         # we exclude cases where counterfactual images have not been produced
            # source images
            chat = Chat(model_id, bedrock_runtime_client) # create a chat like openning a new chat in 
            if analyze:
                chat.add_user_message_image(prompt_analyze, load_image(name)) # analyze image
                chat.generate()
                chat.add_user_message(text_prompt)                            # answer about the analyzed image
            else:
                chat.add_user_message_image(classification_prompt, load_image(name)) # add a user message with an image and a text prompt
            answer_source = chat.generate().lower()
            source_classes[name]=answer_source
            chat.add_user_message(explain_prompt)
            explanation_source = chat.generate()
            source_explanations[name]=explanation_source
            
            if analyze:
                chat.add_user_message_image(prompt_analyze, load_image(counterfactual)) # analyze image
                chat.generate()
                chat.add_user_message(text_prompt) 
            else:
                chat.add_user_message_image(classification_prompt, load_image(counterfactual))
            answer_counter = chat.generate().lower()
            counter_classes[name]=answer_counter      # if None, it means that there is a bug in defining edit order
            chat.add_user_message(explain_prompt)
            explanation_counter = chat.generate()     # if None, same as above, there is no target image
            counter_explanations[name]=explanation_counter
        else:
            pass
    return source_classes, source_explanations, counter_classes, counter_explanations
    
def all_images(image_directory, display=False):
    images = []
    image_names = []
    counterfactuals = []
    
    for filename in os.listdir(image_directory):
        filename=image_directory+filename+'/'
        largest_digit_file = keep_largest_digit_image(filename)
        if largest_digit_file:     # if not None, append the whole image path
            counterfactuals.append(filename+largest_digit_file)
        else:                      # if None, just append None
            counterfactuals.append(largest_digit_file)
        for im in os.listdir(filename):
            if im.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):    # is image file
                if im.startswith(('source')):
                    image_path = os.path.join(filename, im)
                    image_names.append(image_path)
                
        if display:
            for img in images:
                plt.imshow(img)
                plt.axis('off')  # Hide axis
                plt.show()  # Display the image
    return image_names, counterfactuals


def source_images(image_directory, display=False):
    images = []
    image_names = []
    
    for filename in os.listdir(image_directory):
        filename=image_directory+filename+'/'
        for im in os.listdir(filename):
            if im.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):    # is image file
                if im.startswith(('source')):
                    image_path = os.path.join(filename, im)
                    image_names.append(image_path)
                
        if display:
            for img in images:
                plt.imshow(img)
                plt.axis('off')  # Hide axis
                plt.show()  # Display the image
    return image_names

def generate_prompt(categories):
    # Join the categories into a readable list format
    categories_str = ", ".join(categories)
    return categories_str

def predict_classes_claude(image_names, source_classes, classification_prompt, prompt_analyze, text_prompt, analyze=False):
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    for name in tqdm(image_names):    
        chat = Chat(model_id, bedrock_runtime_client) # create a chat like openning a new chat in 
        if analyze:
            try:
                chat.add_user_message_image(prompt_analyze, load_image(name)) # analyze image
                chat.generate()
                chat.add_user_message(text_prompt)                            # answer about the analyzed image
            except:
                print("ValidationException occured in ", name)
        else:
            chat.add_user_message_image(classification_prompt, load_image(name)) # add a user message with an image and a text prompt
        try:
            answer_source = chat.generate().lower()
            source_classes[name].append(answer_source)
        except:
            print("ValidationException occured in ", name)  
    return source_classes

def construct_contrastive_explanations(source_classes, counter_classes, counterfactual_images):
    contrastive_explanations = defaultdict(list)

    for gt, cc, counter_image in zip(source_classes, counter_classes, counterfactual_images):
        counter_class = counter_classes[cc]
        ground_truth_class = source_classes[gt]
        chat = Chat(model_id, bedrock_runtime_client) 
        if counter_class and (ground_truth_class != counter_class):
            contrastive_prompt= f"""
                You previously classified this instance in the class {counter_class}.
                Why did you select the class {counter_class} instead of the class {ground_truth_class}?
                Stay confident on your prediction in {counter_class} and do not change it, just provide me a constrastive explanation.
                I only need a few sentences explaining me your previous decision.
                """
            chat.add_user_message_image(contrastive_prompt, load_image(counter_image))
            why = chat.generate()
            #print(f"""Why {counter_class} and not {ground_truth_class}?""")

            concept_prompt = f"""
                Based on the previous explanation, give me the concepts that differentiate the {counter_class} from the {ground_truth_class}.
                Focus on specific objects and exclude general stuff. These objects should returned in a Python list.
                Give me this list and nothing else.
                """
            chat.add_user_message(concept_prompt)        
            concepts = chat.generate()    # the counterfactual has these concepts, while the GT doe not
            contrastive_explanations[cc] = concepts
    return contrastive_explanations
