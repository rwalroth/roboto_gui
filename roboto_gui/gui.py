import json
from multiprocessing import Queue
import time

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget

from .mr_roboto.MrRoboto_python_test import *
from .sample_gui import Ui_Form
from .sample_cassette import SampleCassette
from .qkeylog import QKeyLog
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
        self.keylabel = QtWidgets.QLabel("Scanner: None")
        self.registerButton = QtWidgets.QPushButton("Register Scanner")
        self.layout.addWidget(self.registerButton, 1, 0)
        self.layout.addWidget(self.keylabel, 1, 1)
        self.applyButton = QtWidgets.QPushButton("Apply")
        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.layout.addWidget(self.applyButton, 2, 0)
        self.layout.addWidget(self.cancelButton, 2, 1)

        self.applyButton.clicked.connect(self.apply_clicked)
        self.cancelButton.clicked.connect(self.cancel_clicked)

    def apply_clicked(self, _):
        self.sigFinished.emit(1)

    def cancel_clicked(self, _):
        self.sigFinished.emit(-1)


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
        self.setupWidget.registerButton.clicked.connect(self.register_scanner)

        self.dataFilePath = ""
        self.state = "safe"
        self.currentSample = None

        self.ui.mountButton.clicked.connect(self.mount_sample)
        self.ui.scanButton.clicked.connect(self.scan_sample)
        self.ui.runButton.clicked.connect(self.run_sample)
        self.ui.loadButton.clicked.connect(self.load_cassette)
        self.ui.scanAllButton.clicked.connect(self.scan_all_sampels)

        self.hwnd = int(self.winId())
        self.commandQueue = Queue()
        self.keylog = QKeyLog(self.commandQueue, parent=self)
        self.keylog.sigKeyboard.connect(self.new_keyboard)
        self.keylog.sigBuffer.connect(self.handle_buffer)
        self.keylog.start()
        self.timer = QtCore.QTimer()
        self.awaitingScan = False
        self.splash = QtWidgets.QSplashScreen(self)


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
            self.ui.cassetteList.setCurrentRow(0)
        self.setupWidget.hide()

    def sample_clicked(self, data):
        jdata = json.loads(data)
        self.currentSample = jdata
        self.ui.metaDataText.setText(data)

    def mount_sample(self, _):
        if self.currentSample is not None:
            id = self.currentSample["metaData"].get("id", "unscanned")
            self.ui.currentSampleLabel.setText(id)

    def scan_sample(self, _):
        if self.ui.currentCassetteLabel.text() != self.ui.cassetteList.currentItem().text():
            reply = QtWidgets.QMessageBox.question(
                self,
                "test",
                "Scanning this requires loading a new cassette, proceed?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.Yes:
                self.load_cassette(None)
            else:
                return
        if not self.awaitingScan and self.currentSample is not None:
            self.commandQueue.put("CLEAR")
            self.awaitingScan = True
            self.timer.singleShot(5000, self.get_scan_result)
            self.splash.showMessage("Scanning sample", 1, QtGui.QColor(255, 255, 255))
            self.splash.show()

    def get_scan_result(self, _=None):
        self.commandQueue.put("GET")
        self.awaitingScan = False
        self.splash.close()

    def run_sample(self, _):
        if self.currentSample is not None:
            self.currentSample["scanned"] = True

    def load_cassette(self, _):
        self.ui.currentCassetteLabel.setText(self.ui.cassetteList.currentItem().text())

    def scan_all_sampels(self, _):
        pass

    def register_scanner(self, _):
        self.commandQueue.put("CLEAR")
        self.commandQueue.put("REGISTER")

    def new_keyboard(self, keyboard):
        self.setupWidget.keylabel.setText(f"Scanner: {keyboard}")

    def handle_buffer(self, buffer):
        self.ui.metaDataText.setText(buffer)
        cassette = self._current_cassette()
        self.currentSample["metaData"]["id"] = buffer
        cassette.set_metadata(self.currentSample)

    def close(self):
        self.commandQueue.put("QUIT")
        return super().close()

    def _current_cassette(self):
        idx = int(self.ui.currentCassetteLabel.text())
        return self.cassettes[idx - 1]
