import pickle
import time
from mouse_movement import move_mouse
import keyboard


data = pickle.load(open("./data/data0.pkl", 'rb'))
_, mouse = data

is_record_pressed = False
is_recording = False

i = 1

while True:
    if keyboard.is_pressed('ctrl + r') and not is_record_pressed:
        is_record_pressed = True      
        is_recording = not is_recording
                                      
        if not is_recording:           
            pass                                
    
    elif not keyboard.is_pressed('ctrl + r'):
        is_record_pressed = False

    if is_recording:
        move = mouse[i]
        for move in mouse[i]:
            move_mouse(*(move))

        i+=1
        if i >= len(mouse):
            i = 1
    
    time.sleep(1/30)


