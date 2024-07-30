from winapi_functions import * 
from mss import mss
from PIL import Image
import pickle
import time
from input_map import vk_to_unicode
import matplotlib.pyplot as plt
import dxcam
import cv2


FPS = 20
SCALE_DOWN = 10

SHOW_SCREEN_CAPTURE = True



def capture_screenshot():
    with mss(with_cursor=True) as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        return Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

def recorder_loop(camera: dxcam.DXCamera, cv_window=None):
    msg = wintypes.MSG()
    msg_pointer = ctypes.byref(msg)
    cv_window = cv2.namedWindow('CV Screen Capture', cv2.WINDOW_NORMAL)
    while True:

        start_time = time.perf_counter()

        frame_mouse_movement = [0, 0] # x, y 
        frame_keyboard_events = []
        frame_mouse_events = []
        
    
        while peek_message(msg_pointer, None, 0, 0, 1):
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

                    #print(mouse.DUMMYUNIONNAME.DUMMYSTRUCTNAME.usButtonFlags)
                
                if rawinput.header.dwType == 1: # KEYBOARD
                    keyboard = rawinput.data.keyboard

                    #print(vk_to_unicode[keyboard.VKey], keyboard.Flags)

        screenshot = camera.get_latest_frame()
        print('helo world!')
        if cv_window != None:
            cv2.imshow('CV Screen Capture', screenshot)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        


        # REACH TARGET FPS - (not needed as screen capture can handle)
        # end_time = time.perf_counter()

        # amount_time_to_wait = (1/FPS) - (end_time - start_time)
        # if amount_time_to_wait > 0:
        #     time.sleep(amount_time_to_wait)


        end_time = time.perf_counter()
        print((1 / (end_time - start_time))) # SHOULD BE AROUND FPS


if __name__ == "__main__":
    # everything needs to run on single thread to ENSURE FRAMES and INPUT ARE SYNCED

    initialize_input_recorder_window()

    screen_capture = dxcam.create()
    screen_capture.start(target_fps=30)

    # if SHOW_SCREEN_CAPTURE:
    #     cv_window = cv2.namedWindow('CV Screen Capture', cv2.WINDOW_NORMAL)
    # else:
    #     cv_window = None
    
    recorder_loop(screen_capture)
    
    print('done')
    screen_capture.stop()

    cv2.destroyAllWindows()