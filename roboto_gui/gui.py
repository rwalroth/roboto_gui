import json
from copy import deepcopy
from functools import wraps
from queue import Queue
import traceback

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QMainWindow

import pandas as pd

from .mr_roboto.mr_roboto_funcs import *
from .sample_gui import Ui_MainWindow
from .sample_cassette import SampleCassette
from .qkeylog import QKeyLog
from .pySSRL_bServer.bServer_funcs import specCommand, wait_until_SPECfinished
from .tsstring import TSString


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


def SampleMounted(mounted=True):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if mounted:
                if self.mountedSample is None:
                    print(f"Cannot execute {func.__name__} without a sample mounted")
                else:
                    return func(self, *args, **kwargs)
            else:
                if self.mountedSample is not None:
                    print(f"Cannot execute {func.__name__} with a sample mounted")
                else:
                    return func(self, *args, **kwargs)
        return wrapper
    return decorator


def SampleGrabbed(grabbed=True):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if grabbed:
                if self.grabbedSample is None:
                    print(f"Cannot execute {func.__name__} without a sample grabbed")
                else:
                    return func(self, *args, **kwargs)
            else:
                if self.grabbedSample is not None:
                    print(f"Cannot execute {func.__name__} with a sample grabbed")
                else:
                    return func(self, *args, **kwargs)
        return wrapper
    return decorator


