import keyboard
import time
from PIL import Image
from mss import mss
import pickle
import ctypes as cts
import ctypes.wintypes as wts

from old_win_recorder import Recorder
import ctypes_wrappers as cws
from old_win_recorder import wnd_proc, register_devices

import pyaudiowpatch as pyaudio

from copy import deepcopy

from spectrogram_collector import SpectroCollector

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
spectrograms = []
reward = []


time_count = 0


save_count = 2 # implement detector to continue


frame_count = 0


wnd_cls = "SO049572093_RawInputWndClass"
wcx = cws.WNDCLASSEX()
wcx.cbSize = cts.sizeof(cws.WNDCLASSEX)

wcx.lpfnWndProc = cws.WNDPROC(wnd_proc)
wcx.hInstance = cws.GetModuleHandle(None)
wcx.lpszClassName = wnd_cls

res = cws.RegisterClassEx(cts.byref(wcx))

hwnd = cws.CreateWindowEx(0, wnd_cls, None, 0, 0, 0, 0, 0, 0, None, wcx.hInstance, None)

print('created window')

register_devices(hwnd)

msg = wts.MSG()
pmsg = cts.byref(msg)

spectro = SpectroCollector()

while True: 
    
    start_time = time.time()

    # reset msg
    msg = wts.MSG()
    pmsg = cts.byref(msg)

    while cws.PeekMessage(pmsg, None, 0, 0, PM_REMOVE):
        print('working')
        cws.TranslateMessage(pmsg)

        if msg.message == WM_INPUT:
            
            size = wts.UINT(0)
            res = cws.GetRawInputData(cts.cast(msg.lParam, cws.PRAWINPUT), RID_INPUT, None, cts.byref(size), cts.sizeof(cws.RAWINPUTHEADER))
            
            if res == wts.UINT(-1) or size == 0:
                print("GetRawInputData 0")
                #return 0
            buf = cts.create_string_buffer(size.value)
            res = cws.GetRawInputData(cts.cast(msg.lParam, cws.PRAWINPUT), RID_INPUT, buf, cts.byref(size), cts.sizeof(cws.RAWINPUTHEADER))
            if res != size.value:
                print("GetRawInputData 1")
                #print_error(text="GetRawInputData 1")
                #return 0

            ri = cts.cast(buf, cws.PRAWINPUT).contents
            head = ri.header
            

            if head.dwType == RIM_TYPEMOUSE:
                data = ri.data.mouse
                if is_recording:
                    current_frame_mouse_data.append(data)
                #print(data.lLastX, data.lLastY)
            elif head.dwType == RIM_TYPEKEYBOARD:
                data = ri.data.keyboard
                
                # append key and release or press
                if is_recording:
                    current_frame_keyboard_data.append((data.VKey, data.Flags))

                if data.VKey == 0x1B:
                    cws.PostQuitMessage(0)
            elif head.dwType == RIM_TYPEHID:
                data = ri.data.hid
            else:
                print("Wrong raw input type!!!")


    if keyboard.is_pressed('ctrl + r') and not is_record_pressed:
        is_record_pressed = True      
        is_recording = not is_recording


        if not is_recording:           
            with open("./val_range_data/data" + str(save_count) + ".pkl", "wb") as f:
                pickle.dump((frames, keyboard_data, mouse_data, cursor_positions, spectrograms), f)
                
                current_frame_keyboard_data.clear()
                current_frame_mouse_data.clear()
                keyboard_data.clear()
                mouse_data.clear() 
                frames.clear()
                cursor_positions.clear()
                reward.clear()
                spectrograms.clear()
                
                time_count = 0  
                save_count += 1                         

        #print("Is Recording: ", is_recording, end="\r")

    elif not keyboard.is_pressed('ctrl + r'):
        is_record_pressed = False



    if is_recording:
        time_count += 1/FPS
             
        
        img = capture_screenshot()
        
        # mss capture screenshot with cursor
        
        img = img.resize((1920//5, 1080//5))
        
        cursor_pos = cws.getCursorPos()
        cursor_positions.append(cursor_pos)

        frames.append(img)
        keyboard_data.append(deepcopy(current_frame_keyboard_data))
        current_frame_keyboard_data.clear()

        mouse_data.append(deepcopy(current_frame_mouse_data))
        current_frame_mouse_data.clear()

        spectrograms.append(spectro.get())

        if time_count > 10*60:
            # have two buffers and then swap them when saving then thread the saving so recording can continue
            with open("./val_range_data/data" + str(save_count) + ".pkl", "wb") as f:
                pickle.dump((frames, keyboard_data, mouse_data, cursor_positions, spectrograms), f)
            

            cursor_positions.clear()
            frames.clear()
            keyboard_data.clear()
            mouse_data.clear()
            reward.clear()
            spectrograms.clear()
            
            save_count += 1
            time_count = 0

        # save image in to lists

        # grab sounds 

        # grab keyboard inputs

        # grab mouse inputs
        
    
    # # sleep remaining time to make fps]
    time.sleep(max(0, (1 / FPS) - (time.time() - start_time - 0.0001)))

    fps = 1 / (time.time() - start_time - 0.0001)
   # print("FPS: ", fps, " Is Recording: ", is_recording, end="\r")
