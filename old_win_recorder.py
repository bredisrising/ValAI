import ctypes as cts
import ctypes.wintypes as wts
import sys
import time
from copy import deepcopy

import ctypes_wrappers as cws

HWND_MESSAGE = -3

WM_QUIT = 0x0012
WM_INPUT = 0x00FF
WM_KEYUP = 0x0101
WM_CHAR = 0x0102

HID_USAGE_PAGE_GENERIC = 0x01

RIDEV_NOLEGACY = 0x00000030
RIDEV_INPUTSINK = 0x00000100
RIDEV_CAPTUREMOUSE = 0x00000200

RID_HEADER = 0x10000005
RID_INPUT = 0x10000003

RIM_TYPEMOUSE = 0
RIM_TYPEKEYBOARD = 1
RIM_TYPEHID = 2

PM_NOREMOVE = 0x0000

def print_error(code=None, text=None):
    text = text + " - e" if text else "E"
    code = cws.GetLastError() if code is None else code
    print(f"{text}rror code: {code}")

def register_devices(hwnd=None):
    flags = RIDEV_INPUTSINK  # @TODO - cfati: If setting to 0, GetMessage hangs
    generic_usage_ids = (0x01, 0x02, 0x04, 0x05, 0x06, 0x07, 0x08)
    devices = (cws.RawInputDevice * len(generic_usage_ids))(
        *(cws.RawInputDevice(HID_USAGE_PAGE_GENERIC, uid, flags, hwnd) for uid in generic_usage_ids)
    )
    
    if cws.RegisterRawInputDevices(devices, len(generic_usage_ids), cts.sizeof(cws.RawInputDevice)):
        print("Successfully registered input device(s)!")
        return True
    else:
        print_error(text="RegisterRawInputDevices")
        return False

class Recorder:
    def __init__(self, keyboard, mouse):
        self.keyboarddata = keyboard
        self.mousedata = mouse
       
        wnd_cls = "SO049572093_RawInputWndClass"
        wcx = cws.WNDCLASSEX()
        wcx.cbSize = cts.sizeof(cws.WNDCLASSEX)

        wcx.lpfnWndProc = cws.WNDPROC(self.wnd_proc)
        wcx.hInstance = cws.GetModuleHandle(None)
        wcx.lpszClassName = wnd_cls
       
        res = cws.RegisterClassEx(cts.byref(wcx))
        if not res:
            print_error(text="RegisterClass")
            return 0
        hwnd = cws.CreateWindowEx(0, wnd_cls, None, 0, 0, 0, 0, 0, 0, None, wcx.hInstance, None)
        if not hwnd:
            print_error(text="CreateWindowEx")
            return 0
        
        if not register_devices(hwnd):
            return 0
        self.msg = wts.MSG()
        self.pmsg = cts.byref(self.msg)
        # while res := cws.GetMessage(self.pmsg, None, 0, 0):
        #     if res < 0:
        #         print_error(text="GetMessage")
        #         break
        #     cws.TranslateMessage(self.pmsg)
        #     cws.DispatchMessage(self.pmsg)
    
    def next(self):
        
        while res := cws.GetMessage(self.pmsg, None, 0, 0):
            if res < 0:
                print_error(text="GetMessage")
                break
            cws.TranslateMessage(self.pmsg)
            cws.DispatchMessage(self.pmsg)

        #cws.GetMessage(self.pmsg, None, 0, 0)

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        print(f"Handle message - hwnd: 0x{hwnd:016X} msg: 0x{msg:08X} wp: 0x{wparam:016X} lp: 0x{lparam:016X}")
        if msg == WM_INPUT:
            size = wts.UINT(0)
            res = cws.GetRawInputData(cts.cast(lparam, cws.PRAWINPUT), RID_INPUT, None, cts.byref(size), cts.sizeof(cws.RAWINPUTHEADER))
            if res == wts.UINT(-1) or size == 0:
                print_error(text="GetRawInputData 0")
                return 0
            buf = cts.create_string_buffer(size.value)
            res = cws.GetRawInputData(cts.cast(lparam, cws.PRAWINPUT), RID_INPUT, buf, cts.byref(size), cts.sizeof(cws.RAWINPUTHEADER))
            if res != size.value:
                print_error(text="GetRawInputData 1")
                return 0

            ri = cts.cast(buf, cws.PRAWINPUT).contents

            head = ri.header
            print(head.to_string())

            if head.dwType == RIM_TYPEMOUSE:
                data = ri.data.mouse
                self.mousedata.append((data.lLastX, data.lLastY))
            elif head.dwType == RIM_TYPEKEYBOARD:
                data = ri.data.keyboard

                # append key and release or press
                self.keyboarddata.append((data.VKey))

                if data.VKey == 0x1B:
                    cws.PostQuitMessage(0)
            elif head.dwType == RIM_TYPEHID:
                data = ri.data.hid
            else:
                print("Wrong raw input type!!!")
                return 0
            
        return cws.DefWindowProc(hwnd, msg, wparam, lparam)


