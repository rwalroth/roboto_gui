import json
from threading import RLock
from copy import deepcopy
from PyQt5 import QtWidgets, QtCore


class SampleButton(QtWidgets.QPushButton):
    sigClicked = QtCore.pyqtSignal(str)

    def __init__(self, text, row, column, cassette=0, parent=None):
        super(SampleButton, self).__init__(text, parent)
        self.row = row
        self.column = column
        self.cassette = cassette
        self.metaData = {}
        self.metaLock = RLock()
        self.clicked.connect(self.button_clicked)

    def button_clicked(self, _):
        self.sigClicked.emit(self.__str__())

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            "row": deepcopy(self.row),
            "column": deepcopy(self.column),
            "cassette": deepcopy(self.cassette),
            "metaData": deepcopy(self.metaData)
        }

    def set_meta(self, newData):
        with self.metaLock:
            self.metaData = newData
            self.setText(newData["id"])


class SampleCassette(QtWidgets.QWidget):
    sigSampleClicked = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, cassetteNumber=0):
        super(SampleCassette, self).__init__(parent)
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.cassetteNumber = cassetteNumber
        self.sampleButtons = []
        self.metaLock = RLock()
        for i in range(9):
            row = i // 3
            column = i % 3
            newButton = SampleButton(f"unscanned {i}", row - 1, column - 1,
                                     self.cassetteNumber, parent=self)
            newButton.sigClicked.connect(self.sigSampleClicked.emit)
            self.layout.addWidget(newButton, row, column)
            self.sampleButtons.append(newButton)

    def set_metadata(self, sample):
        with self.metaLock:
            row = int(sample["row"]) + 1
            column = int(sample["column"]) + 1
            idx = row * 3 + column
            self.sampleButtons[idx].set_meta(sample["metaData"])