def RobotoSafe(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.state.lower() != "safe":
            print(f"Cannot execute {func.__name__}, robot not safe")
        else:
            return func(self, *args, **kwargs)
    return wrapper


class MrRobotoGui(QMainWindow):
    def __init__(self, parent=None):
        super(MrRobotoGui, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.state = "safe"
        self.awaitingScan = False
        self.splash = QtWidgets.QSplashScreen(self)

        self.mountedSample = None
        self.grabbedSample = None
        self.selectedSample = None

        self.roboto = MrRobotoStart()

        try:
            test = list(self.roboto.GetJoints())
        except:
            raise RuntimeError("MrRoboto failed to start")

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
        self.ui.actionLoadMetadata.triggered.connect(self.load_metadata_file)
        self.ui.actionSavePath.triggered.connect(self.set_pd_save_path)

        # Cassette pane setup
        self.cassettes = [SampleCassette(self)]
        self.cassettes[0].sigSampleClicked.connect(self.sample_clicked)
        self.ui.cassetteStack.addWidget(self.cassettes[0])
        self.ui.cassetteList.addItem("1")
        self.ui.cassetteList.setCurrentRow(0)
        self.ui.cassetteList.itemClicked.connect(self.set_cassette)
        self.ui.loadButton.clicked.connect(self.load_cassette)

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

    def set_pd_save_path(self, q=None):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, "PD Save Path")
        if dirname != "":
            command = f'pd savepath {dirname}'
            try:
                specCommand(command, queue=True)
            except:
                traceback.print_exc()

    def set_spec_file(self, q=None):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "SPEC File")

        if filename != "":
            path, name = os.path.split(filename)

            command = f'newfile {path}/{name}'
            try:
                specCommand(command, queue=True)
            except:
                traceback.print_exc()

    @RobotoSafe
    @SampleGrabbed(False)
    @SampleMounted(False)
    def show_setup(self, _):
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
            for i in range(newCassettes):
                newCassette = SampleCassette(self)
                newCassette.sigSampleClicked.connect(self.sample_clicked)
                self.cassettes.append(newCassette)
                self.ui.cassetteStack.addWidget(self.cassettes[i])
                self.ui.cassetteList.addItem(str(i + 1))
            self.ui.cassetteList.setCurrentRow(0)
        self.setupWidget.hide()

    def set_cassette(self, q):
        self.ui.cassetteStack.setCurrentIndex(int(q.text()) - 1)

    @SampleGrabbed(False)
    @SampleMounted(False)
    def load_cassette(self, _):
        self.ui.currentCassetteLabel.setText(self.ui.cassetteList.currentItem().text())
        idx = int(self.ui.currentCassetteLabel.text())
        self.set_state("Loading Cassette")
        move_sample_stage(idx - 1)

    def _current_cassette(self):
        idx = int(self.ui.currentCassetteLabel.text())
        return self.cassettes[idx - 1]

    def sample_clicked(self, data):
        jdata = json.loads(data)
        self.selectedSample = jdata
        self.ui.metaDataText.setText(data)

    @RobotoSafe
    @SampleMounted(False)
    @SampleGrabbed(False)
    def grab_selected_sample(self):
        self.set_state("Grabbing")
        GrabSample(
            self.roboto,
            int(self.selectedSample["column"]),
            int(self.selectedSample["row"])
        )
        self.grabbedSample = deepcopy(self.selectedSample)
        self.set_state("Safe")

    @RobotoSafe
    @SampleGrabbed(True)
    def replace_current(self):
        self.set_state("Replacing")
        ReplaceSample(
            self.roboto,
            int(self.grabbedSample["column"]),
            int(self.grabbedSample["row"])
        )
        self.set_state("Safe")
        self.grabbedSample = None

    @RobotoSafe
    @SampleMounted(False)
    @SampleGrabbed(False)
    def mount_sample(self, _=None):
        self.grab_selected_sample()
        id = self.grabbedSample["metaData"].get("id", "unscanned")
        self.ui.currentSampleLabel.setText(id)
        self.set_state("Mounting")
        MountSample(self.roboto)
        self.set_state("Safe")
        self.mountedSample = deepcopy(self.grabbedSample)
        self.grabbedSample = None
        self.ui.mountButton.setText("Dismount")
        self.ui.mountButton.clicked.disconnect(self.mount_sample)
        self.ui.mountButton.clicked.connect(self.dismount_sample)

    @RobotoSafe
    @SampleMounted(True)
    @SampleGrabbed(False)
    def dismount_sample(self, _=None):
        self.set_state("Dismounting")
        DismountSample(self.roboto)
        self.set_state("Safe")
        self.grabbedSample = deepcopy(self.mountedSample)
        self.mountedSample = None
        self.replace_current()
        self.ui.mountButton.setText("Mount")
        self.ui.mountButton.clicked.disconnect(self.dismount_sample)
        self.ui.mountButton.clicked.connect(self.mount_sample)

    @RobotoSafe
    @SampleGrabbed(False)
    def scan_sample(self, _=None, sampleIDX=None):
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
        if not self.awaitingScan and self.selectedSample is not None:
            self.awaitingScan = True
            self.ui.statusbar.showMessage("Scanning Sample")
            self.grab_selected_sample()
            self.commandQueue.put("CLEAR")
            self.set_state("Scanning")
            self.roboto.MovePose(*BarcodeScanPose)
            code = self.read_scanner_data(1)
            self.set_state("Safe")
            start = time.time()
            # barcode_joints = list(self.roboto.GetJoints())
            # sign = -1
            # while not code:
            #     self.roboto.SetJointVel(5)
            #     barcode_joints[-1] -= 30
            #     barcode_joints[-2] -= 10
            #     # print(barcode_joints)
            #     code = self.scan_grabbed_sample(barcode_joints, code)
            #     if code:
            #         break
            #     barcode_joints[-1] += 30
            #     barcode_joints[-2] += 10
            #     # print(barcode_joints)
            #     code = self.scan_grabbed_sample(barcode_joints, code)
            #     if code:
            #         break
            #     self.roboto.SetJointVel(5)
            #     barcode_joints[-1] -= 30
            #     barcode_joints[-2] += 10
            #     # print(barcode_joints)
            #     code = self.scan_grabbed_sample(barcode_joints, code)
            #     if code:
            #         break
            #     barcode_joints[-1] += 30
            #     barcode_joints[-2] -= 10
            #     # print(barcode_joints)
            #     code = self.scan_grabbed_sample(barcode_joints, code)
            #     if code:
            #         break
            #     self.roboto.MoveLinRelWRF(0, 0, sign * 25, 0, 0, 0)
            #     sign *= -1
            # self.roboto.SetJointVel(speed)
            self.replace_current()
            if code:
                self.ui.metaDataText.setText(code)
                cassette = self._current_cassette()
                self.selectedSample["metaData"]["id"] = code
                if self.metaDataFrame is not None:
                    try:
                        meta = self.metaDataFrame.loc[code].to_dict()
                        self.selectedSample["metaData"].update(meta)
                    except:
                        traceback.print_exc()
                cassette.set_metadata(self.selectedSample)
            self.awaitingScan = False

    @RobotoSafe
    @SampleGrabbed(True)
    def scan_grabbed_sample(self, barcode_joints, code):
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

    @RobotoSafe
    @SampleGrabbed(False)
    @SampleMounted(False)
    def scan_all_samples(self, _):
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

    @SampleMounted(True)
    def run_sample(self, _):
        if self.ui.scanComboBox.currentText() == "ascan":
            motor = self.ui.motorSelectorA.currentText()
            start = self.ui.startSpinBoxA.value()
            stop = self.ui.stopSpinBoxA.value()
            steps = self.ui.stepsSpinBoxA.value()
            count = self.ui.timeSpinBoxA.value()
            print(f"ascan {motor} {start} {stop} {steps} {count}")
            try:
                specCommand(f"ascan {motor} {start} {stop} {steps} {count}", queue=True)
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
        self.set_state("Running")
        wait_until_SPECfinished(5)
        self.ui.statusbar.clearMessage()
        self.set_state("Safe")

    @RobotoSafe
    @SampleGrabbed(False)
    @SampleMounted(False)
    def run_all_samples(self, _):
        pass

    def closeEvent(self, event):
        if self.mountedSample is not None:
            print(f"Closing while sample {self.mountedSample} is mounted")
            self.dismount_sample()
        if self.grabbedSample is not None:
            print(f"Closing while sample {self.grabbedSample} is grabbed")
            self.replace_current()
        print("Deactivating Mr Roboto")
        self.roboto.MoveJoints(0,0,0,0,0,0)
        self.roboto.Delay(3)
        self.roboto.Deactivate()
        self.roboto.Disconnect()
        print("Sending kill command to QKeyLog")
        self.commandQueue.put("QUIT")
        self.keylog.wait()
        print("Closing")
        super(MrRobotoGui, self).closeEvent(event)
