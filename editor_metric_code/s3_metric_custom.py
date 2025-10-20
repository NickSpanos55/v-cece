import os
import re
import torch
import itertools
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm
from torch.utils import data
from torchvision import transforms
from simsiam_folder.eval_utils.simsiam import get_simsiam_dist  

gpu_id =   # GPU id to use
source_dir =  # Path to the directory containing source images
counterfactual_dir =   # Path to the directory containing counterfactual images
weights_path =  # Path to the SimSiam model weights
batch_size =  # Batch size for processing images


# Set device
if gpu_id.lower() == 'cpu':
    device = torch.device('cpu')
else:
    device = torch.device(f'cuda:{gpu_id}' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

class PairedImageDataset(data.Dataset):
    def __init__(self, source_dir, counterfactual_dir, transform=None):
        """
        Initializes the dataset by pairing source and counterfactual images based on their unique base identifiers.

        Args:
            source_dir (str): Path to the source images directory.
            counterfactual_dir (str): Path to the counterfactual images directory.
            transform (callable, optional): Optional transform to be applied on a sample.
        """
        self.source_dir = source_dir
        self.counterfactual_dir = counterfactual_dir
        self.transform = transform

        # Regular expressions to extract base identifiers
        # For source images: capture everything before '_source.jpg'
        source_pattern = re.compile(r'^(.*)\.jpg_source\.jpg$', re.IGNORECASE)
        # For counterfactual images: capture everything before '_cf.jpg'
        counterfactual_pattern = re.compile(r'^(.*)\.jpg_cf\.jpg$', re.IGNORECASE)

        # Get list of source and counterfactual images
        self.source_images = [
            fname for fname in os.listdir(source_dir)
            if re.match(source_pattern, fname)
        ]

        self.counterfactual_images = [
            fname for fname in os.listdir(counterfactual_dir)
            if re.match(counterfactual_pattern, fname)
        ]

        # Extract base identifiers using regex
        self.source_bases = set()
        for fname in self.source_images:
            match = source_pattern.match(fname)
            if match:
                base = match.group(1) + '.jpg'  # Adding '.jpg' back to base
                self.source_bases.add(base)
            else:
                print(f"Skipping unmatched source filename: {fname}")

        self.counterfactual_bases = set()
        for fname in self.counterfactual_images:
            match = counterfactual_pattern.match(fname)
            if match:
                base = match.group(1) + '.jpg'  # Adding '.jpg' back to base
                self.counterfactual_bases.add(base)
            else:
                print(f"Skipping unmatched counterfactual filename: {fname}")

        # Find common base identifiers
        self.common_bases = sorted(list(self.source_bases.intersection(self.counterfactual_bases)))
        print(f"Found {len(self.common_bases)} paired images.")

        # Identify any unmatched images
        unmatched_sources = self.source_bases - self.counterfactual_bases
        unmatched_counterfactuals = self.counterfactual_bases - self.source_bases

        if unmatched_sources:
            print(f"Warning: {len(unmatched_sources)} source images do not have corresponding counterfactual images.")
            # Optionally, list some unmatched source images
            for fname in list(unmatched_sources)[:5]:
                print(f"  Unmatched source: {fname}_source.jpg")

        if unmatched_counterfactuals:
            print(f"Warning: {len(unmatched_counterfactuals)} counterfactual images do not have corresponding source images.")
            # Optionally, list some unmatched counterfactual images
            for fname in list(unmatched_counterfactuals)[:5]:
                print(f"  Unmatched counterfactual: {fname}_cf.jpg")

    def __len__(self):
        return len(self.common_bases)

    def __getitem__(self, idx):
        """
        Retrieves the paired source and counterfactual images.

        Args:
            idx (int): Index of the image pair.

        Returns:
            tuple: (source_image, counterfactual_image)
        """
        base_name = self.common_bases[idx]
        source_filename = f"{base_name}_source.jpg"
        counterfactual_filename = f"{base_name}_cf.jpg"

        source_path = os.path.join(self.source_dir, source_filename)
        counterfactual_path = os.path.join(self.counterfactual_dir, counterfactual_filename)

        # Verify that both files exist
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source image not found: {source_path}")
        if not os.path.exists(counterfactual_path):
            raise FileNotFoundError(f"Counterfactual image not found: {counterfactual_path}")

        source_image = self.load_image(source_path)
        counterfactual_image = self.load_image(counterfactual_path)

        return source_image, counterfactual_image

    def load_image(self, path):
        """
        Loads and transforms an image.

        Args:
            path (str): Path to the image file.

        Returns:
            Tensor: Transformed image tensor.
        """
        try:
            with Image.open(path) as img:
                img = img.convert('RGB')  # Ensure image is in RGB format
                if self.transform:
                    img = self.transform(img)
                return img
        except Exception as e:
            raise IOError(f"Error loading image {path}: {e}")


# Define image transformations
transform = transforms.Compose([
    transforms.Resize(256),              # Resize the shorter side to 256
    transforms.CenterCrop(224),          # Crop the center 224x224 pixels
    transforms.ToTensor(),               # Convert PIL Image to Tensor
    transforms.Normalize(                # Normalize with ImageNet means and stds
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


@torch.inference_mode()
def compute_similarity(oracle, source_dir, counterfactual_dir, batch_size, device):
    """
    Computes the similarity between source and counterfactual images.

    Args:
        oracle (torch.nn.Module): The SimSiam model for computing distances.
        source_dir (str): Directory containing source images.
        counterfactual_dir (str): Directory containing counterfactual images.
        batch_size (int): Number of image pairs per batch.
        device (torch.device): Device to run computations on.

    Returns:
        np.ndarray: Array of similarity scores.
    """
    # Initialize the dataset and dataloader
    dataset = PairedImageDataset(
        source_dir=source_dir,
        counterfactual_dir=counterfactual_dir,
        transform=transform
    )
    loader = data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,  # Adjust based on your system. Use 0 if issues arise in Jupyter.
        pin_memory=True if device.type == 'cuda' else False
    )

    similarities = []
    for source, counterfactual in tqdm(loader, desc="Computing similarities"):
        source = source.to(device, dtype=torch.float)
        counterfactual = counterfactual.to(device, dtype=torch.float)
        similarity = oracle(source, counterfactual).cpu().numpy()
        similarities.append(similarity)

    return np.concatenate(similarities)


# Load the SimSiam model
oracle = get_simsiam_dist(weights_path)
oracle.to(device)
oracle.eval()

# Compute similarities
similarities = compute_similarity(
    oracle=oracle,
    source_dir=source_dir,
    counterfactual_dir=counterfactual_dir,
    batch_size=batch_size,
    device=device
)

# Compute and print the average similarity
average_similarity = np.mean(similarities)
print(f'SimSiam Average Similarity: {average_similarity:.4f}')