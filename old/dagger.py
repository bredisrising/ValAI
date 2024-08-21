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
import ctypes as cts
import ctypes.wintypes as wts
from old_win_recorder import Recorder
import ctypes_wrappers as cws
import math
from old_win_recorder import wnd_proc, register_devices

HWND_MESSAGE = -3

WM_QUIT = 0x0012
WM_INPUT = 0x00FF
WM_KEYUP = 0x0101
WM_CHAR = 0x0102

HID_USAGE_PAGE_GENERIC = 0x01

RIDEV_NOLEGACY = 0x00000030
RIDEV_INPUTSINK = 0x00000100
RIDEV_CAPTUREMOUSE = 0x00000200

RID_HEADER = 0x10000005
RID_INPUT = 0x10000003

RIM_TYPEMOUSE = 0
RIM_TYPEKEYBOARD = 1
RIM_TYPEHID = 2

PM_NOREMOVE = 0x0000
PM_REMOVE = 0x0001

wnd_cls = "SO049572093_RawInputWndClass"
wcx = cws.WNDCLASSEX()
wcx.cbSize = cts.sizeof(cws.WNDCLASSEX)

wcx.lpfnWndProc = cws.WNDPROC(wnd_proc)
wcx.hInstance = cws.GetModuleHandle(None)
wcx.lpszClassName = wnd_cls

res = cws.RegisterClassEx(cts.byref(wcx))

hwnd = cws.CreateWindowEx(0, wnd_cls, None, 0, 0, 0, 0, 0, 0, None, wcx.hInstance, None)

register_devices(hwnd)

msg = wts.MSG()
pmsg = cts.byref(msg)

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

is_playing = False
is_play_pressed = False


time_count = 0
save_count = 0 # implement detector to continue
frame_count = 0

efficientnet = efficientnet = torchvision.models.efficientnet_b0()
efficientnet = efficientnet.features[:6]

last_img = None
img = capture_screenshot()


mouse_multiplier = 566

class Net(nn.Module):
    def __init__(self, eff):
        super().__init__()
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
        x = self.fc(x)
        x = self.fc2(x)

        return x
        

net = Net(efficientnet)
net.load_state_dict(torch.load('./valorant_models/mouse_model_cont_3.pt'))
optimizer = torch.optim.Adam(net.parameters(), 5e-5)
lossfn = nn.MSELoss()

print("ready")

THRESHOLD = .24

training_mode = False
is_train_pressed = False

current_frame_mouse = []

lastx_total = 0
lasty_total = 0

output = None

leftclick = 0

while True: 
    start_time = time.time()

    msg = wts.MSG()
    pmsg = cts.byref(msg)

    lastx_total = 0
    lasty_total = 0
    leftclick = 0

    while cws.PeekMessage(pmsg, None, 0, 0, PM_REMOVE):
        cws.TranslateMessage(pmsg)
        if msg.message == WM_INPUT:
            
            size = wts.UINT(0)
            res = cws.GetRawInputData(cts.cast(msg.lParam, cws.PRAWINPUT), RID_INPUT, None, cts.byref(size), cts.sizeof(cws.RAWINPUTHEADER))
            
            if res == wts.UINT(-1) or size == 0:
                print("GetRawInputData 0")

            buf = cts.create_string_buffer(size.value)
            res = cws.GetRawInputData(cts.cast(msg.lParam, cws.PRAWINPUT), RID_INPUT, buf, cts.byref(size), cts.sizeof(cws.RAWINPUTHEADER))
            if res != size.value:
                print("GetRawInputData 1")


            ri = cts.cast(buf, cws.PRAWINPUT).contents
            head = ri.header
            
            if head.dwType == RIM_TYPEMOUSE:
                data = ri.data.mouse
                if is_playing:
                    current_frame_mouse.append(data)
                    lasty_total += data.lLastY
                    lastx_total += data.lLastX

                    if data.union.structure.usButtonFlags == 1 and leftclick == 0:
                        leftclick = 1
                    elif data.union.structure.usButtonFlags == 2 and leftclick == 0:
                        leftclick = -1

                #print(data.lLastX, data.lLastY)
            elif head.dwType == RIM_TYPEKEYBOARD:
                data = ri.data.keyboard
                
                # append key and release or press
                if is_playing:
                    pass
                    #current_frame_keyboard_data.append((data.VKey, data.Flags))

                if data.VKey == 0x1B:
                    cws.PostQuitMessage(0)
            elif head.dwType == RIM_TYPEHID:
                data = ri.data.hid
            else:
                print("Wrong raw input type!!!")

    if keyboard.is_pressed('ctrl + t') and not is_train_pressed:
        is_train_pressed = True
        training_mode = True
        print("training_mode: ", training_mode)
        if not training_mode:
            pass
    elif not keyboard.is_pressed('ctrl + t'):
        is_train_pressed = False


    if keyboard.is_pressed('ctrl + m') and not is_play_pressed:
        is_play_pressed = True      
        is_playing = not is_playing
        print("playing: ", is_playing)                              
        if not is_playing:           
            pass                       
    elif not keyboard.is_pressed('ctrl + m'):
        is_play_pressed = False


    if is_playing:
        time_count += 1/FPS
        
        last_img = img
        img = capture_screenshot()
        
        img = img.resize((1920//5, 1080//5))
        img = cv2.resize(np.array(img, dtype=np.float32), (280, 150))/255.0

        img = torch.tensor(img).permute(2, 0, 1).unsqueeze(0)

        #print(lastx_total, lasty_total)

        if training_mode:
            label_mag = math.sqrt(lastx_total**2 + lasty_total**2)

            if label_mag == 0.0:
                label = torch.tensor([leftclick, 0.0, 0.0, 0.0])
            else:
                label = torch.tensor([leftclick, label_mag / mouse_multiplier, lastx_total / label_mag, lasty_total / label_mag])

            loss = lossfn(output, label)
            print(loss, label, output)
            if loss > .35:
                print("training")
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                print("training done")

        
        output = net(img)

        
        move_mouse(int(output[0][2].item()*(output[0][1].item()*mouse_multiplier)), int(output[0][3].item()*(output[0][1].item()*mouse_multiplier)))
        
        if output[0][0] > THRESHOLD:
            press_mouse("left")
        elif output[0][0] < -THRESHOLD:
            release_mouse("left")






    # sleep remaining time to make fps]
    time.sleep(max(0, (1 / FPS) - (time.time() - start_time - 0.0001)))

    fps = 1 / (time.time() - start_time - 0.0001)
    #print("FPS: ", fps, " Is Recording: ", is_recording, end="\r")