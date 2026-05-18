import torch
import torchvision

from torch import nn
from torchvision import models

import warnings
warnings.filterwarnings(action='ignore')


class Model(torch.nn.Module):
    def __init__(self, output_head: int, dropout1=0.2, dropout2=0.1, dropout3=0.5, hidden1=1024, hidden2=256, hidden3=128, out1=32, out2=64, resnet50_use=False):
        super().__init__()

        self.output_head = output_head
        self.dropout1 = dropout1
        self.dropout2 = dropout2
        self.dropout3 = dropout3
        self.hidden1 = hidden1
        self.hidden2 = hidden2
        self.hidden3 = hidden3
        self.out1 = out1
        self.out2 = out2
        self.resnet50_use = resnet50_use

        self.cnn_layer_1 = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=out1, kernel_size=(3, 3), padding=1, padding_mode='reflect'),
            nn.BatchNorm2d(num_features=out1),
            nn.MaxPool2d(kernel_size=2),
            nn.ReLU(),
            nn.Dropout(dropout1)
        )

        self.cnn_layer_2 = nn.Sequential(
            nn.Conv2d(in_channels=out1, out_channels=out2, kernel_size=(3, 3), padding=1, padding_mode='reflect'),
            nn.BatchNorm2d(num_features=out2),
            nn.MaxPool2d(kernel_size=2),
            nn.ReLU(),
            nn.Dropout(dropout2)
        )

        if resnet50_use:
            self.extractor = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            self.extractor.conv1 = nn.Conv2d(in_channels=out2, out_channels=64, kernel_size=7, stride=2, padding=3, bias=False)
            in_features = self.extractor.fc.in_features
            self.extractor.fc = nn.Identity()
        else:
            self.pool = nn.AdaptiveAvgPool2d(output_size=(3, 3))
            self.flatten = nn.Flatten()
            in_features = out2 * 3 * 3

        self.fc_layer = nn.Sequential(
            nn.Linear(in_features=in_features, out_features=hidden1),
            nn.ReLU(),

            nn.Linear(in_features=hidden1, out_features=hidden2),
            nn.ReLU(),
            nn.Dropout(dropout3),

            nn.Linear(in_features=hidden2, out_features=hidden3),
            nn.ReLU(),

            nn.Linear(in_features=hidden3, out_features=output_head)
        )


    def forward(self, x):
        x = self.cnn_layer_1(x)
        x = self.cnn_layer_2(x)

        if self.resnet50_use:
            x = self.extractor(x)
        else:
            x = self.pool(x)
            x = self.flatten(x)

        x = self.fc_layer(x)
        return x