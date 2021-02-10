import json
import time
from copy import deepcopy
from multiprocessing import Queue, Process

import win32gui
import win32api
from win32con import CW_USEDEFAULT, NULL
from .win_defs import *


class RawKeyboardProc(Process):
    def __init__(self, bufferQueue=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if bufferQueue is None:
            self.bufferQueue = Queue()
        else:
            self.bufferQueue = bufferQueue

        self.shift_down = False

        self.UWM_KBHOOK = None
        self.UWM_NEWNAME = None

        self.getNextKeyboard = False
        self.keyboardName = ""

        self.decisionBuffer = []

    def run(self):
        CLASS_NAME = "Mr Roboto raw keyboard input class"
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
        self.UWM_NEWNAME = RegisterWindowMessage(LPCWSTR(UWM_NEWNAME_MSG))

        win32gui.PumpMessages()

    def WndProc(self, hwnd, uMsg, wParam, lParam):
        if uMsg == self.UWM_NEWNAME:
            self.getNextKeyboard = True

        elif uMsg == WM_INPUT:
            return self._handle_wm_input(lParam)

        elif uMsg == self.UWM_KBHOOK:
            return self._handle_uwm_kbhook(hwnd, lParam, wParam)

        return DefWindowProc(hwnd, uMsg, wParam, lParam)

    def _handle_uwm_kbhook(self, hwnd, lParam, wParam):
        pressed = True
        if lParam & 0x80000000:
            pressed = False
        print(f"Hook: {wParam}, {pressed}")
        found = False
        decision = {}
        if self.decisionBuffer:
            found = self._get_decision_from_buffer(decision, found, pressed, wParam)
            if found:
                print(decision)
                if decision["block"]:
                    return 1
                return 0
        if not found:
            return self._get_matching_rmsg(hwnd)
        return 0

    def _get_matching_rmsg(self, hwnd):
        start = time.time() * 1000
        rawMessage = MSG()

        while not PeekMessage(byref(rawMessage), hwnd, WM_INPUT, WM_INPUT, PM_REMOVE):
            if time.time() * 1000 - start > 100:
                print("Hook time out")
                return 0

        raw = self._get_raw_data(rawMessage.lParam)

        keyboardName = self._get_keyboard_name(raw)

        if self.keyboardName == keyboardName:
            self._send_keyboard_message(keyboardName, raw)
            return 1
        else:
            return 0

    def _get_decision_from_buffer(self, decision, found, pressed, wParam):
        for i in range(len(self.decisionBuffer)):
            dec = self.decisionBuffer[i]
            if dec["pressed"] == pressed and dec["code"] == wParam:
                decision.update(dec)
                for j in range(i):
                    self.decisionBuffer.pop(0)
                found = True
                break
        return found

    def _handle_wm_input(self, lParam):
        raw = self._get_raw_data(lParam)

        if raw.header.dwType == RIM_TYPEKEYBOARD:
            keyboardName = self._get_keyboard_name(raw)

            if self.getNextKeyboard:
                self.keyboardName = keyboardName
                self.getNextKeyboard = False

            self.decisionBuffer.append(
                {
                    "code": raw.keyboard.VKey,
                    "pressed": raw.keyboard.Flags == RI_KEY_MAKE,
                    "block": self.keyboardName == keyboardName
                }
            )
            print(f"Raw: {raw.keyboard.VKey}, {raw.keyboard.Flags == RI_KEY_MAKE}")

            if self.keyboardName == keyboardName:
                self._send_keyboard_message(keyboardName, raw)

        return 0

    def _send_keyboard_message(self, keyboardName, raw):
        message = {"keyboard": keyboardName}
        message["key"] = None

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

    def _get_raw_data(self, lParam):
        dwSize = c_uint()
        GetRawInputData(lParam, RID_INPUT, NULL, byref(dwSize), sizeof(RAWINPUTHEADER))
        raw = RAWINPUT()
        GetRawInputData(lParam, RID_INPUT, byref(raw), byref(dwSize), sizeof(RAWINPUTHEADER))
        return raw

    def _get_keyboard_name(self, raw):
        bufferSize = c_uint()
        GetRawInputDeviceInfo(raw.header.hDevice, RIDI_DEVICENAME, NULL, byref(bufferSize))
        stringBuffer = create_unicode_buffer(bufferSize.value)
        GetRawInputDeviceInfo(raw.header.hDevice, RIDI_DEVICENAME, byref(stringBuffer), byref(bufferSize))
        return ''.join(stringBuffer)
