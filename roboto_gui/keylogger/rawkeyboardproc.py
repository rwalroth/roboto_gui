import json
from multiprocessing import Queue, Process

import win32gui
import win32api
from win32con import CW_USEDEFAULT, NULL
from .win_defs import *

UWM_KBHOOK_MSG = "UMW_KBHOOK-{B30856F0-D3DD-11d4-A00B-006067718D04}"

class RawKeyboardProc(Process):
    def __init__(self, bufferQueue=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if bufferQueue is None:
            self.bufferQueue = Queue()
        else:
            self.bufferQueue = bufferQueue

        self.shift_down = False

        self.UWM_KBHOOK = None

    def run(self):
        CLASS_NAME = "My window class"
        hInstance = win32api.GetModuleHandle()

        wndclass = win32gui.WNDCLASS()
        wndclass.style = 0
        wndclass.lpfnWndProc = lambda h, m, w, l: self.WndProc(h, m, w, l)
        wndclass.hInstance = hInstance
        wndclass.lpszClassName = CLASS_NAME

        wndClassAtom = None
        wndClassAtom = win32gui.RegisterClass(wndclass)

        hwnd = win32gui.CreateWindow(
            wndClassAtom,
            "Capturing keyboard input",
            NULL,

            CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT,

            NULL,
            NULL,
            hInstance,
            None
        )

        if hwnd == NULL:
            raise RuntimeError("Failed to create window")

        self.bufferQueue.put(json.dumps({"hwnd": hwnd}))

        Rid = (1 * RAWINPUTDEVICE)()
        Rid[0].usUsagePage = 0x01
        Rid[0].usUsage = 0x06
        Rid[0].dwFlags = RIDEV_INPUTSINK
        Rid[0].hwndTarget = hwnd

        RegisterRawInputDevices(Rid, 1, sizeof(RAWINPUTDEVICE))
        self.UWM_KBHOOK = RegisterWindowMessage(LPCWSTR(UWM_KBHOOK_MSG))
        win32gui.PumpMessages()

    def WndProc(self, hwnd, uMsg, wParam, lParam):
        if uMsg == WM_INPUT:
            dwSize = c_uint()
            GetRawInputData(lParam, RID_INPUT, NULL, byref(dwSize), sizeof(RAWINPUTHEADER))

            raw = RAWINPUT()

            GetRawInputData(lParam, RID_INPUT, byref(raw), byref(dwSize), sizeof(RAWINPUTHEADER))

            if raw.header.dwType == RIM_TYPEKEYBOARD:
                bufferSize = c_uint()
                GetRawInputDeviceInfo(raw.header.hDevice, RIDI_DEVICENAME, NULL, byref(bufferSize))

                stringBuffer = create_unicode_buffer(bufferSize.value)
                GetRawInputDeviceInfo(raw.header.hDevice, RIDI_DEVICENAME, byref(stringBuffer), byref(bufferSize))
                keyboardName = ''.join(stringBuffer)
                message = {"keyboard": keyboardName}
                message["key"] = None
                print(f"Raw: {raw.keyboard.VKey}, {raw.keyboard.Flags == RI_KEY_MAKE}")
                if raw.keyboard.VKey in VKCodes:
                    newChar = VKCodes[raw.keyboard.VKey]
                    if raw.keyboard.Flags == RI_KEY_MAKE:
                        if newChar[0] == "SHIFT":
                            self.shift_down = True
                        elif newChar[0] == "SPACE":
                            message["key"] = ' '
                        elif self.shift_down:
                            message["key"] = newChar[1]
                        else:
                            message["key"] = newChar[0]
                        self.bufferQueue.put(json.dumps(message))
                    elif raw.keyboard.Flags == RI_KEY_BREAK:
                        if newChar[0] == "SHIFT":
                            self.shift_down = False
            return 0

        elif uMsg == self.UWM_KBHOOK:
            pressed = True
            if lParam & 0x80000000:
                pressed = False
            print(f"Hook: {USHORT(wParam)}, {pressed}")
            return 0

        return DefWindowProc(hwnd, uMsg, wParam, lParam)