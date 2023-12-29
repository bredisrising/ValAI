from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
from pynput.keyboard import Key, Controller



class Recorder:
    def __init__(self, keyboard_data_pointer, verbose=False):
        self.keyboard_data = keyboard_data_pointer
        
        self.verbose = verbose
        
        mouse_listener = MouseListener(on_move=self.on_mouse_move, on_click=self.on_mouse_click)
        keyboard_listener = KeyboardListener(on_press=self.on_key_press, on_release=self.on_key_release)
        
        mouse_listener.start()
        keyboard_listener.start()

        

    def on_mouse_move(self, x, y):
        if self.verbose:
            print(f"Mouse moved to ({x}, {y})")


    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            pass
            #print(f"Mouse clicked at ({x}, {y}) with {button}")

    def on_key_press(self, key):
        self.keyboard_data.append(key)
        try:
            pass
            #print(f"Key pressed: {key.char}")
        except AttributeError:
            pass
            #print(f"Special key pressed: {key}")

    def on_key_release(self, key):
        self.keyboard_data.append(key)
        try:
            pass
            #print(f"Key released: {key.char}")
        except AttributeError:
            pass
            #print(f"Special key released: {key}")


if __name__ == "__main__":
    keyboard_data = []
    recorder = Recorder(keyboard_data, False)
    while True:
        pass