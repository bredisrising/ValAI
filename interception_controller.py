import interception
import time

def init():
    interception.auto_capture_devices(keyboard=True, mouse=True)

def move_mouse(x, y):
    interception.move_relative(x, y)

def press_key(key):
    interception.key_down(key)

def release_key(key):
    interception.key_up(key)

def press_mouse(button):
    interception.mouse_down(button)

def release_mouse(button):
    interception.mouse_up(button)

def send_mouse(button_state): # button state from rawmouse directly
    stroke = interception.MouseStroke(button_state, interception.MouseFlag.MOUSE_MOVE_ABSOLUTE, 0, 0, 0, 0)
    interception.interception.send_mouse(stroke)
    time.sleep(0.03)

if __name__ == '__main__':
    import time
    init()
    #time.sleep(5)

    # print mouse movemnt
    while True:
        time.sleep(1)
        print(interception.get_mouse())


    # move_relative(500, 300)
    




