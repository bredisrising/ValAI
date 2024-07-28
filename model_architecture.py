import torch
from torch import nn
import torchvision
from torchsummary import summary

class Tim(nn.Module):
    def __init__(self):
        super().__init__()

        self.efficientnet = torchvision.models.efficientnet_b0(weights=torchvision.models.EfficientNet_B0_Weights.DEFAULT)
        self.efficientnet = self.efficientnet.features[:6]  

        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(20160, 128),
            nn.PReLU(),
            nn.Linear(128, 128),
            nn.PReLU(),
            nn.Linear(128, 64),
            nn.PReLU(),
            nn.Linear(64, 16),
            nn.PReLU(),
            nn.Linear(16, 4)
        )

    def forward(self, x):
        x = self.efficientnet(x)
        x = self.fc(x)

        return x
    
if __name__ == "__main__":
    tim = Tim()
    summary(tim, (3, 280, 150), device='cpu')
    