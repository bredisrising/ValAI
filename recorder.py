from winapi_functions import * 
import mss
from PIL import Image
import pickle

FPS = 20
SCALE_DOWN = 10




def capture_screenshot():
    with mss(with_cursor=True) as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        return Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')



def start_main_recorder_loop():
    msg = wintypes.MSG()
    msg_pointer = ctypes.byref(msg)

    while True:
        while peek_message(msg_pointer, None, 0, 0, 1):
            if msg.message == 0x00FF:
                print('PLACEHOLDER - handle message')

        # call other recording!



if __name__ == "__main__":
    # everything needs to run on single thread to ENSURE FRAMES and INPUT ARE SYNCED
    initialize_input_recorder_window()
    #print(window_class)
    start_main_recorder_loop()