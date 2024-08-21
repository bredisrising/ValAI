from winapi_functions import * 
from mss import mss
from PIL import Image
import pickle
import time
from input_map import vk_to_unicode
import matplotlib.pyplot as plt
import dxcam
import warnings
import cv2 
import numpy as np
import keyboard
from copy import deepcopy
from win11toast import notify
import os



FPS = 20
SCALE_DOWN = 10

SHOW_SCREEN_CAPTURE = False


def capture_screenshot():
    with mss(with_cursor=True) as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        return Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

def win_input_recorder(msg_pointer, frame_mouse_movement: list, frame_mouse_events: list, frame_keyboard_events: list):
    while peek_message(msg_pointer, None, 0, 0, 1):
        msg = msg_pointer.contents
        if msg.message == 0x00FF:
            size = wintypes.UINT(0)
            get_raw_input_data(ctypes.cast(msg.lParam, PRAWINPUT), 0x10000003, None, ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER))

            buffer = ctypes.create_string_buffer(size.value)
            get_raw_input_data(ctypes.cast(msg.lParam, PRAWINPUT), 0x10000003, buffer, ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER))

            rawinput = ctypes.cast(buffer, PRAWINPUT).contents

            if rawinput.header.dwType == 0: # MOUSE
                mouse = rawinput.data.mouse
                frame_mouse_movement[0] += mouse.lLastX
                frame_mouse_movement[1] += mouse.lLastY

                frame_mouse_events.append(mouse.DUMMYUNIONNAME.DUMMYSTRUCTNAME.usButtonFlags)
            
            if rawinput.header.dwType == 1: # KEYBOARD
                keyboard = rawinput.data.keyboard
                frame_keyboard_events.append((keyboard.VKey, keyboard.Flags))

                #print(vk_to_unicode[keyboard.VKey], keyboard.Flags)


def recorder_loop(screen_capture: dxcam.DXCamera, cv_window=None):
    msg = wintypes.MSG()
    msg_pointer = ctypes.pointer(msg)

    is_recording = False
    is_record_button_pressed = False

    keyboard_events = []
    mouse_movements = []
    mouse_events = []
    frames = []

    frames_passed = 0


    lenfiles = 0
    for roots, dirs, files in os.walk('./val_range_data/'):
        lenfiles = len(files)

    current_save_number = lenfiles + 1

    while True:
        if keyboard.is_pressed('ctrl + r') and not is_record_button_pressed:
            is_record_button_pressed = True
            is_recording = not is_recording

            if is_recording:
                notify('STARTED RECORDING!')
            else:
                notify('STOPPED RECORDING!')

                # SAVE
                with open("./val_range_data/save" + str(current_save_number) + '.pkl', 'wb') as f:
                    pickle.dump((frames, keyboard_events, mouse_events, mouse_movements), f)
                    current_save_number += 1
            
                keyboard_events.clear()
                mouse_movements.clear()
                mouse_events.clear()
                frames.clear()

                frame_keyboard_events.clear()
                frame_mouse_events.clear()
                frame_mouse_movement = [0, 0]

                frames_passed = 0

        elif not keyboard.is_pressed('ctrl + r'):
            is_record_button_pressed = False



        start_time = time.perf_counter()

        frame_mouse_movement = [0, 0] # x, y 
        frame_keyboard_events = []
        frame_mouse_events = []        

        if is_recording:
            win_input_recorder(msg_pointer, frame_mouse_movement, frame_mouse_events, frame_keyboard_events)
            screenshot = screen_capture.get_latest_frame()
            frame = cv2.resize(screenshot, (1920//5, 1080//5))
            
            frames.append(frame)
            keyboard_events.append(frame_keyboard_events)
            # not clear() (this is like reassigning the pointer) that way no copying is needed
            frame_keyboard_events = [] 
            

            mouse_events.append(frame_mouse_events)
            frame_mouse_events = []

            mouse_movements.append(frame_mouse_movement)
            frame_mouse_movement = [0, 0]

            frames_passed += 1


            if frames_passed > 3000: # equivalent to 2.5 minutes at 20 fps
                notify('SAVED!')
                with open("./val_range_data/save" + str(current_save_number) + '.pkl', 'wb') as f:
                    pickle.dump((frames, keyboard_events, mouse_events, mouse_movements), f)
                    current_save_number += 1

                
                keyboard_events.clear()
                mouse_movements.clear()
                mouse_events.clear()
                frames.clear()

                frame_keyboard_events.clear()
                frame_mouse_events.clear()
                frame_mouse_movement = [0, 0]

                frames_passed = 0


        # REACH TARGET FPS - (not needed as screen capture can handle)
        
        if not is_recording:
            end_time = time.perf_counter()
            amount_time_to_wait = (1/FPS) - (end_time - start_time)
            if amount_time_to_wait > 0:
                time.sleep(amount_time_to_wait)

        end_time = time.perf_counter()
        print((1 / (end_time - start_time)), end="\r") # SHOULD BE AROUND FPS


if __name__ == "__main__":
    print("\033[31m","MAKE SURE THE TERMINAL THIS SCRIPT IS RUNNING IN IS IN THE MONITOR TO CAPTURE!!!", "\n\033[0m")

    # everything needs to run on single thread to ENSURE FRAMES and INPUT ARE SYNCED
    initialize_input_recorder_window()

    # MAKE SURE TO RUN THE TERMINAL WHICH IS RUNNING THE SCRIPT IN THE MONITOR TO CAPTURE!!! idk why 
    screen_capture = dxcam.create(output_idx = 0) 
    screen_capture.start(target_fps=FPS)

    print(dxcam.device_info(), dxcam.output_info())
    
    recorder_loop(screen_capture)
    
    print('done')
    screen_capture.stop()
