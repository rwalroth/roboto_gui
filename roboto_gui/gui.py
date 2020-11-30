import json
import os
import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget
from MrRoboto_python_test import *
from sample_gui import Ui_Form
from sample_cassette import SampleCassette
import qdarkstyle


class SetupWidget(QWidget):
    sigFinished = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QGridLayout(self)
        self.setLayout(self.layout)
        self.cassettesLabel = QtWidgets.QLabel("Number of cassettes:")
        self.cassettesSpinBox = QtWidgets.QSpinBox()
        self.layout.addWidget(self.cassettesLabel, 0, 0)
        self.layout.addWidget(self.cassettesSpinBox, 0, 1)
        self.applyButton = QtWidgets.QPushButton("Apply")
        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.layout.addWidget(self.applyButton, 1, 0)
        self.layout.addWidget(self.cancelButton, 1, 1)

        self.applyButton.clicked.connect(self.apply_clicked)
        self.cancelButton.clicked.connect(self.cancel_clicked)

    def apply_clicked(self, _):
        self.sigFinished.emit(1)

    def cancel_clicked(self, _):
        self.sigFinished.emit(-1)


class ScanInputWidget(QWidget):
    def __init__(self, parent=None):
        super(ScanInputWidget, self).__init__(parent)
        self.inputLine = QtWidgets.QLineEdit(self)
        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.layout().addWidget(self.inputLine)
        self.inputLine.textChanged.connect(self.received_input)

    def get_input(self):
        self.inputLine.grabKeyboard()

    def received_input(self, q=None):
        if q is not None:
            print(q)
        self.inputLine.releaseKeyboard()


class MrRobotoGui(QWidget):
    def __init__(self, parent=None):
        super(MrRobotoGui, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.cassettes = [SampleCassette(self)]
        self.cassettes[0].sigSampleClicked.connect(self.sample_clicked)
        self.ui.cassetteStack.addWidget(self.cassettes[0])
        self.ui.cassetteList.addItem("1")
        self.ui.cassetteList.setCurrentRow(0)

        self.ui.cassetteList.itemClicked.connect(self.set_cassette)

        self.ui.setupButton.clicked.connect(self.show_setup)

        self.setupWidget = SetupWidget()
        self.setupWidget.hide()
        self.setupWidget.sigFinished.connect(self.setup_finished)

        self.dataFilePath = ""
        self.state = "safe"
        self.currentSample = {}

        self.inputWidget = ScanInputWidget()

        self.ui.mountButton.clicked.connect(self.mount_sample)
        self.ui.scanButton.clicked.connect(self.scan_sample)
        self.ui.runButton.clicked.connect(self.run_sample)
        self.ui.loadButton.clicked.connect(self.load_cassette)
        self.ui.scanAllButton.clicked.connect(self.scan_all_sampels)

    def set_cassette(self, q):
        self.ui.cassetteStack.setCurrentIndex(int(q.text()) - 1)

    def show_setup(self, _):
        self.setupWidget.cassettesSpinBox.setValue(len(self.cassettes))
        self.setupWidget.show()

    def setup_finished(self, q):
        if q == 1:
            while self.cassettes:
                w = self.cassettes.pop()
                w.deleteLater()
                self.ui.cassetteStack.removeWidget(w)
                self.ui.cassetteList.takeItem(len(self.cassettes))
            newCassettes = self.setupWidget.cassettesSpinBox.value()
            for i in range(newCassettes):
                newCassette = SampleCassette(self)
                newCassette.sigSampleClicked.connect(self.sample_clicked)
                self.cassettes.append(newCassette)
                self.ui.cassetteStack.addWidget(self.cassettes[i])
                self.ui.cassetteList.addItem(str(i + 1))
        self.setupWidget.hide()

    def sample_clicked(self, data):
        jdata = json.loads(data)
        self.ui.metaDataText.setText()
        self.currentSample = jdata

    def mount_sample(self, _):
        pass

    def scan_sample(self, _):
        self.inputWidget.show()
        self.inputWidget.get_input()

    def run_sample(self, _):
        pass
    def load_cassette(self, _):
        pass
    def scan_all_sampels(self, _):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api=os.environ['PYQTGRAPH_QT_LIB']))
    w = MrRobotoGui()
    w.show()
    sys.exit(app.exec_())
