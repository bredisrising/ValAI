import ctypes
import ctypes.wintypes as wintypes
import threading

# TYPEDEFS

RIDEV_INPUTSINK = 0x00000100 # flag to let caller receive input even if its not in foreground

user32 = ctypes.WinDLL("User32")
kernel32 = ctypes.WinDLL("Kernel32")

register_class = user32["RegisterClassExW"]

get_module_handle = kernel32["GetModuleHandleW"]
register_raw_input_devices = user32["RegisterRawInputDevices"]

def_window_proc = user32["DefWindowProcW"]
def_window_proc.argtypes = (wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
def_window_proc.restype = ctypes.c_ssize_t

peek_message = user32["PeekMessageW"]
peek_message.argtypes = (wintypes.PMSG, wintypes.HWND, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint)
peek_message.restype = ctypes.c_bool

dispatch_message = user32["DispatchMessageW"]

create_window = user32["CreateWindowExW"]
create_window.argtypes = (wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID)
create_window.restype = wintypes.HWND

WNDPROC_ARGTYPES = (wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
WNDPROC_TYPE = ctypes.CFUNCTYPE(ctypes.c_ssize_t, *WNDPROC_ARGTYPES)

class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = (
        ('usUsagePage', wintypes.USHORT),
        ('usUsage', wintypes.USHORT),
        ('dwFlags', wintypes.DWORD),
        ('hwndTarget', wintypes.HWND)
    )

class WNDCLASSEXW(ctypes.Structure):
    _fields_ = (
        ('cbSize', ctypes.c_uint),
        ('style', ctypes.c_uint),
        ('lpfnWndProc', WNDPROC_TYPE),
        ('cbClsExtra', ctypes.c_int),
        ('cbWndExtra', ctypes.c_int),
        ('hInstance', wintypes.HINSTANCE),
        ('hIcon', ctypes.c_void_p),
        ('hCursor', ctypes.c_void_p),
        ('hbrBackground', ctypes.c_void_p),
        ('lpszMenuName', wintypes.LPCWSTR),
        ('lpszClassName', wintypes.LPCWSTR),
        ("hIconSm", ctypes.c_void_p)
    )

def wndproc(hwnd, msg, wparam, lparam):
    return def_window_proc(hwnd, msg, wparam, lparam)


def initialize_input_recorder_window():
    window_class_name = "RawInputCollector"
    window_class = WNDCLASSEXW()
    window_class.cbSize = ctypes.sizeof(WNDCLASSEXW)
    window_class.lpfnWndProc = WNDPROC_TYPE(wndproc)
    window_class.lpszClassName = window_class_name
    window_class.hInstance = get_module_handle(None)

    res = register_class(ctypes.byref(window_class))
    assert res > 0, "FAILED TO REGISTER CLASS!"
            
    hwnd = create_window(0, window_class_name, None, 0, 0, 0, 0, 0, 0, None, window_class.hInstance, None)
    assert hwnd != None, "FAILED TO CREATE WINDOW!"

    # register devices
    RAWINPUT_KEYBOARD = RAWINPUTDEVICE()
    RAWINPUT_KEYBOARD.usUsagePage = 0x01
    RAWINPUT_KEYBOARD.usUsage = 0x06
    RAWINPUT_KEYBOARD.dwFlags = RIDEV_INPUTSINK
    RAWINPUT_KEYBOARD.hwndTarget = hwnd

    RAWINPUT_MOUSE = RAWINPUTDEVICE()
    RAWINPUT_MOUSE.usUsagePage = 0x01
    RAWINPUT_MOUSE.usUsage = 0x02 
    RAWINPUT_MOUSE.dwFlags = RIDEV_INPUTSINK
    RAWINPUT_MOUSE.hwndTarget = hwnd
    
    RAWINPUTS = (RAWINPUTDEVICE * 2)(RAWINPUT_KEYBOARD, RAWINPUT_MOUSE)

    assert register_raw_input_devices(RAWINPUTS, 2, ctypes.sizeof(RAWINPUTDEVICE)) == True, "FAILED TO REGISTER INPUT DEVICES!"

    print('Recorder Initialized!')

    return window_class



