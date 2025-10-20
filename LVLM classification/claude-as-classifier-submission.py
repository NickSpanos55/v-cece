# We use CLAUDE as the classifier to be explained by V-CECE

import os
from PIL import Image
import matplotlib.pyplot as plt
from tqdm import tqdm
import re
import pickle
from claude_predictor import *
from multi_chat import Chat
import boto3
from collections import defaultdict, Counter


# ### Visual Genome categories

with open("processed_places_categories.pickle", "rb") as f:
    processed_categories = pickle.load(f)

# # Classification

def open_image_from_path(image_path, filename):
    try:                            # Open the image and append to the list
        with Image.open(image_path) as img:
            images.append(img.copy())  # Use .copy() to avoid closing the image
            image_names.append(image_path)
    except Exception as e:
        print(f"Error loading image {filename}: {e}")

# ## Load images

claude_directory = 'imgs/random/claude/'  # CLAUDE decides the order of edits
image_names_claude = source_images(claude_directory)

# ## Prompts

str_categories = generate_prompt(processed_categories)

classification_prompt = f"""
Classify each image in their appropriate class according to the scene they depict. 
Valid classes are {str_categories} and only these, so you need to classify the images in one of these classes.
Pay attention to the semantics that define each class.
Return me only the label of the scene depicted and nothing else.
"""

# Attempt the analyze-then-predict prompting for "step by step" reasoning
prompt_analyze = """
Please analyze the images in detail and answer the following question with reason based on these images. 
"""

text_prompt = f"""
Based on your analysis above, classify each image in their appropriate class according to the scene they depict. 
Valid classes are {str_categories}.
Pay attention to the semantics that define each class.
Return me only the label of the scene depicted and nothing else.
"""

# ## Predict
source_classes = defaultdict(list)

for ii in range(7):
    source_classes = predict_classes_claude(image_names_claude, source_classes, classification_prompt, prompt_analyze, text_prompt, analyze=False)
    
# clean responses, especially '\n' character, if present
source_classes_clean = defaultdict(list, {k: list(map(lambda x: x.replace('\n', ''), v)) for k, v in source_classes.items()})

# filter out items that do not belong to PLACES classes
source_classes_filtered = {key: list(filter(lambda item: item in processed_categories, items)) for key, items in source_classes_clean.items()}

for key in source_classes_filtered:
    if not source_classes_filtered[key]:  # Checks if the list is empty
        source_classes_filtered[key] = source_classes_clean[key]

# substitute each value list with the most frequent element from the lists per key
source_classes = defaultdict(list, {k: (lambda v: Counter(v).most_common(1)[0][0])(v) for k, v in source_classes_filtered.items()})

for class_ in source_classes:
    print(source_classes[class_])


with open('claude-sonnet-as-classifier_source_class_claude.pickle', 'wb') as f:
    pickle.dump(source_classes, f)


# ## Analyze-then-predict
# 
# This prompt seems more stable in comparison to the non-analyze one
source_classes_analyze = defaultdict(list)

for ii in range(7):
    source_classes_analyze = predict_classes_claude(image_names_claude, source_classes_analyze, classification_prompt, 
                                                 prompt_analyze, text_prompt, analyze=True)

source_classes_analyze_clean = defaultdict(list, {k: list(map(lambda x: x.replace('\n', ''), v)) for k, v in source_classes_analyze.items()})

# filter out items that do not belong to PLACES classes
source_classes_analyze_filtered = {key: list(filter(lambda item: item in processed_categories, items)) for key, items in source_classes_analyze_clean.items()}


for key in source_classes_analyze_filtered:
    if not source_classes_analyze_filtered[key]:  # Checks if the list is empty
        source_classes_analyze_filtered[key] = source_classes_analyze_clean[key]


# substitute each value list with the most frequent element from the lists per key
source_classes_analyze = defaultdict(list, {k: (lambda v: Counter(v).most_common(1)[0][0])(v) for k, v in source_classes_analyze_filtered.items()})

for s in source_classes_analyze:
    print(source_classes_analyze[s])
    
with open('analyze-claude-sonnet-as-classifier_source_class_claude.pickle', 'wb') as f:
    pickle.dump(source_classes_analyze, f)


# ## Explain after Predict
# 
# Collect the predictions from Claude and prompt it to explain its decision. This focuses on *why* questions (not in a counterfactual manner yet). We want to extract whether such association-based explanations are connected with our V-CECE counterfactuals.
# 
# By having the lists of concepts for source and counterfactual classes *given* the (Claude) label, we can check what we need to change to make the transition. Therefore, does Claude as classifier have an understanding of discriminative concepts? Can they be connected with V-CECE counterfactuals?


def post_explain(image_names, explanations, prompt_analyze, analyze=False, explain=True):
    
    for name, lab in tqdm(zip(image_names, source_classes)):   
        label = source_classes[lab]
        
        # add self-explanations
        explain_prompt = f"""
        Can you explain me why you selected class {label} for this image? Stay confident on your prediction in class {label} and do not change it.
        Mainly focus on the key objects associated with the scene. These objects should returned in a Python list.
        Give me this list and nothing else.
        """
        
        chat = Chat(model_id, bedrock_runtime_client) 
        if analyze:
            chat.add_user_message_image(prompt_analyze, load_image(name)) # analyze image
            chat.generate()
            chat.add_user_message(explain_prompt)                         # answer about the analyzed image
        else:
            chat.add_user_message_image(explain_prompt, load_image(name)) # add a user message with an image and a text prompt
        expl = chat.generate()
        explanations[name].append(expl)
           
    return explanations
