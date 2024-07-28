import ctypes as cts
import ctypes_wrappers as cws
import time


mouse = cws.INPUT()
mouse.type = cws.INPUT_MOUSE
mouse.u.mi.mouseData = 0
mouse.u.mi.time = 0
mouse.u.mi.dx = 100
mouse.u.mi.dy = 100
mouse.u.mi.dwFlags = 0x8000 | 0x0001

def map_RAWMOUSE_code_to_MOUSEINPUT(code):
    if code == 0x0001: # left down
        return 0x0002
    elif code == 0x0002: # left up
        return 0x0004
    elif code == 0x0004: # right down
        return 0x0008
    elif code == 0x0008: # right up
        return 0x0010
    elif code == 0x0010: # middle down
        return 0x0020
    elif code == 0x0020: # middle up
        return 0x0040
    elif code == 0x0040 or code == 0x0100: # x down
        return 0x0080
    elif code == 0x0080 or code == 0x200: # x up
        return 0x0100
    elif code == 0x0400: # 5 down
        return 0x0800
    

def mouse_key(code):
    if code == 0: return
    
    newcode = map_RAWMOUSE_code_to_MOUSEINPUT(code)

    if code == 0x0040 or code == 0x0100: # x down
        mouse.u.mi.mouseData = 0x0001
    elif code == 0x0080 or code == 0x200: # x up
        mouse.u.mi.mouseData = 0x0002
    

    mouse.u.mi.dwFlags = newcode
    return cws.SendInput(1, cts.byref(mouse), cts.sizeof(mouse))



def move_mouse_to(x, y):
    mouse.u.mi.dwFlags = 0x8000 | 0x0001
    mouse.u.mi.dx = int(x/1920*65535)
    mouse.u.mi.dy = int(y/1080*65535)
    return cws.SendInput(1, cts.byref(mouse), cts.sizeof(mouse))

def move_mouse(x, y):
    mouse.u.mi.dwFlags = 0x0001
    mouse.u.mi.dx = x
    mouse.u.mi.dy = y
    return cws.SendInput(1, cts.byref(mouse), cts.sizeof(mouse))


keyboard = cws.INPUT()
keyboard.type = cws.INPUT_KEYBOARD
keyboard.u.ki.time = 0
keyboard.u.ki.wScan = 0


def press_and_release_key(keyCode):
    press_key(keyCode)
    release_key(keyCode)

def press_key(keyCode):
    keyboard.u.ki.dwFlags = 0x0008
    keyboard.u.ki.wScan = cws.MapVirtualKeyA(keyCode, 0)
    return cws.SendInput(1, cts.byref(keyboard), cts.sizeof(keyboard))


def release_key(keyCode):
    keyboard.u.ki.dwFlags = 0x0008 | 0x0002
    keyboard.u.ki.wScan = cws.MapVirtualKeyA(keyCode, 0)
    return cws.SendInput(1, cts.byref(keyboard), cts.sizeof(keyboard))



if __name__ == "__main__":
    press_and_release_key(0x45)

