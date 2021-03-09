from multiprocessing import Queue
import json
import os

from PyQt5.QtCore import QThread, pyqtSignal
from .keylogger import RawKeyboardProc, KeyboardHookProc, UWM_NEWNAME_MSG
from .keylogger.win_defs import RegisterWindowMessage, LPCWSTR, PostMessage, WM_QUIT
from ctypes.wintypes import HWND

mainPath = os.path.abspath(__file__).split("roboto_gui")[0]
logDirectory = os.path.join(mainPath, "roboto_gui\\logs")
if not os.path.isdir(logDirectory):
    os.mkdir(logDirectory)
logPath = os.path.join(logDirectory, "keyboard_record.json")

class QKeyLog(QThread):
    sigBuffer = pyqtSignal(str)
    sigKeyboard = pyqtSignal(str)

    def __init__(self, commandqueue, tsString, *args, **kwargs):
        super(QKeyLog, self).__init__(*args, **kwargs)
        self.keyboardRecord = {
            "all_keyboards": [],
            "ignore_list": [],
            "last_used": None,
            "previously_used": []
        }
        self.keyboardRecordPath = logPath
        if not os.path.exists(self.keyboardRecordPath):
            with open(self.keyboardRecordPath, 'w') as file:
                json.dump(self.keyboardRecord, file, indent=4)
        else:
            with open(self.keyboardRecordPath, 'r') as file:
                keyboardRecord = json.load(file)
                for key in self.keyboardRecord:
                    if key in keyboardRecord:
                        self.keyboardRecord[key] = keyboardRecord[key]

        self.tsString = tsString
        self.commandQueue = commandqueue
        self.getKeyboard = False
        if self.keyboardRecord["last_used"] is None or \
                self.keyboardRecord["last_used"] == "null":
            self.keyboard = None
        else:
            self.keyboard = self.keyboardRecord["last_used"]
        self.bufferQueue = Queue()
        self.hookCommandQ = Queue()
        self.keylogger = None
        self.keyhook = None
        self.UWM_NEWNAME = RegisterWindowMessage(LPCWSTR(UWM_NEWNAME_MSG))

    def run(self):
        self.keylogger = RawKeyboardProc(
            self.bufferQueue,
            self.keyboard,
            self.keyboardRecord["ignore_list"],
            daemon=True)
        self.keylogger.start()
        message = json.loads(self.bufferQueue.get())
        self.keyhook = KeyboardHookProc(message["hwnd"], self.hookCommandQ, daemon=True)
        self.keylogHwnd = HWND(message["hwnd"])
        self.keyhook.start()
        if self.keyboard is not None:
            self.sigKeyboard.emit(self.keyboard)
        while True:
            if not self.bufferQueue.empty():
                jMessage = self.bufferQueue.get()
                message = json.loads(jMessage)
                if self.getKeyboard:
                    keyboard = message["keyboard"]
                    if keyboard not in self.keyboardRecord["ignore_list"]:
                        self.keyboard = message["keyboard"]
                        self.getKeyboard = False
                        self.sigKeyboard.emit(self.keyboard)
                        self.record_keyboard(keyboard, True)
                    else:
                        self.record_keyboard(keyboard, False)
                if (self.keyboard is not None) and (self.keyboard == message["keyboard"]) and (message["key"] is not None):
                    self.tsString.append_data(message["key"])
            if not self.commandQueue.empty():
                command = self.commandQueue.get()
                if command == "PEEK":
                    self.sigBuffer.emit(self.tsString.get_data())
                elif command == "GET":
                    print(self.tsString.get_data())
                    self.tsString.set_data("")
                elif command == "CLEAR":
                    print(self.tsString.get_data())
                    self.tsString.set_data("")
                elif command == "REGISTER":
                    self.getKeyboard = True
                    self.keyboard = None
                    self.sigKeyboard.emit(self.keyboard)
                    PostMessage(self.keylogHwnd, self.UWM_NEWNAME, 0, 0)
                elif command == "KEYBOARD":
                    self.sigKeyboard.emit(self.keyboard)
                elif command == "QUIT":
                    break
        self.hookCommandQ.put("QUIT")
        PostMessage(self.keylogHwnd, WM_QUIT, 0, 0)
        self.keyhook.join()
        self.keylogger.join()

    def record_keyboard(self, keyboard, used):
        # self.keyboardRecord["all_keyboards"].append(keyboard)
        if used:
            self.keyboardRecord["all_keyboards"].append(keyboard)
            self.keyboardRecord["last_used"] = keyboard
            self.keyboardRecord["previously_used"].append(keyboard)
            with open(self.keyboardRecordPath, 'w') as file:
                json.dump(self.keyboardRecord, file, indent=4)
