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
#from input_control import move_mouse, release_key, press_key, mouse_key

from interception_controller import init, move_mouse, release_key, press_key, press_mouse, release_mouse

init()

def capture_screenshot():
    with mss(with_cursor=True) as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        return Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

FPS = 10
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

class Net(nn.Module):
    def __init__(self, eff):
        super().__init__()
        # self.convs = nn.Sequential(
        #     nn.Conv2d(1, 64, 3, padding=1),
        #     nn.LeakyReLU(),
        #     nn.Conv2d(64, 64, 3, padding=1),
        #     nn.LeakyReLU(.1),
        #     nn.MaxPool2d(2),
        #     nn.Conv2d(64, 128, 3, padding=1),
        #     nn.LeakyReLU(.1),
        #     nn.MaxPool2d(2),
        #     nn.Conv2d(128, 128, 3, padding=1),
        #     nn.LeakyReLU(.1),
        #     nn.MaxPool2d(2),
        #     nn.Conv2d(128, 128, 3, padding=1),
        #     nn.LeakyReLU(.1),
        #     nn.MaxPool2d(2),
        #     nn.Conv2d(128, 128, 3, padding=1),
        #     nn.LeakyReLU(.1),
        #     nn.MaxPool2d(2),
        # )

        self.efficientnet = eff



        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(20160, 128),
            nn.PReLU(),
            nn.Linear(128, 128),
            nn.PReLU(),
            nn.Linear(128, 128),
            nn.PReLU(),
            nn.Linear(128, 64),
        )

        self.fc2 = nn.Sequential(
            nn.Linear(64, 16),
            nn.Linear(16, 4),
            
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
net.load_state_dict(torch.load('./valorant_models/mouse_model_cont_2.pt'))

print("ready")

THRESHOLD = .5

while True: 
    start_time = time.time()


    if keyboard.is_pressed('ctrl + m') and not is_record_pressed:
        is_record_pressed = True      
        is_recording = not is_recording
                                      
        if not is_recording:           
            pass                       
    
    elif not keyboard.is_pressed('ctrl + m'):
        is_record_pressed = False


    # if arrow up is pressed, increase threshold
    if keyboard.is_pressed('up'):
        move_mouse(0, -10)

    if keyboard.is_pressed('down'):
        move_mouse(0, 10)
    
    if keyboard.is_pressed('left'):
        move_mouse(-10, 0)
    
    if keyboard.is_pressed('right'):
        move_mouse(10, 0)

    if is_recording:
        time_count += 1/FPS
        img = capture_screenshot()
        
        img = img.resize((1920//5, 1080//5))
        img = cv2.resize(np.array(img, dtype=np.float32), (280, 150))/255.0
        # grayscale img
        # convert to numpy array

        # red channel only
        #img = img[:,:,0]
        #print(img.shape)
        img = torch.tensor(img).permute(2, 0, 1).unsqueeze(0)
        #print(img.shape)

        output = net(img)
        print(output)
        #action = torch.argmax(output[0]).item()
        #print(action)
        
        multiplier = 2000
        move_mouse(int(output[0][2].item()*(output[0][1].item()*multiplier)), int(output[0][3].item()*(output[0][1].item()*multiplier)))
        
        if output[0][0] > THRESHOLD:
            press_mouse("left")
        elif output[0][0] < -THRESHOLD:
            release_mouse("left")


        # if action == 0:
        #     pass
        # elif action == 1:
        #     move_mouse(100, 0)
        # elif action == 2:
        #     move_mouse(-100, 0)

        # none = output[0][0].item()
        # dx = output[0][0].item()
        #dy = output[0][1].item()

        # w = output[0][2].item()
        # a = output[0][3].item()
        # s = output[0][4].item()
        # d = output[0][5].item()
        # space = output[0][6].item()
        # shift = output[0][7].item()
        # ctrl = output[0][8].item()
        # leftclick = output[0][0].item()

        # if w > THRESHOLD:
        #     #print(press_key(0x57))
        #     press_key("w")
        # elif w < -THRESHOLD:
        #     release_key("w")
        
        # if a > THRESHOLD:
        #     press_key("a")
        # elif a < -THRESHOLD:
        #     release_key("a")
        
        # if s > THRESHOLD:
        #     press_key("s")
        # elif s < -THRESHOLD:
        #     release_key("s")
        
        # if d > THRESHOLD:
        #     press_key("d")
        # elif d < -THRESHOLD:
        #     release_key("d")
        
        # if space > THRESHOLD:
        #     press_key("space")
        # elif space < -THRESHOLD:
        #     release_key("space")

        # if shift > THRESHOLD:
        #     press_key("shift")
        # elif shift < -THRESHOLD:
        #     release_key("shift")
        
        # if ctrl > THRESHOLD:
        #     press_key("ctrl")
        # elif ctrl < -THRESHOLD:
        #     release_key("ctrl")
        
        # if leftclick > THRESHOLD:
        #     press_mouse("left")
        # else:
        #     release_mouse("left")



        #move_mouse  (int(dx*1000.0), int(dy*1000.0))

       # print(output)
    

    # sleep remaining time to make fps]
    time.sleep(max(0, (1 / FPS) - (time.time() - start_time - 0.0001)))

    fps = 1 / (time.time() - start_time - 0.0001)
    #print("FPS: ", fps, " Is Recording: ", is_recording, end="\r")