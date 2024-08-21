import torch
from torch import nn
import torchvision
from torchsummary import summary

class LSTM(nn.Module):
    def __init__(self, hidden_state_size, input_size):
        super().__init__()

        self.forget_linear = nn.Linear(input_size + hidden_state_size, hidden_state_size)

        self.cell_state = torch.zeros((hidden_state_size))

    def forward(self, new_input, previous_hidden_state):
        combined_input = torch.cat(new_input, previous_hidden_state)
        forgetter = self.forget_linear(combined_input)



class BasicOneFrame(nn.Module):
    def __init__(self):
        super().__init__()

        self.efficientnet = torchvision.models.efficientnet_b0(weights=torchvision.models.EfficientNet_B0_Weights.DEFAULT)
        self.efficientnet = self.efficientnet.features[:6]  
        self.efficientnet.train()

        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(37632, 512),
            nn.PReLU(),
            nn.Linear(512, 512),
            nn.PReLU(),
            nn.Linear(512, 128),
            nn.PReLU(),
            nn.Linear(128, 64),
            nn.PReLU(),
            nn.Linear(64, 3)
        )

    def forward(self, x):
        x = self.efficientnet(x)
        # print(x.shape, "\n\n\n")

        x = self.fc(x)

        return x
    
    
if __name__ == "__main__":
    tim = BasicOneFrame()
    summary(tim, (3, 1080//5, 1920//5), device='cpu')
    