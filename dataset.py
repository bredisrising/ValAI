import torch
from torch.utils.data import Dataset
import numpy as np
from PIL import Image
import pickle

class BasicDataset(Dataset):
    def __init__(self):
        
        # load pkls
        data1 = pickle.load(open("./val_range_data/save1.pkl", "rb"))
        #data2 = pickle.load(open("./val_range_data/save2.pkl", "rb"))

        # filtering
        self.frames = []
        self.mouse_movements = []

        for i in range(len(data1[0])):
            if data1[3][i][0] == 0. and data1[3][i][1] == 0.:
                continue
            else:
                self.frames.append(data1[0][i])
                self.mouse_movements.append(data1[3][i])


        self.frames = torch.tensor(np.array(self.frames))
        self.mouse_movements = torch.tensor(self.mouse_movements)

        self.frames = torch.tensor(np.array(data1[0]))
        self.mouse_movements = torch.tensor(data1[3])
        
        # normalize (separate magnitude)
        theoretical_max_magnitude = torch.linalg.norm(torch.tensor([1920., 1080.]))
        self.mouse_movements = torch.cat((self.mouse_movements, torch.zeros((self.mouse_movements.shape[0], 1))), dim = 1)
        self.magnitudes = torch.linalg.norm(self.mouse_movements[:, :2], dim=1)
        self.mouse_movements[:, 2] = self.magnitudes
        self.mouse_movements[:, :2] /= self.mouse_movements[:, 2].unsqueeze(-1)
        self.mouse_movements[:, 2] /= theoretical_max_magnitude
        self.mouse_movements = torch.nan_to_num(self.mouse_movements)

        # shift
        self.mouse_movements = torch.roll(self.mouse_movements, -1, 0)


        # EXTRA - set magnitude - hand inconsistency could me messing it up
        self.mouse_movements[:, 2] = self.mouse_movements[:, 2].mean()
        # print(self.mouse_movements)

        #print(self.frames[0].shape, self.frames[0].max())

        print("Num Data Examples: ", len(self))

    def __len__(self):
        #return 10
        return self.frames.shape[0] # last one will have wrong mouse movements

    def __getitem__(self, index):
        i = index
        return self.frames[i].permute(2,0,1).to(torch.float32) / 255.0, self.mouse_movements[i]
 
if __name__ == "__main__":
    data = BasicDataset()
    