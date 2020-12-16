from multiprocessing import Process, Queue
import os
import sys

from .win_defs import *

mainPath = os.path.abspath(__file__).split("roboto_gui")[0]

if sys.maxsize > 2**32:
    dllPath = os.path.join(
        mainPath,
        "roboto_gui\\keyhookdll\\x64\\Release\\keyhookdll.dll"
    )
else:
    dllPath = os.path.join(
        mainPath,
        "roboto_gui\\keyhookdll\\Release\\keyhookdll.dll"
    )


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
