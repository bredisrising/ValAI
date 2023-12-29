import keyboard
import time
from PIL import Image
from mss import mss
import pickle
import ctypes as cts
import ctypes.wintypes as wts
#from record_input import Recorder

from winrecorder import Recorder
import ctypes_wrappers as cws
from winrecorder import wnd_proc, register_devices

from copy import deepcopy

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
    with mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        return Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

FPS = 30
SCALE_DOWN = 4

is_recording = False
is_record_pressed = False

data = []

keyboard_data = []
current_frame_keyboard_data = []
mouse_data = []
current_frame_mouse_data = []


time_count = 0
save_count = 0
frame_count = 0


recorder = Recorder(current_frame_keyboard_data, current_frame_mouse_data)


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


while True: 
    # reset msg
    msg = wts.MSG()
    pmsg = cts.byref(msg)

    while cws.PeekMessage(pmsg, None, 0, 0, PM_REMOVE):
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
                current_frame_mouse_data.append((data.lLastX, data.lLastY))
                #print(data.lLastX, data.lLastY)
            elif head.dwType == RIM_TYPEKEYBOARD:
                data = ri.data.keyboard

                # append key and release or press
                current_frame_keyboard_data.append((data.VKey))

                if data.VKey == 0x1B:
                    cws.PostQuitMessage(0)
            elif head.dwType == RIM_TYPEHID:
                data = ri.data.hid
            else:
                print("Wrong raw input type!!!")


    time_count += 1/FPS
    start_time = time.time()

    if keyboard.is_pressed('ctrl + r') and not is_record_pressed:
        is_record_pressed = True      
        is_recording = not is_recording
                                      
        if not is_recording:           
            pass                                
    
    elif not keyboard.is_pressed('ctrl + r'):
        is_record_pressed = False


    if is_recording:
        #img = capture_screenshot()
        #img = img.resize((1920//SCALE_DOWN, 1080//SCALE_DOWN))
        

        #data.append(img)
        keyboard_data.append(deepcopy(current_frame_keyboard_data))
        current_frame_keyboard_data.clear()

        mouse_data.append(deepcopy(current_frame_mouse_data))
        current_frame_mouse_data.clear()

        if time_count > 15:
            # have two buffers and then swap them when saving then thread the saving so recording can continue
            with open("./data/data" + str(save_count) + ".pkl", "wb") as f:
                pickle.dump((keyboard_data, mouse_data), f)
            
            #data.clear()
            keyboard_data.clear()
            mouse_data.clear()
            
            save_count += 1
            time_count = 0

        # save image in to lists

        # grab sounds 

        # grab keyboard inputs

        # grab mouse inputs
        
    
    # sleep remaining time to make fps]
    time.sleep(max(0, (1 / FPS) - (time.time() - start_time - 0.0001)))

    fps = 1 / (time.time() - start_time - 0.0001)
    print("FPS: ", fps, " Is Recording: ", is_recording, end="\r")
