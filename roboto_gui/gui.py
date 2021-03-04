import json
from queue import Queue
import traceback
from threading import RLock
from collections import deque

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QMainWindow

import pandas as pd

from .mr_roboto.mr_roboto_funcs import *
from .sample_gui import Ui_MainWindow
from .sample_cassette import SampleCassette
from .qkeylog import QKeyLog
from .pySSRL_bServer.bServer_funcs import specCommand, wait_until_SPECfinished
from .tsstring import TSString
from .RobotoThread import RobotoThread


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


class MrRobotoGui(QMainWindow):
    def __init__(self, robotoRequired=True, parent=None):
        super(MrRobotoGui, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.state = "safe"
        self.awaitingScan = False
        self.splash = QtWidgets.QSplashScreen(self)

        self.qLock = RLock()
        self.taskQueue = deque([])
        self.robotoThread = RobotoThread(self.qLock, self.taskQueue, robotoRequired, self)
        self.robotoThread.stateChanged.connect(self.set_state)
        self.robotoThread.createSpecFile.connect(self.create_SPEC_file)
        self.robotoThread.sampleMounted.connect(self._set_mounted_sample)
        self.robotoThread.start()

        self.selectedSample = None

        # QKeyLog Setup
        self.commandQueue = Queue()
        self.tsString = TSString()
        self.keylog = QKeyLog(self.commandQueue, self.tsString, parent=self)
        self.keylog.sigKeyboard.connect(self.new_keyboard)
        self.keylog.sigBuffer.connect(self.handle_buffer)
        self.keylog.start()
        self.timer = QtCore.QTimer()

        # Menu bar setup
        # Setup
        self.setupWidget = SetupWidget()
        self.setupWidget.hide()
        self.setupWidget.sigFinished.connect(self.setup_finished)
        self.setupWidget.registerButton.clicked.connect(self.register_scanner)
        self.ui.actionSetup.triggered.connect(self.show_setup)
        # File
        self.dataFilePath = ""
        self.metaDataFrame = None
        self.specPath = ""
        self.localDataPath = 'P:/bl2-1/'
        self.ui.actionLoadMetadata.triggered.connect(self.load_metadata_file)
        self.ui.actionSavePath.triggered.connect(self.set_pd_save_path)
        self.ui.actionSetSpecFile.triggered.connect(self.set_spec_file)

        # Cassette pane setup
        self.cassettes = [SampleCassette(self)]
        self.cassettes[0].sigSampleClicked.connect(self.sample_clicked)
        self.ui.cassetteStack.addWidget(self.cassettes[0])
        self.ui.cassetteList.addItem("0")
        self.ui.cassetteList.setCurrentRow(0)
        self.ui.cassetteList.itemClicked.connect(self.set_cassette)
        self.ui.loadButton.clicked.connect(self.load_cassette)
        self.load_cassette(None)

        # Sample scan pane setup
        self.ui.mountButton.clicked.connect(self.mount_sample)
        self.ui.scanButton.clicked.connect(self.scan_sample)
        #self.ui.scanAllButton.clicked.connect(self.scan_all_samples)
        self.ui.scanAllButton.setEnabled(False)

        # Run pane setup
        self.ui.runButton.clicked.connect(self.run_sample)
        #self.ui.runAllButton.clicked.connect(self.run_all_samples)
        self.ui.runAllButton.setEnabled(False)
        # ascan
        self.ui.stepsSpinBoxA.valueChanged.connect(self.estimate_time_A)
        self.ui.timeSpinBoxA.valueChanged.connect(self.estimate_time_A)
        # pscan
        self.ui.minTimeP.valueChanged.connect(self.estimate_time_P)
        self.ui.maxTimeP.valueChanged.connect(self.estimate_time_P)
        self.ui.timePowerP.valueChanged.connect(self.estimate_time_P)
        self.ui.stepPowerP.valueChanged.connect(self.estimate_time_P)
        self.ui.stepsSpinBoxP.valueChanged.connect(self.estimate_time_P)

    def set_state(self, state):
        self.state = state
        if state.lower() == "safe":
            self.ui.statusbar.clearMessage()
        else:
            self.ui.statusbar.showMessage(state)
        self.ui.stateLabel.setText(state)

    def pause_splash_screen(self, message, timeout):
        self.splash.showMessage(message, 1, QtGui.QColor(255, 255, 255))
        self.splash.show()
        time.sleep(timeout)
        self.splash.close()

    def load_metadata_file(self, q=None):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Metadata file",
                                                            os.getcwd(), "CSV files (*.csv);;All files (*)")
        self.dataFilePath = filename
        if filename != "":
            try:
                self.metaDataFrame = pd.read_csv(filename, header=0, index_col=0)
            except:
                self.metaDataFrame = None
                traceback.print_exc()

    def local_to_remote(self, dirname):
        if dirname[:len(self.localDataPath)] != self.localDataPath:
            print("invalid path")
            return
        return '~/data/' + dirname.split(self.localDataPath)[-1]

    def set_pd_save_path(self, q=None):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, "PD Save Path", self.localDataPath)
        if dirname != "":
            remote = self.local_to_remote(dirname)
            if remote is None:
                return
            
            command = f'pd savepath {remote}'
            try:
                print(command)
                specCommand(command, queue=True)
            except:
                traceback.print_exc()

    def set_spec_file(self, q=None):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, "SPEC Save Folder", self.localDataPath)
        if dirname != "":
            remote = self.local_to_remote(dirname)
            if remote is not None:
                self.specPath = remote + "/"
    
    def create_SPEC_file(self, code):
        """Create new calibration spec file with date time stamp"""
        if code == "unscanned":
            row = int(self.mountedSample["row"]) + 1
            column = int(self.mountedSample["column"]) + 1
            idx = row * 3 + column
            cidx = (len(self.cassettes) // 2) + int(self.ui.currentCassetteLabel.text()) + 1
            samplenum = "unsc_" + str(1000*cidx + idx)
        else:
            samplenum = code.split()[-1]
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d-%H%M")
        print(f"Sample number is {samplenum}...")
        samplename = f"BL21Robot_{samplenum}-{timestamp}"
        command = f'newfile {self.specPath}{samplename}'
        try:
            print(command)
            specCommand(command, queue=True)
        except:
            traceback.print_exc()

    # Check state
    def show_setup(self, _):
        if not self.check_state():
            return
        self.setupWidget.cassettesSpinBox.setValue(len(self.cassettes))
        self.setupWidget.show()

    def register_scanner(self, _):
        self.commandQueue.put("CLEAR")
        self.commandQueue.put("REGISTER")

    def new_keyboard(self, keyboard):
        self.setupWidget.keylabel.setText(f"Scanner: {keyboard}")

    def setup_finished(self, q):
        if q == 1:
            while self.cassettes:
                w = self.cassettes.pop()
                w.deleteLater()
                self.ui.cassetteStack.removeWidget(w)
                self.ui.cassetteList.takeItem(len(self.cassettes))
            newCassettes = self.setupWidget.cassettesSpinBox.value()
            adj = newCassettes // 2
            for i in range(newCassettes):
                newCassette = SampleCassette(self)
                newCassette.sigSampleClicked.connect(self.sample_clicked)
                self.cassettes.append(newCassette)
                self.ui.cassetteStack.addWidget(self.cassettes[i])
                self.ui.cassetteList.addItem(str(i - adj))
            self.ui.cassetteList.setCurrentRow(0)
        self.setupWidget.hide()

    def set_cassette(self, q):
        self.ui.cassetteStack.setCurrentIndex(
            (len(self.cassettes) // 2) + int(q.text())
        )

    def load_cassette(self):
        idx = int(self.ui.currentCassetteLabel.text())
        with self.qLock:
            self.taskQueue.append(
                {
                    "task": "load_cassette",
                    "data": idx
                }
            )

    def cassette_loaded(self, idx):
        self.ui.currentCassetteLabel.setText(idx)

    def _current_cassette(self):
        idx = (len(self.cassettes) // 2) + int(self.ui.currentCassetteLabel.text())
        return self.cassettes[idx]

    def sample_clicked(self, data):
        jdata = json.loads(data)
        self.selectedSample = jdata
        self.ui.metaDataText.setText(data)

    def mount_sample(self, _=None):
        with self.qLock:
            self.taskQueue.append(
                {
                    "task": "mount_sample",
                    "data": deepcopy(self.selectedSample)
                }
            )
        self.ui.mountButton.setText("Dismount")
        self.ui.mountButton.clicked.disconnect(self.mount_sample)
        self.ui.mountButton.clicked.connect(self.dismount_sample)

    def _set_mounted_sample(self, jsample):
        sample = json.loads(jsample)
        if sample is None:
            self.ui.currentSampleLabel.setText("None")
        else:
            id = sample["metaData"].get("id", "unscanned")
            self.ui.currentSampleLabel.setText(id)

    # Check state
    def dismount_sample(self, _=None):
        if not self.check_state(mounted=True, cassette=None):
            return
        self.set_state("Dismounting")
        DismountSample(self.roboto)
        self.set_state("Safe")
        self.grabbedSample = deepcopy(self.mountedSample)
        self._set_mounted_sample(None)
        self.replace_current()
        self.ui.mountButton.setText("Mount")
        self.ui.mountButton.clicked.disconnect(self.dismount_sample)
        self.ui.mountButton.clicked.connect(self.mount_sample)

    # Check state
    def scan_sample(self, _=None, sampleIDX=None):
        if not self.check_state():
            return
        if self.selectedSample is not None:
            self.ui.statusbar.showMessage("Scanning Sample")
            self.grab_selected_sample()
            self.commandQueue.put("CLEAR")
            self.set_state("Scanning")
            self.roboto.MovePose(*BarcodeScanPose)
            self.pause_splash_screen("Scanning", 1)
            self.set_state("Safe")
            self.replace_current()
            rawCode = self.read_scanner_data(1)
            if rawCode:
                code = rawCode.split('\n')[0]
                self.ui.metaDataText.setText(code)
                cassette = self._current_cassette()
                self.selectedSample["metaData"]["id"] = code
                if self.metaDataFrame is not None:
                    try:
                        meta = self.metaDataFrame.loc[code].to_dict()
                        self.ui.metaDataText.setText(json.dumps(meta))
                        self.selectedSample["metaData"].update(meta)
                    except:
                        traceback.print_exc()
                cassette.set_metadata(self.selectedSample)
            self.awaitingScan = False

    # Check state
    def scan_grabbed_sample(self, barcode_joints, code):
        if not self.check_state(grabbed=True, mounted=None, cassette=None):
            return
        self.set_state("Scanning")
        self.roboto.MoveJoints(*barcode_joints)
        code = self.read_scanner_data(1)
        self.set_state("Safe")
        return code

    def read_scanner_data(self, timeout):
        self.pause_splash_screen("Scanning sample", timeout)
        code = self.tsString.get_data()
        return code

    def handle_buffer(self, buffer):
        print(buffer)

    # Check state
    def scan_all_samples(self, _):
        if not self.check_state():
            return
        pass

    def estimate_time_A(self, _):
        estimate = self.ui.timeSpinBoxA.value() * self.ui.stepsSpinBoxA.value()
        self.ui.estimatedTimeA.setText(f"Estimated time: {estimate}")

    def estimate_time_P(self, _):
        timePower = self.ui.timePowerP.value()
        steps = self.ui.stepsSpinBoxP.value()
        minTime = self.ui.minTimeP.value()
        maxTime = self.ui.maxTimeP.value()
        if steps > 1:
            scalar = (maxTime - minTime)/((steps - 1)**timePower)
            estimate = sum([minTime + scalar*(x**timePower) for x in range(steps)])
        else:
            estimate = 0.0
        self.ui.estimatedTimeP.setText(f"Estimated time: {estimate}")

    # Check State
    def run_sample(self, _):
        if not self.check_state(safeState=None, grabbed=None, mounted=True,
                                cassette=None):
            return
        if self.ui.scanComboBox.currentText() == "ascan":
            motor = self.ui.motorSelectorA.currentText()
            start = self.ui.startSpinBoxA.value()
            stop = self.ui.stopSpinBoxA.value()
            steps = self.ui.stepsSpinBoxA.value()
            count = self.ui.timeSpinBoxA.value()
            print(f"ascan {motor} {start} {stop} {steps} {count}")
            try:
                specCommand(f"ascan {motor} {start} {stop} {steps} {count}",
                            queue=True)
                self.ui.statusbar.showMessage("ascan running")
                self._wait_for_spec()
            except:
                traceback.print_exc()
        elif self.ui.scanComboBox.currentText() == "pscan":
            motor = self.ui.motorSelectorP.currentText()
            start = self.ui.startSpinBoxP.value()
            stop = self.ui.stopSpinBoxP.value()
            power1 = self.ui.stepPowerP.value()
            minTime = self.ui.minTimeP.value()
            maxTime = self.ui.maxTimeP.value()
            power2 = self.ui.timePowerP.value()
            steps = self.ui.stepsSpinBoxA.value()
            print(f"pscan {motor} {start} {stop} {power1} " +
                  f"{minTime} {maxTime} {power2} {steps}")
            try:
                specCommand(f"pscan {motor} {start} {stop} {power1} " +
                            f"{minTime} {maxTime} {power2} {steps}", queue=True)
                self.ui.statusbar.showMessage("pscan running")
                self._wait_for_spec()
            except:
                traceback.print_exc()

    def _wait_for_spec(self):
        self.set_state("Waiting for SPEC")
        wait_until_SPECfinished(5)
        self.set_state("Safe")

    # Check state
    def run_all_samples(self, _):
        if not self.check_state():
            return
        pass

    def closeEvent(self, event):
        print("Sending kill command to QKeyLog")
        with self.qLock:
            if self.taskQueue:
                self.taskQueue[0] = {"task": "finish"}
            else:
                self.taskQueue.append({"task": "finish"})
        self.robotoThread.wait()
        self.commandQueue.put("QUIT")
        self.keylog.wait()
        print("Closing")
        super(MrRobotoGui, self).closeEvent(event)
