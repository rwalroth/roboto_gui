from multiprocessing import Queue
import json

from PyQt5.QtCore import QThread, pyqtSignal

from .keylogger import RawKeyboardProc, KeyboardHookProc, UWM_NEWNAME_MSG
from .keylogger.win_defs import RegisterWindowMessage, LPCWSTR, PostMessage
from ctypes.wintypes import HWND


class QKeyLog(QThread):
    sigBuffer = pyqtSignal(str)
    sigKeyboard = pyqtSignal(str)
    def __init__(self, commandqueue, *args, **kwargs):
        super(QKeyLog, self).__init__(*args, **kwargs)
        self.commandQueue = commandqueue
        self.getKeyboard = False
        self.keyboard = None
        self.stringBuffer = ""
        self.bufferQueue = Queue()
        self.hookCommandQ = Queue()
        self.keylogger = RawKeyboardProc(self.bufferQueue, daemon=True)
        self.keyhook = None
        self.UWM_NEWNAME = RegisterWindowMessage(LPCWSTR(UWM_NEWNAME_MSG))

    def run(self):
        self.keylogger.start()
        message = json.loads(self.bufferQueue.get())
        print(message)
        self.keyhook = KeyboardHookProc(message["hwnd"], self.hookCommandQ, daemon=True)
        self.keylogHwnd = HWND(message["hwnd"])
        self.keyhook.start()
        while True:
            if not self.bufferQueue.empty():
                jMessage = self.bufferQueue.get()
                message = json.loads(jMessage)
                if self.getKeyboard:
                    self.keyboard = message["keyboard"]
                    self.getKeyboard = False
                    self.sigKeyboard.emit(self.keyboard)
                if self.keyboard is not None and self.keyboard == message["keyboard"] and message["key"] is not None:
                    self.stringBuffer += message["key"]
            if not self.commandQueue.empty():
                command = self.commandQueue.get()
                if command == "PEEK":
                    self.sigBuffer.emit(self.stringBuffer)
                elif command == "GET":
                    print(self.stringBuffer)
                    self.sigBuffer.emit(self.stringBuffer)
                    self.stringBuffer = ""
                elif command == "CLEAR":
                    print(self.stringBuffer)
                    self.stringBuffer = ""
                elif command == "REGISTER":
                    self.getKeyboard = True
                    PostMessage(self.keylogHwnd, self.UWM_NEWNAME, 0, 0)
                elif command == "KEYBOARD":
                    self.sigKeyboard.emit(self.keyboard)
                elif command == "QUIT":
                    break
        self.hookCommandQ.put("QUIT")