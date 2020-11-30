import json
from PyQt5 import QtWidgets, QtCore


class SampleButton(QtWidgets.QPushButton):
    sigClicked = QtCore.pyqtSignal(str)

    def __init__(self, text, row, column, parent=None):
        super(SampleButton, self).__init__(text, parent)
        self.row = row
        self.column = column
        self.metaData = ""
        self.clicked.connect(self.button_clicked)

    def button_clicked(self, _):
        self.sigClicked.emit(json.dumps({
            "row": self.row,
            "column": self.column,
            "metaData": self.metaData
        }))

    def set_meta(self, newData):
        self.metaData = newData


class SampleCassette(QtWidgets.QWidget):
    sigSampleClicked = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(SampleCassette, self).__init__(parent)
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.sampleButtons = []
        for i in range(9):
            row = i // 3
            column = i % 3
            newButton = SampleButton("unscanned", row - 1, column - 1, self)
            newButton.sigClicked.connect(self.sigSampleClicked.emit)
            self.layout.addWidget(newButton, row, column)
            self.sampleButtons.append(newButton)
