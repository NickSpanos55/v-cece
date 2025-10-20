import sys
sys.path.append("TIME")

from models import get_classifier
import PIL.Image as Image
import torch
import torch.nn.functional as F
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import os


class Args:
    
    def __init__(self):
        self.dataset = "BDD100k"
        self.label_query = 0
        self.classifier_path = "decision_densenet/bdd/checkpoint.tar"
        
        
class BDD100k_classifier:
    
    def __init__(self, device = "cpu"):
        self.device = device
        self.args = Args()
        self.classifier = get_classifier(self.args)
        self.classifier.to(device).eval()
        
        image_size = 256
        normalize=False
        padding=False
    
        self.transform = transforms.Compose([
                    transforms.Resize((image_size, 2 * image_size)),
                    transforms.ToTensor(),
                    torch.nn.ConstantPad2d((0, 0, image_size // 2, image_size // 2), 0) if padding else lambda x: x,  # lambda x: F.pad(x, (0, 0, 128, 128), value=0)
                    transforms.Normalize([0.5, 0.5, 0.5],
                                         [0.5, 0.5, 0.5]) if normalize else lambda x: x
                ])
        
        
    def classify(self, image_path):
        with open(image_path, "rb") as f:
            img = Image.open(f)
            img = img.convert('RGB')

        img = self.transform(img)
        
        img = img.to(self.device)
        pred = (self.classifier(img) > 0).int()
        return int (pred[0])
