import keyboard
import time
from PIL import Image
from mss import mss
import ctypes_wrappers as cws
import torch
from torch import nn
import numpy as np
from input_control import move_mouse, release_key, press_key, mouse_key

def capture_screenshot():
    with mss(with_cursor=True) as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        return Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

FPS = 20
SCALE_DOWN = 10

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


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.convs = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

        self.fc = nn.Sequential(
            nn.Linear(9216, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
        )

        self.fc2 = nn.Sequential(
            nn.Linear(64, 15),
            nn.ReLU(),
            nn.Linear(15, 2)
        )


    def forward(self, input):
        x = self.convs(input)
        x = x.view(x.size(0), -1)
        #print(x.shape, cursor_position.shape)
        x = self.fc(x)
        x = self.fc2(x)
        return x

# load state dict
net = Net()
net.load_state_dict(torch.load('./model/slither5.pt'))

print("ready")

while True: 
    start_time = time.time()


    if keyboard.is_pressed('ctrl + m') and not is_record_pressed:
        is_record_pressed = True      
        is_recording = not is_recording
                                      
        if not is_recording:           
            pass                       
    
    elif not keyboard.is_pressed('ctrl + m'):
        is_record_pressed = False


    if is_recording:
        time_count += 1/FPS
        img = capture_screenshot()
        
        img = img.resize((1920//10, 1080//10))
        # grayscale img
        img = img.convert('L')
        # convert to numpy array
        img = np.array(img)


        cursor_pos = cws.getCursorPos()

        img = torch.tensor(img).unsqueeze(0).unsqueeze(0).float()
        cursor_position = torch.tensor([cursor_pos[0]/1920-0.5, cursor_pos[1]/1080-0.5]).unsqueeze(0).float()
        #print(cursor_position)
        output = net(img)

        x = (output[0][0].item() + 0.5) * 1920
        y = (output[0][1].item() + 0.5) * 1080

        dx = x - cursor_pos[0]
        dy = y - cursor_pos[1]

        move_mouse(int(dx), int(dy))

       # print(output)
    

    # sleep remaining time to make fps]
    time.sleep(max(0, (1 / FPS) - (time.time() - start_time - 0.0001)))

    fps = 1 / (time.time() - start_time - 0.0001)
    #print("FPS: ", fps, " Is Recording: ", is_recording, end="\r")
