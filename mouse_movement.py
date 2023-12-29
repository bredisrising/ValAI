import ctypes as cts
import ctypes_wrappers as cws

poop = cws.INPUT()
poop.type = cws.INPUT_MOUSE
poop.mi.mouseData = 0
poop.mi.time = 0
poop.mi.dx = 100
poop.mi.dy = 100
poop.mi.dwFlags = 0x8000 | 0x0001

def move_mouse_to(x, y):
    poop.mi.dwFlags = 0x8000 | 0x0001
    poop.mi.dx = int(x/1920*65535)
    poop.mi.dy = int(y/1080*65535)
    cws.SendInput(1, cts.byref(poop), cts.sizeof(poop))

def move_mouse(x, y):
    poop.mi.dwFlags = 0x0001
    poop.mi.dx = x
    poop.mi.dy = y
    cws.SendInput(1, cts.byref(poop), cts.sizeof(poop))


if __name__ == "__main__":
    move_mouse(1920//2, 1080//2)

