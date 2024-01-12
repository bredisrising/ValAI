import pickle
import time
from input_control import move_mouse, release_key, press_key, mouse_key
import keyboard


data = pickle.load(open("./data/data0.pkl", 'rb'))
keys, mouse = data

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
        key = keys[i]
        
        for data in mouse[i]:

            dx = data.lLastX
            dy = data.lLastY

            move_mouse(dx, dy)
            mouse_key(data.union.structure.usButtonFlags)


        for key in keys[i]:
            #print(key)
            if key[1] == 1:
                release_key(key[0])
            elif key[1] == 0:
                press_key(key[0])

        i+=1
        if i >= len(mouse):
            i = 1
    
    time.sleep(1/30)


