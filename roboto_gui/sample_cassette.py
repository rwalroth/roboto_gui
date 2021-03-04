import json
from PyQt5 import QtWidgets, QtCore


class SampleButton(QtWidgets.QPushButton):
    sigClicked = QtCore.pyqtSignal(str)

    def __init__(self, text, row, column, cassette=0, parent=None):
        super(SampleButton, self).__init__(text, parent)
        self.row = row
        self.column = column
        self.cassette = cassette
        self.metaData = {}
        self.clicked.connect(self.button_clicked)

    def button_clicked(self, _):
        self.sigClicked.emit(json.dumps({
            "row": self.row,
            "column": self.column,
            "cassette": self.cassette,
            "metaData": self.metaData
        }))

    def set_meta(self, newData):
        self.metaData = newData
        self.setText(newData["id"])


class SampleCassette(QtWidgets.QWidget):
    sigSampleClicked = QtCore.pyqtSignal(str)

    def __init__(self, cassetteNumber=0, parent=None):
        super(SampleCassette, self).__init__(parent)
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.cassetteNumber = cassetteNumber
        self.sampleButtons = []
        for i in range(9):
            row = i // 3
            column = i % 3
            newButton = SampleButton(f"unscanned {i}", row - 1, column - 1,
                                     self.cassetteNumber, self)
            newButton.sigClicked.connect(self.sigSampleClicked.emit)
            self.layout.addWidget(newButton, row, column)
            self.sampleButtons.append(newButton)

    def set_metadata(self, sample):
        row = int(sample["row"]) + 1
        column = int(sample["column"]) + 1
        idx = row * 3 + column
        self.sampleButtons[idx].set_meta(sample["metaData"])
