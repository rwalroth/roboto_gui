from threading import RLock
from collections import deque

from .QueueWidgetUI import *

class QueueWidget(QtWidgets.QWidget):
    def __init__(self, qLock=None, qList=None, parent=None):
        super(QueueWidget, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        if qLock is None:
            self.qLock = RLock()
        else:
            self.qLock = qLock
        if qList is None:
            self.qList = deque([])
        else:
            self.qList = qList
        self.ui.moveDownButton.clicked.connect(self.move_item_down)
        self.ui.moveUpButton.clicked.connect(self.move_item_up)
        self.ui.deleteButton.clicked.connect(self.remove_item)

    def _move_item(self, orig, dest):
        with self.qLock:
            currentItem = self.ui.queueList.takeItem(orig)
            self.ui.queueList.insertItem(dest, currentItem)
            self.ui.queueList.setCurrentItem(currentItem)
            self.qList[orig], self.qList[dest] = \
                self.qList[dest], self.qList[orig]

    def move_item_up(self, q=None):
        with self.qLock:
            currentRow = self.ui.queueList.currentRow()
            if currentRow > 0:
                self._move_item(currentRow, currentRow - 1)

    def move_item_down(self, q=None):
        with self.qLock:
            currentRow = self.ui.queueList.currentRow()
            if currentRow < len(self.qList) - 1:
                self._move_item(currentRow, currentRow + 1)

    def remove_item(self, q=None):
        with self.qLock:
            currentRow = self.ui.queueList.currentRow()
            self.ui.queueList.takeItem(currentRow)
