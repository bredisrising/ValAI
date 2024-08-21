import pickle
import time
import keyboard

import sys
import os
sys.path.append(os.path.abspath('./'))
print(sys.path)

from interception_controller import move_mouse




data = pickle.load(open("./val_range_data/save2.pkl", 'rb'))
frames, keyboard_events, mouse_events, mouse_movements = data

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
        move = mouse_movements[i]
        #key = keys[i]
        #print(mouse_movements[i])

            #print(data)
        dx = move[0]
        dy = move[1]

        move_mouse(dx, dy)
            #mouse_key(data.union.structure.usButtonFlags)


        # for key in keys[i]:
        #     #print(key)
        #     if key[1] == 1:
        #         release_key(key[0])
        #     elif key[1] == 0:
        #         press_key(key[0])

        i+=1
        if i >= len(mouse_movements):
            i = 1
    
    time.sleep(1/20)