def wnd_proc(hwnd, msg, wparam, lparam):
    print(f"Handle message - hwnd: 0x{hwnd:016X} msg: 0x{msg:08X} wp: 0x{wparam:016X} lp: 0x{lparam:016X}")
    if msg == WM_INPUT:
        size = wts.UINT(0)
        res = cws.GetRawInputData(cts.cast(lparam, cws.PRAWINPUT), RID_INPUT, None, cts.byref(size), cts.sizeof(cws.RAWINPUTHEADER))
        
        if res == wts.UINT(-1) or size == 0:
            print_error(text="GetRawInputData 0")
            return 0
        buf = cts.create_string_buffer(size.value)
        res = cws.GetRawInputData(cts.cast(lparam, cws.PRAWINPUT), RID_INPUT, buf, cts.byref(size), cts.sizeof(cws.RAWINPUTHEADER))
        if res != size.value:
            print_error(text="GetRawInputData 1")
            return 0

        ri = cts.cast(buf, cws.PRAWINPUT).contents

        head = ri.header
        #print(head.to_string())

        if head.dwType == RIM_TYPEMOUSE:
            data = ri.data.mouse
        elif head.dwType == RIM_TYPEKEYBOARD:
            data = ri.data.keyboard
            if data.VKey == 0x1B:
                cws.PostQuitMessage(0)
        elif head.dwType == RIM_TYPEHID:
            data = ri.data.hid
        else:
            print("Wrong raw input type!!!")
            return 0
        #print(data.to_string())

        #print(data.lLastX, data.lLastY)

        #print(data)

    return cws.DefWindowProc(hwnd, msg, wparam, lparam)




def main(*argv):
    wnd_cls = "SO049572093_RawInputWndClass"
    wcx = cws.WNDCLASSEX()
    wcx.cbSize = cts.sizeof(cws.WNDCLASSEX)
   
    wcx.lpfnWndProc = cws.WNDPROC(wnd_proc)
    wcx.hInstance = cws.GetModuleHandle(None)
    wcx.lpszClassName = wnd_cls

    res = cws.RegisterClassEx(cts.byref(wcx))
    if not res:
        print_error(text="RegisterClass")
        return 0
    hwnd = cws.CreateWindowEx(0, wnd_cls, None, 0, 0, 0, 0, 0, 0, None, wcx.hInstance, None)
    if not hwnd:
        print_error(text="CreateWindowEx")
        return 0
    
    if not register_devices(hwnd):
        return 0
    msg = wts.MSG()
    pmsg = cts.byref(msg)
    print("Start loop (press <ESC> to exit)...")
    
    while res := cws.GetMessage(pmsg, None, 0, 0):
        if res < 0:
            print_error(text="GetMessage")
            break
        cws.TranslateMessage(pmsg)
        cws.DispatchMessage(pmsg)


if __name__ == "__main__":
    # print("Python {:s} {:03d}bit on {:s}\n".format(" ".join(elem.strip() for elem in sys.version.split("\n")),
    #                                                 64 if sys.maxsize > 0x100000000 else 32, sys.platform))
    rc = main(*sys.argv[1:])
    print("\nDone.\n")
    sys.exit(rc)