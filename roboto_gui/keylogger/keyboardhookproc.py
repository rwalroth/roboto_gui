from multiprocessing import Process, Queue
import os

from win32con import WH_KEYBOARD
import win32api
import win32gui
from .win_defs import *

dllPath = r"C:\Users\walroth\Documents\repos\roboto_gui\keyhookdll\x64\Release\keyhookdll.dll"

class KeyboardHookProc(Process):
    def __init__(self, hwnd, commandQueue=None, *args, **kwargs):
        super(KeyboardHookProc, self).__init__(*args, **kwargs)
        self.hwnd = hwnd
        if commandQueue is None:
            self.commandQueue = Queue()
        else:
            self.commandQueue = Queue()

    def run(self):
        dll = WinDLL(dllPath)
        hwnd = HWND(self.hwnd)
        res = dll.setMyHook(hwnd)
        print(res)
        while True:
            if not self.commandQueue.empty():
                command = self.commandQueue.get()
                if command == "QUIT":
                    break
