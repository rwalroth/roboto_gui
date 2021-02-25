from PyQt5.QtCore import QThread


class RobotoThread(QThread):
    def __init__(self, qLock, taskQueue, parent=None):
        super(RobotoThread, self).__init__(parent)
        self.qLock = qLock
        self.taskQueue = taskQueue

    def run(self):
        task = None
        with self.qLock:
            if self.taskQueue:
                priority =
                for i, t in enumerate(self.taskQueue):
                    if t["priority"] > task["priority"]:
                        task = t
                        idx = i
                del self.taskQueue[idx]
        if task is not None:
