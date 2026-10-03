"""Tomato leaf-disease classifier.

Two interchangeable feature extractors feed a shared classifier head:
a pretrained ResNet-50 backbone (``resnet50_use=True``), or a small
convolutional stack trained from scratch. The head is a three-layer MLP with
dropout between layers.

Every hyperparameter is stored as a plain attribute because the training script
writes them into the checkpoint so inference can rebuild the same network.
"""

from __future__ import annotations

import torch
from torch import nn

# PlantVillage's tomato subset, which is what the dataset tooling expects.
DEFAULT_NUM_CLASSES = 10

# Spatial size the data loader produces.
INPUT_SIZE = 224


class Model(nn.Module):
    """Image classifier returning raw logits.

    Args:
        output_head: Number of classes to predict.
        out1: Channels produced by the first scratch conv block.
        out2: Channels produced by the second scratch conv block.
        hidden1: Width of the first fully-connected layer.
        hidden2: Width of the second fully-connected layer.
        hidden3: Width of the third fully-connected layer.
        dropout1: Dropout applied after the first fully-connected layer.
        dropout2: Dropout applied after the second.
        dropout3: Dropout applied after the third.
        resnet50_use: Use a pretrained ResNet-50 backbone instead of the
            scratch convolutional stack.
        pretrained: Load ImageNet weights for the backbone. Disabled
            automatically when weights cannot be downloaded.
    """

    def __init__(
        self,
        output_head: int = DEFAULT_NUM_CLASSES,
        out1: int = 32,
        out2: int = 64,
        hidden1: int = 512,
        hidden2: int = 256,
        hidden3: int = 128,
        dropout1: float = 0.4,
        dropout2: float = 0.3,
        dropout3: float = 0.2,
        resnet50_use: bool = True,
        pretrained: bool = True,
    ) -> None:
        super().__init__()

        self.output_head = output_head
        self.out1 = out1
        self.out2 = out2
        self.hidden1 = hidden1
        self.hidden2 = hidden2
        self.hidden3 = hidden3
        self.dropout1 = dropout1
        self.dropout2 = dropout2
        self.dropout3 = dropout3
        self.resnet50_use = resnet50_use

        if resnet50_use:
            self.features, feature_dim = self._build_resnet_backbone(pretrained)
        else:
            self.features, feature_dim = self._build_scratch_backbone(out1, out2)

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(feature_dim, hidden1),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout1),
            nn.Linear(hidden1, hidden2),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout2),
            nn.Linear(hidden2, hidden3),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout3),
            nn.Linear(hidden3, output_head),
        )

    @staticmethod
    def _build_resnet_backbone(pretrained: bool) -> tuple[nn.Module, int]:
        """Return a ResNet-50 trunk with its classifier removed."""
        from torchvision import models

        weights = None
        if pretrained:
            try:
                weights = models.ResNet50_Weights.IMAGENET1K_V2
            except Exception:
                # No cached weights and no network: fall back to random init
                # rather than failing to construct the model.
                weights = None

        try:
            backbone = models.resnet50(weights=weights)
        except Exception:
            backbone = models.resnet50(weights=None)

        feature_dim = backbone.fc.in_features
        backbone.fc = nn.Identity()

        return backbone, feature_dim

    @staticmethod
    def _build_scratch_backbone(out1: int, out2: int) -> tuple[nn.Module, int]:
        """Return a two-block convolutional trunk trained from scratch."""
        trunk = nn.Sequential(
            nn.Conv2d(3, out1, kernel_size=3, padding=1),
            nn.BatchNorm2d(out1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            nn.Conv2d(out1, out2, kernel_size=3, padding=1),
            nn.BatchNorm2d(out2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            nn.AdaptiveAvgPool2d((4, 4)),
        )

        return trunk, out2 * 4 * 4

    @property
    def config(self) -> dict:
        """Hyperparameters needed to rebuild this network from a checkpoint."""
        return {
            "output_head": self.output_head,
            "out1": self.out1,
            "out2": self.out2,
            "hidden1": self.hidden1,
            "hidden2": self.hidden2,
            "hidden3": self.hidden3,
            "dropout1": self.dropout1,
            "dropout2": self.dropout2,
            "dropout3": self.dropout3,
            "resnet50_use": self.resnet50_use,
        }

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Map a batch of images to class logits.

        Args:
            x: Float tensor shaped [batch, 3, 224, 224].

        Returns:
            Float tensor shaped [batch, output_head]. Raw logits, because the
            training loop uses CrossEntropyLoss.
        """
        return self.classifier(self.features(x))
