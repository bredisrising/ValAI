
import ctypes as cts
import ctypes.wintypes as wts


HCURSOR = cts.c_void_p
LRESULT = cts.c_ssize_t

wndproc_args = (wts.HWND, wts.UINT, wts.WPARAM, wts.LPARAM)

WNDPROC = cts.CFUNCTYPE(LRESULT, *wndproc_args)

kernel32 = cts.WinDLL("Kernel32")
user32 = cts.WinDLL("User32")

def structure_to_string_method(self):
    ret = [f"{self.__class__.__name__} (size: {cts.sizeof(self.__class__)}) instance at 0x{id(self):016X}:"]
    for fn, _ in self._fields_:
        ret.append(f"  {fn}: {getattr(self, fn)}")
    return "\n".join(ret) + "\n"

union_to_string_method = structure_to_string_method


class Struct(cts.Structure):
    to_string = structure_to_string_method


class Uni(cts.Union):
    to_string = union_to_string_method


class WNDCLASSEXW(Struct):
    _fields_ = (
        ("cbSize", wts.UINT),
        ("style", wts.UINT),
        #("lpfnWndProc", cts.c_void_p),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", cts.c_int),
        ("cbWndExtra", cts.c_int),
        ("hInstance", wts.HINSTANCE),
        ("hIcon", wts.HICON),
        ("hCursor", HCURSOR),
        ("hbrBackground", wts.HBRUSH),
        ("lpszMenuName", wts.LPCWSTR),
        ("lpszClassName", wts.LPCWSTR),
        ("hIconSm", wts.HICON),
    )

WNDCLASSEX = WNDCLASSEXW


class RawInputDevice(Struct):
    _fields_ = (
        ("usUsagePage", wts.USHORT),
        ("usUsage", wts.USHORT),
        ("dwFlags", wts.DWORD),
        ("hwndTarget", wts.HWND),
    )

PRawInputDevice = cts.POINTER(RawInputDevice)


class RAWINPUTHEADER(Struct):
    _fields_ = (
        ("dwType", wts.DWORD),
        ("dwSize", wts.DWORD),
        ("hDevice", wts.HANDLE),
        ("wParam", wts.WPARAM),
    )

class MOUSE_FLAGS(Struct):
    _fields_ = (
        ("usButtonFlags", wts.USHORT),
        ("usButtonData", wts.USHORT),
    )

class MOUSE_ONION(Uni):
    _fields_ = (
        ("ulButtons", wts.ULONG),
        ("structure", MOUSE_FLAGS),
    )

class RAWMOUSE(Struct):
    _fields_ = (
        ("usFlags", wts.USHORT),
        ("union", MOUSE_ONION),  
        ("ulRawButtons", wts.ULONG),
        ("lLastX", wts.LONG),
        ("lLastY", wts.LONG),
        ("ulExtraInformation", wts.ULONG),
    )


class RAWKEYBOARD(Struct):
    _fields_ = (
        ("MakeCode", wts.USHORT),
        ("Flags", wts.USHORT),
        ("Reserved", wts.USHORT),
        ("VKey", wts.USHORT),
        ("Message", wts.UINT),
        ("ExtraInformation", wts.ULONG),
    )


class RAWHID(Struct):
    _fields_ = (
        ("dwSizeHid", wts.DWORD),
        ("dwCount", wts.DWORD),
        ("bRawData", wts.BYTE * 1),  # @TODO - cfati: https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-rawhid, but not very usable via CTypes
    )


class RAWINPUT_U0(Uni):
    _fields_ = (
        ("mouse", RAWMOUSE),
        ("keyboard", RAWKEYBOARD),
        ("hid", RAWHID),
    )


class RAWINPUT(Struct):
    _fields_ = (
        ("header", RAWINPUTHEADER),
        ("data", RAWINPUT_U0),
    )

