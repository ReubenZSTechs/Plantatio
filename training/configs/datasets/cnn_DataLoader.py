"""Dataset and image transforms for the tomato leaf-disease classifier.

Two transform pipelines are exported on purpose:

``train_transform`` applies random augmentation and belongs only in training.
``eval_transform`` is deterministic and is what validation, test and inference
must use — reusing the augmentation chain at inference made every prediction
random, so the same leaf scored differently on each call.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

IMAGE_SIZE = 224
RESIZE_SIZE = 256

# ImageNet statistics, matching the pretrained ResNet-50 backbone.
NORMALIZE_MEAN = [0.485, 0.456, 0.406]
NORMALIZE_STD = [0.229, 0.224, 0.225]

train_transform = transforms.Compose([
    transforms.Resize(RESIZE_SIZE),
    transforms.RandomResizedCrop(IMAGE_SIZE, scale=(0.8, 1.0)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.25),
    transforms.RandomRotation(degrees=20),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
    transforms.GaussianBlur(kernel_size=(3, 5), sigma=(0.1, 2.0)),
    transforms.ToTensor(),
    transforms.Normalize(mean=NORMALIZE_MEAN, std=NORMALIZE_STD),
])

eval_transform = transforms.Compose([
    transforms.Resize(RESIZE_SIZE),
    transforms.CenterCrop(IMAGE_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(mean=NORMALIZE_MEAN, std=NORMALIZE_STD),
])

# Retained so existing imports keep working; prefer the explicit names above.
transform = train_transform


class TomatoDataset(Dataset):
    """Leaf images listed in a CSV of ``filepath,class`` rows.

    Class indices are assigned in sorted order so they are stable across runs
    and match the labels persisted in the training checkpoint.
    """

    def __init__(self, csv_file: str | Path, transform=None):
        # Imported here rather than at module scope so the inference path,
        # which only needs the transforms above, does not pull in pandas.
        import pandas as pd

        csv_path = Path(csv_file)

        if not csv_path.is_file():
            # Previously this printed and returned, leaving a half-built object
            # that failed later with a confusing AttributeError.
            raise FileNotFoundError(f"Dataset index not found: {csv_path}")

        self.data = pd.read_csv(csv_path)

        missing = {"filepath", "class"} - set(self.data.columns)
        if missing:
            raise ValueError(f"{csv_path} is missing column(s): {sorted(missing)}")

        self.transform = transform
        self.classes = sorted(self.data["class"].unique())
        self.class_label = {name: index for index, name in enumerate(self.classes)}

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index: int):
        """Return (image_tensor, class_index) for one row."""
        row = self.data.iloc[index]

        image = Image.open(row["filepath"]).convert("RGB")
        if self.transform is not None:
            image = self.transform(image)

        return image, self.class_label[row["class"]]
