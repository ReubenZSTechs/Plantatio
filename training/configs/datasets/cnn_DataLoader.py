import os
from dotenv import load_dotenv

load_dotenv()

from torchvision import transforms
from torch.utils.data import random_split, DataLoader, Dataset
from PIL import Image

from collections import Counter
import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings(action='ignore')


transform = transforms.Compose([
    transforms.Resize(256),
    transforms.RandomResizedCrop(224, scale = (0.8, 1.0)),
    transforms.RandomHorizontalFlip(p = 0.5),
    transforms.RandomVerticalFlip(p = 0.25),
    transforms.RandomRotation(degrees = 20),
    transforms.ColorJitter(                               
        brightness=0.3, 
        contrast=0.3, 
        saturation=0.3, 
        hue=0.1
    ),
    transforms.GaussianBlur(kernel_size=(3, 5), sigma=(0.1, 2.0)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])


class TomatoDataset(Dataset):
    def __init__(self, csv_file: str, transform: transforms):
        try:
            self.data = pd.read_csv(csv_file)
        except FileNotFoundError:
            print(f"File not found: {csv_file}")
            return
        
        self.transform = transform
        self.classes = sorted(self.data['class'].unique())
        self.class_label = {cls: idx for idx, cls in enumerate(self.classes)}

    
    def __len__(self):
        return len(self.data)
    

    def __getitem__(self, index):
        img_path = self.data.iloc[index, 0]
        img_label_name = self.data.iloc[index, 1]
        img_label = self.class_label[img_label_name]

        image = Image.open(img_path).convert("RGB")

        if self.transform:
            img = self.transform(image)

        return img, img_label