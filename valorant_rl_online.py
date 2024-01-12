import keyboard
import time
from PIL import Image
from mss import mss
import ctypes_wrappers as cws
import torch
from torch import nn
import numpy as np
import torchvision
import cv2
import random
from copy import deepcopy
from interception_controller import init, move_mouse

init()

def capture_screenshot():
    with mss(with_cursor=True) as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        return Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

FPS = 3
SCALE_DOWN = 5

is_recording = False
is_record_pressed = False

frames = [] 

keyboard_data = []
current_frame_keyboard_data = []
mouse_data = []
current_frame_mouse_data = []
cursor_positions = []


time_count = 0
save_count = 0 # implement detector to continue
frame_count = 0

efficientnet = efficientnet = torchvision.models.efficientnet_b0()
efficientnet = efficientnet.features[:6]


class Value(nn.Module):
    def __init__(self, eff):
        super().__init__()

        self.efficientnet = eff

        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(20160, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.PReLU(),
            nn.Linear(64, 32),
        )

        self.fc2 = nn.Sequential(
            nn.Linear(32, 16),
            nn.Linear(16, 1),
        
        )

    def forward(self, input):
        x = self.efficientnet(input)

        #print(x.shape, cursor_position.shape)
        x = self.fc(x)
        x = self.fc2(x)
        #print(means)
        #stds = torch.clamp(self.logstds.exp(), 1e-3, 5)

        return x

class Net(nn.Module):
    def __init__(self, eff):
        super().__init__()

        self.efficientnet = eff

        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(20160, 256),
            nn.Tanh(),
            nn.Linear(256, 256),
            nn.Tanh(),
            nn.Linear(256, 128),
            nn.Tanh(),
            nn.Linear(128, 128),
            nn.Tanh(),
            nn.Linear(128, 64),
        )

        self.fc2 = nn.Sequential(
            nn.Linear(64, 16),
            nn.Linear(16, 3),
            nn.Tanh()
        )
    


    def forward(self, input):
        x = self.efficientnet(input)

        #print(x.shape, cursor_position.shape)
        x = self.fc(x)
        x = self.fc2(x)
        #print(means)
        #stds = torch.clamp(self.logstds.exp(), 1e-3, 5)

        return x
    
# load state dict
    
net = Net(efficientnet)
net.load_state_dict(torch.load('./valorant_models/mouse_model.pt'))

value_efficientnet = deepcopy(efficientnet)
value = Value(value_efficientnet)
value.load_state_dict(torch.load('./valorant_models/mouse_value_model.pt'))

print("ready")

THRESHOLD = .6

entropies = []
inputs = []
actions = []
log_probs = []

optim = torch.optim.Adam(net.parameters(), lr=5e-4)
value_optim = torch.optim.Adam(net.parameters(), lr=1e-3)

while True: 
    start_time = time.time()


    if keyboard.is_pressed('ctrl + m') and not is_record_pressed:
        is_record_pressed = True      
        is_recording = not is_recording

        actions.clear()
        log_probs.clear()
        inputs.clear()

        print("Is Recording: ", is_recording, end="\r")

        if not is_recording:           
            pass                 
    
    elif not keyboard.is_pressed('ctrl + m'):
        
        if keyboard.is_pressed('ctrl + r'):
            torch.save(net.state_dict(), './valorant_models/mouse_model.pt')
            torch.save(value.state_dict(), './valorant_models/mouse_value_model.pt')
            print('saved')
        is_record_pressed = False


    if is_recording:
        time_count += 1/FPS

        if keyboard.is_pressed('plus'):
            print('training')
            # discount reward
            returns = []
            advantages = []
            for i in range(len(log_probs)-1):
                bruh = .99**(len(log_probs)-i-1) + value(inputs[i+1])
                returns.append(bruh*1)

            returns.append(1.0)
            entropy = 0
            for i in range(len(returns)):
                entropy += entropies[i]
                advantage = returns[i] - value(inputs[i])
                advantages.append(advantage)

            vloss = 0
            ploss = 0
            advantages = torch.stack(advantages)
            vloss = advantages.pow(2).sum()


            log_probs_tensor = torch.stack(log_probs)
            ploss = (-log_probs_tensor * advantages.detach()).sum() + entropy*.1

            value_optim.zero_grad()
            vloss.backward()
            value_optim.step()


            optim.zero_grad()
            ploss.backward()
            optim.step()

            actions.clear()
            inputs.clear()
            log_probs.clear()

            print('done')
        
        if keyboard.is_pressed('-'):
            print('training')
            # discount reward
            returns = []
            advantages = []
            for i in range(len(log_probs)-1):
                bruh = .95**(len(log_probs)-i-1) + value(inputs[i+1])
                returns.append(bruh*-.5)

            returns.append(-1.0)

            for i in range(len(returns)):
                advantage = returns[i] - value(inputs[i])
                advantages.append(advantage)

            vloss = 0
            ploss = 0
            advantages = torch.stack(advantages)
            vloss = advantages.pow(2).sum()


            log_probs_tensor = torch.stack(log_probs)
            ploss = (-log_probs_tensor * advantages.detach()).sum()

            value_optim.zero_grad()
            vloss.backward()
            value_optim.step()


            optim.zero_grad()
            ploss.backward()
            optim.step()

            actions.clear()
            inputs.clear()
            log_probs.clear()

            print('done')


        img = capture_screenshot()
        
        img = img.resize((1920//5, 1080//5))
        img = cv2.resize(np.array(img, dtype=np.float32), (280, 150))/255.0

        img = torch.tensor(img).permute(2, 0, 1).unsqueeze(0)


        output = net(img)
        
        dist = torch.distributions.Categorical(logits=output)
        
        print(output)

        if random.random() < .2:
            action = dist.sample()
        else:
            action = torch.argmax(output[0])
        # action = torch.tensor([0])
        # if keyboard.is_pressed("left"):
        #     action = torch.tensor([2])
        # elif keyboard.is_pressed("right"):
        #     action = torch.tensor([1])

        inputs.append(img)
        actions.append(action)
        log_probs.append(dist.log_prob(action))
        entropies.append(dist.entropy())

        #print(output)
        #action = torch.argmax(output[0]).item()
        #print(action)
        
        
        if action.item() == 0:
            pass
        elif action.item() == 1:
            move_mouse(300, 0)
        elif action.item() == 2:
            move_mouse(-300, 0)



    # sleep remaining time to make fps]
    time.sleep(max(0, (1 / FPS) - (time.time() - start_time - 0.0001)))

    fps = 1 / (time.time() - start_time - 0.0001)
    #print("FPS: ", fps, " Is Recording: ", is_recording, end="\r")