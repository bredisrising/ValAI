import ctypes
import ctypes.wintypes as wintypes

user32 = ctypes.WinDLL("User32")
kernel32 = ctypes.WinDLL("Kernel32")

register_class = user32["RegisterClassExW"]
def_window_proc = user32["DefWindowProcW"]
get_module_handle = kernel32["GetModuleHandleW"]


peek_message = user32["PeekMessageW"]
peek_message.argtypes = (wintypes.PMSG, wintypes.HWND, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint)
peek_message.restype = ctypes.c_bool

create_window = user32["CreateWindowExW"]
create_window.argtypes = (wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID)
create_window.restype = wintypes.HWND

WNDPROC_ARGTYPES = (wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
WNDPROC_TYPE = ctypes.CFUNCTYPE(ctypes.c_ssize_t, *WNDPROC_ARGTYPES)



def wndproc(hwnd, msg, wparam, lparam):
    print('lParam: ', lparam)
    return def_window_proc(hwnd, msg, wparam, lparam)


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

# TEST
if __name__ == "__main__":
    window_class_name = "RawInputCollector"
    window_class = WNDCLASSEXW()
    window_class.cbSize = ctypes.sizeof(WNDCLASSEXW)
    window_class.lpfnWndProc = WNDPROC_TYPE(wndproc)
    window_class.lpszClassName = window_class_name
    window_class.hInstance = get_module_handle(None)

    res = register_class(ctypes.byref(window_class))

    print('creating window')
    hwnd = create_window(0, window_class_name, None, 0, 0, 0, 0, 0, 0, None, window_class.hInstance, None)
    print('created window', hwnd)


    msg = wintypes.MSG()
    msg_pointer = ctypes.byref(msg)

    # register devices 

    print('starting i think')

    while True:
        result = peek_message(msg_pointer, None, 0, 0, 1)
        if result == True:
            print("ITS WORKING!")