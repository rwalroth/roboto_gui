import json
from queue import Queue

from PyQt5.QtCore import QThread, pyqtSignal

from .mr_roboto.mr_roboto_funcs import *
from .qkeylog import QKeyLog
from .tsstring import TSString


class RobotoThread(QThread):
    taskStarted = pyqtSignal(str)
    codeScanned = pyqtSignal(str)

    def __init__(self, qLock, taskQueue, parent=None):
        super(RobotoThread, self).__init__(parent)
        self.qLock = qLock
        self.taskQueue = taskQueue
        self.state = "safe"

        self.mountedSample = None
        self.grabbedSample = None

        # QKeyLog Setup
        self.commandQueue = Queue()
        self.tsString = TSString()
        self.keylog = QKeyLog(self.commandQueue, self.tsString, parent=self)
        self.keylog.sigKeyboard.connect(self.new_keyboard)
        self.keylog.sigBuffer.connect(self.handle_buffer)
        self.keylog.start()

        self.roboto = None

    def _run(self):
        while True:
            task = None
            with self.qLock:
                if self.taskQueue:
                    task = self.taskQueue.pop()
                    self.taskStarted.emit(task)

            if task is not None:
                jtask = json.loads(task)
                if jtask["task"].lower() == "finish":
                    break

    def run(self):
        try:
            self.roboto = MrRobotoStart()
            self._run()
        except:
            raise
        finally:
            self.roboto_disconnect()

    def roboto_disconnect(self):
        if self.roboto is not None:
            print("Deactivating Mr Roboto")
            self.roboto.MoveJoints(0,0,0,0,0,0)
            self.roboto.Delay(3)
            self.roboto.Deactivate()
            self.roboto.Disconnect()


