import re
import os
import shutil
import re
import ast

def parse_text_file(filepath):
    with open(filepath, 'r') as file:
        text = file.read()

    # Extract the classifications using regex
    # Look for lines that match "Classification: X" and store X in a list
    classifications = re.findall(r'Classification:\s*(\d+)', text)

    # The original classification is the first in the list
    # The final classification is the last
    original_class = int(classifications[0]) if classifications else None
    final_class = int(classifications[-1]) if classifications else None

    # Find the total steps by locating lines with "Output LVLM:" 
    # or you could rely on the final "Output LVLM: X" line
    # Here we match "Output LVLM: <some number>"
    steps = re.findall(r'Output LVLM:\s*(\d+)', text)
    num_steps = max(map(int, steps)) if steps else 0

    # Extract the edits list (the final list of lists) using a regex pattern
    # that captures something like [['remove', 'car', ...], ... ]
    edits_pattern = r'\[\[.*\]\]'
    edits_match = re.search(edits_pattern, text, re.DOTALL)
    edits_list = None
    if edits_match:
        # Evaluate the string as a Python list structure
        # (ONLY do this if you trust the source; otherwise parse it manually)
        edits_str = edits_match.group(0)
        edits_list = eval(edits_str)

    return {
        'number_of_steps': num_steps,
        'original_classification': original_class,
        'final_classification': final_class,
    }


def collect_counterfactual_images(base_directory, step_output_directory, source_output_directory):
    """
    Iterates through all subdirectories in the base_directory, checks for classification changes,
    and copies the corresponding step image to step_output_directory and the source image to source_output_directory.

    Parameters:
    - base_directory (str): Path to the directory containing subfolders with logs and images.
    - step_output_directory (str): Path to the directory where counterfactual step images will be stored.
    - source_output_directory (str): Path to the directory where source images will be stored.
    """
    # Create output directories if they don't exist
    for directory in [step_output_directory, source_output_directory]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created output directory at: {directory}")

    # Iterate through all items in the base directory
    for item in os.listdir(base_directory):
        item_path = os.path.join(base_directory, item)
        
        # Check if the item is a directory
        if os.path.isdir(item_path):
            logs_path = os.path.join(item_path, 'logs.txt')
            
            # Check if logs.txt exists in the directory
            if os.path.isfile(logs_path):
                try:
                    log_data = parse_text_file(logs_path)
                    
                    original_class = log_data.get('original_classification')
                    final_class = log_data.get('final_classification')
                    number_of_steps = log_data.get('number_of_steps')

                    # Validate extracted data
                    if original_class is None or final_class is None or number_of_steps is None:
                        print(f"Missing classification or step information in {logs_path}. Skipping.")
                        continue

                    # Check if classification has changed
                    if (original_class == 0 and final_class == 1) or (original_class == 1 and final_class == 0):
                        # Construct the step image filename
                        step_image_filename = f"step_{number_of_steps}.jpg"
                        step_image_source_path = os.path.join(item_path, step_image_filename)
                        
                        # Define the new filename for the step image
                        step_image_new_filename = f"{item}_cf.jpg"
                        step_destination_path = os.path.join(step_output_directory, step_image_new_filename)
                        
                        # Check if the step image exists
                        if os.path.isfile(step_image_source_path):
                            # To avoid overwriting, rename the file if it already exists
                            if os.path.exists(step_destination_path):
                                base_name, ext = os.path.splitext(step_image_new_filename)
                                counter = 1
                                while True:
                                    new_filename = f"{base_name}_{counter}{ext}"
                                    new_destination = os.path.join(step_output_directory, new_filename)
                                    if not os.path.exists(new_destination):
                                        step_destination_path = new_destination
                                        break
                                    counter += 1
                            
                            # Copy the step image to the step output directory with the new name
                            shutil.copy2(step_image_source_path, step_destination_path)
                            print(f"Copied step image {step_image_source_path} to {step_destination_path}")
                        else:
                            print(f"Step image file {step_image_filename} not found in {item_path}")

                        # Define the source image filename
                        source_image_filename = "source.jpg"  # Always use 'source.jpg'
                        source_image_path = os.path.join(item_path, source_image_filename)
                        
                        # Define the new filename for the source image
                        source_image_new_filename = f"{item}_source.jpg"
                        source_destination_path = os.path.join(source_output_directory, source_image_new_filename)
                        
                        # Check if the source image exists
                        if os.path.isfile(source_image_path):
                            # To avoid overwriting, rename the file if it already exists
                            if os.path.exists(source_destination_path):
                                base_name, ext = os.path.splitext(source_image_new_filename)
                                counter = 1
                                while True:
                                    new_filename = f"{base_name}_{counter}{ext}"
                                    new_destination = os.path.join(source_output_directory, new_filename)
                                    if not os.path.exists(new_destination):
                                        source_destination_path = new_destination
                                        break
                                    counter += 1
                            
                            # Copy the source image to the source output directory with the new name
                            shutil.copy2(source_image_path, source_destination_path)
                            print(f"Copied source image {source_image_path} to {source_destination_path}")
                        else:
                            print(f"Source image file {source_image_filename} not found in {item_path}")
                    else:
                        print(f"No classification change in {item_path}")
                except Exception as e:
                    print(f"Error processing {logs_path}: {e}")
            else:
                print(f"No logs.txt found in {item_path}")
        else:
            print(f"Skipping non-directory item: {item_path}")

if __name__ == '__main__':
    # Define the base directory containing all subfolders
    base_dir = <PATH-TO-GENERATED-IMAGES>  # Update this path as needed

    # Define the output directories for counterfactual step images and source images
    counterfactual__dir = <PATH-TO-SAVE-CE-IMAGES>
    counterfactual_source_dir = <PATH-TO-SAVE-SOURCE-IMAGES>

    # Run the collection process
    collect_counterfactual_images(base_dir, counterfactual_step_dir, counterfactual_source_dir)