class MOUSEINPUT(Struct):
    _fields_ = (
        ("dx", wts.LONG),
        ("dy", wts.LONG),
        ("mouseData", wts.DWORD),
        ("dwFlags", wts.DWORD),
        ("time", wts.DWORD),
        ("dwExtraInfo", cts.POINTER(wts.ULONG)),
    )

class KEYBDINPUT(Struct):
    _fields_ = (
        ("wVk", wts.WORD),
        ("wScan", wts.WORD),
        ("dwFlags", wts.DWORD),
        ("time", wts.DWORD),
        ("dwExtraInfo", cts.POINTER(wts.ULONG)),
    )

class Onion(Uni):
    _fields_ = (
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT)
    )

class INPUT(Struct):
    _fields_ = (
        ("type", wts.DWORD),
        ("u", Onion)
    )

class POINT(Struct):
    _fields_ = (
        ("x", wts.LONG),
        ("y", wts.LONG),
    )


def getCursorPos():
    pt = POINT()
    GetCursorPos(cts.byref(pt))
    return pt.x, pt.y


PINPUT = cts.POINTER(INPUT)

PRAWINPUT = cts.POINTER(RAWINPUT)

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

GetLastError = kernel32.GetLastError
GetLastError.argtypes = ()
GetLastError.restype = wts.DWORD

GetModuleHandle = kernel32.GetModuleHandleW
GetModuleHandle.argtypes = (wts.LPWSTR,)
GetModuleHandle.restype = wts.HMODULE


DefWindowProc = user32.DefWindowProcW
DefWindowProc.argtypes = wndproc_args
DefWindowProc.restype = LRESULT

RegisterClassEx = user32.RegisterClassExW
RegisterClassEx.argtypes = (cts.POINTER(WNDCLASSEX),)
RegisterClassEx.restype = wts.ATOM

CreateWindowEx = user32.CreateWindowExW
CreateWindowEx.argtypes = (wts.DWORD, wts.LPCWSTR, wts.LPCWSTR, wts.DWORD, cts.c_int, cts.c_int, cts.c_int, cts.c_int, wts.HWND, wts.HMENU, wts.HINSTANCE, wts.LPVOID)
CreateWindowEx.restype = wts.HWND

RegisterRawInputDevices = user32.RegisterRawInputDevices
RegisterRawInputDevices.argtypes = (PRawInputDevice, wts.UINT, wts.UINT)
RegisterRawInputDevices.restype = wts.BOOL

GetRawInputData = user32.GetRawInputData
GetRawInputData.argtypes = (PRAWINPUT, wts.UINT, wts.LPVOID, wts.PUINT, wts.UINT)
GetRawInputData.restype = wts.UINT

GetMessage = user32.GetMessageW
GetMessage.argtypes = (wts.LPMSG, wts.HWND, wts.UINT, wts.UINT)
GetMessage.restype = wts.BOOL

PeekMessage = user32.PeekMessageW
PeekMessage.argtypes = (wts.LPMSG, wts.HWND, wts.UINT, wts.UINT, wts.UINT)
PeekMessage.restype = wts.BOOL

TranslateMessage = user32.TranslateMessage
TranslateMessage.argtypes = (wts.LPMSG,)
TranslateMessage.restype = wts.BOOL

DispatchMessage = user32.DispatchMessageW
DispatchMessage.argtypes = (wts.LPMSG,)
DispatchMessage.restype = LRESULT

PostQuitMessage = user32.PostQuitMessage
PostQuitMessage.argtypes = (cts.c_int,)
PostQuitMessage.restype = None

SendInput = user32.SendInput
SendInput.argtypes = (wts.UINT, PINPUT, cts.c_int)
SendInput.restype = wts.UINT

MapVirtualKeyA = user32.MapVirtualKeyA
MapVirtualKeyA.argtypes = (wts.UINT, wts.UINT)
MapVirtualKeyA.restype = wts.UINT

GetCursorPos = user32.GetCursorPos
GetCursorPos.argtypes = (cts.POINTER(POINT),)
GetCursorPos.restype = wts.BOOL


