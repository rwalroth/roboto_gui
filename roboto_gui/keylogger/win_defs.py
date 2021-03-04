# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/208699
# http://msdn.microsoft.com/en-us/library/ms645565(VS.85).aspx
# http://www.eventghost.org (the source code)

from ctypes import *
from ctypes.wintypes import *
from .vkcodes import VKCodes


# Constants not in win32con
RIDEV_INPUTSINK = 0x00000100
WM_INPUT = 0x0ff
WM_USER = 0x0400
WM_PAINT = 0x000f
PM_NOREMOVE = 0x0000
PM_REMOVE = 0x0001
PM_NOYIELD = 0x0002
RID_INPUT = 0x10000003
RIM_TYPEKEYBOARD = 0x00000001
RIDI_DEVICENAME = 0x20000007
RI_KEY_MAKE = 0
RI_KEY_BREAK = 1
ULONG_PTR = WPARAM
LRESULT = LPARAM
LPMSG = POINTER(MSG)
HOOKPROC = WINFUNCTYPE(LRESULT, c_int, WPARAM, LPARAM)


# User defined message strings
UWM_KBHOOK_MSG = "UMW_KBHOOK-{B30856F0-D3DD-11d4-A00B-006067718D04}"
UWM_NEWNAME_MSG = "UWM_NEWNAME-{l3EvBXYE-rqL3-9u11-0fe2-Jl342JRjEuzc}"


# Functions that need to be imported
def errcheck_bool(result, func, args):
    if not result:
        raise WinError(get_last_error())
    return args

KeyboardProc = HOOKPROC

RegisterRawInputDevices = windll.user32.RegisterRawInputDevices

GetRawInputData = windll.user32.GetRawInputData
GetRawInputDeviceInfo = windll.user32.GetRawInputDeviceInfoW
GetRawInputDeviceInfo.argtypes = (HANDLE, UINT, LPVOID, PUINT)

RegisterWindowMessage = windll.user32.RegisterWindowMessageW
RegisterWindowMessage.argtypes = (LPCWSTR,)

DefWindowProc = windll.user32.DefWindowProcA
DefWindowProc.argtypes = (HWND, UINT, WPARAM, LPARAM)

PostMessage = windll.user32.PostMessageW
PostMessage.argtypes = (HWND, UINT, WPARAM, LPARAM)
PeekMessage = windll.user32.PeekMessageW
PeekMessage.argtypes = (LPMSG, HWND, UINT, UINT, UINT)

TranslateMessage = windll.user32.TranslateMessage
TranslateMessage.argtypes = (LPMSG,)


DispatchMessage = windll.user32.DispatchMessageW
DispatchMessage.argtypes = (LPMSG,)

SetWindowsHookEx = windll.user32.SetWindowsHookExW
SetWindowsHookEx.errcheck = errcheck_bool
SetWindowsHookEx.restype = HHOOK
SetWindowsHookEx.argtypes = (c_int, HOOKPROC, HINSTANCE, DWORD)

CallNextHookEx = windll.user32.CallNextHookEx
CallNextHookEx.restype = LRESULT
CallNextHookEx.argtypes = (HHOOK,  # _In_opt_ hhk
                           c_int,  # _In_     nCode
                           WPARAM, # _In_     wParam
                           LPARAM) # _In_     lParam

GetMessageW = windll.user32.GetMessageW
GetMessageW.argtypes = (LPMSG, # _Out_    lpMsg
                        HWND,  # _In_opt_ hWnd
                        UINT,  # _In_     wMsgFilterMin
                        UINT)  # _In_     wMsgFilterMax


class RAWINPUTDEVICE(Structure):
    _fields_ = [
        ("usUsagePage", c_ushort),
        ("usUsage", c_ushort),
        ("dwFlags", DWORD),
        ("hwndTarget", HWND),
    ]

class RAWINPUTHEADER(Structure):
    _fields_ = [
        ("dwType", DWORD),
        ("dwSize", DWORD),
        ("hDevice", HANDLE),
        ("wParam", WPARAM),
    ]

class RAWMOUSE(Structure):
    class _U1(Union):
        class _S2(Structure):
            _fields_ = [
                ("usButtonFlags", c_ushort),
                ("usButtonData", c_ushort),
            ]
        _fields_ = [
            ("ulButtons", ULONG),
            ("_s2", _S2),
        ]

    _fields_ = [
        ("usFlags", c_ushort),
        ("_u1", _U1),
        ("ulRawButtons", ULONG),
        ("lLastX", LONG),
        ("lLastY", LONG),
        ("ulExtraInformation", ULONG),
    ]
    _anonymous_ = ("_u1", )


class RAWKEYBOARD(Structure):
    _fields_ = [
        ("MakeCode", c_ushort),
        ("Flags", c_ushort),
        ("Reserved", c_ushort),
        ("VKey", c_ushort),
        ("Message", UINT),
        ("ExtraInformation", ULONG),
    ]


class RAWHID(Structure):
    _fields_ = [
        ("dwSizeHid", DWORD),
        ("dwCount", DWORD),
        ("bRawData", BYTE),
    ]


class RAWINPUT(Structure):
    class _U1(Union):
        _fields_ = [
            ("mouse", RAWMOUSE),
            ("keyboard", RAWKEYBOARD),
            ("hid", RAWHID),
        ]

    _fields_ = [
        ("header", RAWINPUTHEADER),
        ("_u1", _U1),
        ("hDevice", HANDLE),
        ("wParam", WPARAM),
    ]
    _anonymous_ = ("_u1", )
