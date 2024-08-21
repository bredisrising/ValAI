import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
import numpy as np
from model_architecture import BasicOneFrame
import dataset


def train(num_epochs, nnet, optimizer, dataloader, device, model_path, save_interval=1):
    mse = nn.MSELoss()

    losses = []

    for epoch in range(num_epochs):

        if epoch % save_interval == 0 and epoch != 0:
            torch.save(nnet.state_dict(), model_path)

        for batch_index, batch in enumerate(dataloader):
            frames, mouse_movements = batch
            frames = frames.to(device)
            mouse_movements = mouse_movements.to(device)

            predicted_mouse_movements = nnet(frames)
            #print(predicted_mouse_movements[0])

            optimizer.zero_grad()
            loss = mse(predicted_mouse_movements, mouse_movements)
            loss.backward()
            optimizer.step()

            losses.append(loss.item())
            if len(losses) > 100:
                losses.pop(0)
            avg_loss = sum(losses) / len(losses)

            print(f"{epoch}, {batch_index}, {avg_loss:.6f}, {loss.item():.6f}", end="                         \r")

if __name__ == "__main__":
    device = "cuda"
    model_path = "./trained/behavior_clone.pth"
    
    nnet = BasicOneFrame().to(device)
    #nnet.load_state_dict(torch.load(model_path))
    optimizer = torch.optim.Adam(nnet.parameters(), lr=0.0001)

    data = dataset.BasicDataset()
    dataloader = DataLoader(data, batch_size=8, shuffle=True)

    train(1000000, nnet, optimizer, dataloader, device, model_path)