import time
from threading import Lock, Condition
from collections import deque
from queue import Queue
from .QueueWidgetUI import *

class QueueWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(QueueWidget, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.mutex = Lock()
        self.not_empty = Condition(self.mutex)
        self.not_paused = Condition(self.mutex)
        self.paused = False
        self._qList = deque([])
        self.ui.moveDownButton.clicked.connect(self._move_item_down)
        self.ui.moveUpButton.clicked.connect(self._move_item_up)
        self.ui.deleteButton.clicked.connect(self._remove_item)
        self.ui.playPauseButton.clicked.connect(self._set_paused)

    def _move_item(self, orig, dest):
        currentItem = self.ui.queueList.takeItem(orig)
        self.ui.queueList.insertItem(dest, currentItem)
        self.ui.queueList.setCurrentItem(currentItem)
        self._qList[orig], self._qList[dest] = \
            self._qList[dest], self._qList[orig]

    def _move_item_up(self, q=None):
        with self.mutex:
            currentRow = self.ui.queueList.currentRow()
            if currentRow > 0:
                self._move_item(currentRow, currentRow - 1)

    def _move_item_down(self, q=None):
        with self.mutex:
            currentRow = self.ui.queueList.currentRow()
            if currentRow < len(self._qList) - 1:
                self._move_item(currentRow, currentRow + 1)

    def _remove_item(self, q=None, idx=None):
        with self.mutex:
            if idx is None:
                currentRow = self.ui.queueList.currentRow()
            else:
                currentRow = idx
            if currentRow >= 0 and self._qList:
                self.ui.queueList.takeItem(currentRow)
                del self._qList[currentRow]

    def _set_paused(self, q=None):
        self.set_paused()

    def set_paused(self, pause=None):
        with self.not_paused:
            if pause is None:
                self.paused = not self.paused
            else:
                self.paused = pause
            if self.paused:
                self.ui.currentTaskLabel.setText("PAUSED")
            else:
                self.ui.currentTaskLabel.setText("None")
                self.not_paused.notify()

    def is_paused(self):
        with self.not_paused:
            if self.paused:
                return True
            return False

    def put(self, label, task, doNext=False):
        with self.mutex:
            if doNext:
                self._qList.appendleft(task)
                self.ui.queueList.insertItem(0, label)
            else:
                self._qList.append(task)
                self.ui.queueList.addItem(label)
            self.not_empty.notify()

    def get(self):
        with self.mutex:
            while not len(self._qList):
                self.not_empty.wait()
            while self.paused:
                self.not_paused.wait()
            if self._qList:
                task = self._qList.popleft()
                label = self.ui.queueList.takeItem(0)
                self.ui.currentTaskLabel.setText(label.text())
                return task, label.text()
            else:
                return "null", "null"

    def wait_for_paused(self):
        with self.not_paused:
            while self.paused:
                self.not_paused.wait()

    def empty(self):
        with self.mutex:
            return len(self._qList) > 0

    def clear_task_label(self, q=None):
        with self.mutex:
            if not self.paused:
                self.ui.currentTaskLabel.setText("None")

    def clear(self):
        with self.mutex:
            self._qList.clear()
            self.ui.queueList.clear()
            self.ui.currentTaskLabel.setText("None")
