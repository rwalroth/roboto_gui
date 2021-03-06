import json
from queue import Queue
import traceback
import os
import datetime
from threading import RLock
from collections import deque
from copy import deepcopy

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox

import pandas as pd

# from .mr_roboto.mr_roboto_funcs import *
from .mr_roboto import *
from .sample_gui import Ui_MainWindow
from .sample_cassette import SampleCassette
from .qkeylog import QKeyLog
from .pySSRL_bServer.bServer_funcs import specCommand, wait_until_SPECfinished
from .tsstring import TSString
from .RobotoThread import RobotoThread
from .QueueWidget import QueueWidget
from .CommandLine import CommandLineWidget


class SetupWidget(QWidget):
    sigFinished = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QGridLayout(self)
        self.setLayout(self.layout)
        self.cassettesLabel = QtWidgets.QLabel("Number of cassettes:")
        self.cassettesSpinBox = QtWidgets.QSpinBox()
        self.cassettesSpinBox.setMinimum(1)
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
        self.close()

    def cancel_clicked(self, _):
        self.sigFinished.emit(-1)
        self.close()


class MrRobotoGui(QMainWindow):
    def __init__(self, robotoRequired=True, parent=None):
        super(MrRobotoGui, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.state = "safe"
        self.awaitingScan = False
        self.splash = QtWidgets.QSplashScreen(self)

        self.taskQueue = QueueWidget(self)
        self.taskLayout = QtWidgets.QVBoxLayout()
        self.ui.queueFrame.setLayout(self.taskLayout)
        self.taskLayout.addWidget(self.taskQueue)
        self.commandLine = CommandLineWidget(self)
        self.commandLine.sendButton.setText("Add to queue")
        self.commandLine.sendCommand.connect(self.send_spec_command)
        self.taskLayout.addWidget(self.commandLine)

        self.robotoThread = RobotoThread(self.taskQueue, self)
        # self.robotThread.taskStarted
        # self.robotThread.taskFinished
        self.robotoThread.sampleScanned.connect(self.sample_scanned)
        self.robotoThread.sampleMounted.connect(self._set_mounted_sample)
        # self.robotThread.sampleRunning
        # self.robotoThread.createSpecFile
        self.robotoThread.cassetteLoaded.connect(self.cassette_loaded)
        self.robotoThread.stateChanged.connect(self.set_state)
        self.robotoThread.newKeyboard.connect(self.new_keyboard)
        self.robotoThread.commandNotRun.connect(self.command_not_run)
        self.robotoThread.start()

        self.selectedSample = None

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
        self.ui.currentCassetteLabel.setText("0")
        self.ui.loadButton.clicked.connect(self.load_cassette)
        self.load_cassette()

        # Sample scan pane setup
        self.ui.mountButton.clicked.connect(self.mount_sample)
        self.ui.scanButton.clicked.connect(self.scan_sample)
        self.ui.scanAllButton.clicked.connect(self.scan_all_samples)
        # self.ui.scanAllButton.setEnabled(False)

        # Run pane setup
        self.ui.runButton.clicked.connect(self.run_sample)
        self.ui.runAllButton.clicked.connect(self.run_all_samples)
        # self.ui.runAllButton.setEnabled(False)
        # ascan
        self.ui.stepsSpinBoxA.valueChanged.connect(self.estimate_time_A)
        self.ui.timeSpinBoxA.valueChanged.connect(self.estimate_time_A)
        # pscan
        self.ui.minTimeP.valueChanged.connect(self.estimate_time_P)
        self.ui.maxTimeP.valueChanged.connect(self.estimate_time_P)
        self.ui.timePowerP.valueChanged.connect(self.estimate_time_P)
        self.ui.stepPowerP.valueChanged.connect(self.estimate_time_P)
        self.ui.stepsSpinBoxP.valueChanged.connect(self.estimate_time_P)

        self.setupWidget.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setupWidget.show()

    def set_state(self, state):
        self.state = state
        if state.lower() == "safe":
            self.ui.statusbar.clearMessage()
        else:
            self.ui.statusbar.showMessage(state)
        self.ui.stateLabel.setText(state)

    def command_not_run(self, q):
        self.ui.statusbar.showMessage(q)
        msgBox = QMessageBox()
        msgBox.setText(q + "\nAdjust commands in queue and push play when ready")
        msgBox.exec_()

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
            msgBox = QMessageBox()
            msgBox.setText(f"Invalid path, must be within {self.localDataPath}")
            msgBox.show()
            msgBox.exec_()
            return
        return '~/data/' + dirname.split(self.localDataPath)[-1]

    def send_spec_command(self, command):
        if len(command) > 28:
            label = "Spec: " + command[:25] + "..."
        else:
            label = "Spec: " + command
        self.taskQueue.put(
            label,
            {
                "task": "spec_command",
                "data": command
            }
        )

    def set_pd_save_path(self, q=None):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, "PD Save Path", self.localDataPath)
        if dirname != "":
            remote = self.local_to_remote(dirname)
            if remote is None:
                return
            
            command = f'pd savepath {remote}'
            self.taskQueue.put(
                "Set pd save path",
                {
                    "task": "spec_command",
                    "data": command
                }
            )

    def set_spec_file(self, q=None):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, "SPEC Save Folder", self.localDataPath)
        if dirname != "":
            remote = self.local_to_remote(dirname)
            if remote is not None:
                self.specPath = remote + "/"
                self.taskQueue.put(
                    "New Spec File",
                    {"task": "set_spec_file", "data": remote + "/"}
                )

    # def create_SPEC_file(self, code):
    #     """Create new calibration spec file with date time stamp"""
    #     if code == "unscanned":
    #         row = int(self.mountedSample["row"]) + 1
    #         column = int(self.mountedSample["column"]) + 1
    #         idx = row * 3 + column
    #         cidx = (len(self.cassettes) // 2) + int(self.ui.currentCassetteLabel.text()) + 1
    #         samplenum = "unsc_" + str(1000*cidx + idx)
    #     else:
    #         samplenum = code.split()[-1]
    #     now = datetime.now()
    #     timestamp = now.strftime("%Y-%m-%d-%H%M")
    #     print(f"Sample number is {samplenum}...")
    #     samplename = f"BL21Robot_{samplenum}-{timestamp}"
    #     command = f'newfile {self.specPath}{samplename}'
    #     try:
    #         print(command)
    #         specCommand(command, queue=True)
    #     except:
    #         traceback.print_exc()

    # Check state
    def show_setup(self, _):
        reply = QMessageBox.question(
            None,
            "test",
            "This action will clear task queue, unregister scanner," +
            "clear all scanned samples, and deactivate robot. Proceed?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._end_roboto_thread()
            self.robotoThread.start()
            self.setupWidget.cassettesSpinBox.setValue(len(self.cassettes))
            self.setupWidget.setWindowModality(QtCore.Qt.ApplicationModal)
            self.setupWidget.show()

    def _end_roboto_thread(self):
        self.splash.showMessage("Waiting for thread", 1, QtGui.QColor(255, 255, 255))
        self.splash.show()
        self.taskQueue.put("finish", "finish", True)
        self.robotoThread.wait()
        self.splash.close()

    def register_scanner(self, _):
        self.taskQueue.put("Register Scanner", "register")

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
                newCassette = SampleCassette(self, i - adj)
                newCassette.sigSampleClicked.connect(self.sample_clicked)
                self.cassettes.append(newCassette)
                self.ui.cassetteStack.addWidget(self.cassettes[i])
                self.ui.cassetteList.addItem(str(i - adj))
            self.ui.cassetteList.setCurrentRow(0)

    def set_cassette(self, q):
        self.ui.cassetteStack.setCurrentIndex(
            (len(self.cassettes) // 2) + int(q.text())
        )

    def load_cassette(self):
        idx = int(self.ui.cassetteList.currentItem().text())
        self.taskQueue.put(
            label=f"Load Cassette {idx}",
            task={
                "task": "load_cassette",
                "data": idx
            }
        )

    def cassette_loaded(self, idx):
        print(f"cassette loaded, idx: {idx}")
        self.ui.currentCassetteLabel.setText(idx)

    def _current_cassette(self):
        idx = (len(self.cassettes) // 2) + int(self.ui.currentCassetteLabel.text())
        print(idx)
        return self.cassettes[idx]

    def _selected_cassette(self):
        idx = (len(self.cassettes) // 2) + int(self.ui.cassetteList.currentItem().text())
        print(idx)
        return self.cassettes[idx]

    def sample_clicked(self, data):
        jdata = json.loads(data)
        self.selectedSample = jdata
        self.ui.metaDataText.setText(data)

    def mount_sample(self, _=None):
        if self.selectedSample is not None:
            self.taskQueue.put(
                "Mount sample " + self.get_sample_label(self.selectedSample),
                {
                    "task": "mount",
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

    def dismount_sample(self, _=None):
        self.taskQueue.put("Dismount Sample", "dismount")
        self.ui.mountButton.setText("Mount")
        self.ui.mountButton.clicked.disconnect(self.dismount_sample)
        self.ui.mountButton.clicked.connect(self.mount_sample)

    def get_sample_label(self, sample):
        if sample["cassette"] != int(self.ui.currentCassetteLabel.text()):
            note = '!!'
        else:
            note = ''
        return f"row: {sample['row']} col: {sample['column']} cas: {sample['cassette']}" + note

    def scan_sample(self, _=None, sampleIDX=None):
        if self.selectedSample is not None:
            sampleLabel = self.get_sample_label(self.selectedSample)
            self.taskQueue.put(
                "Scan Sample " + sampleLabel,
                {
                    "task": "scan",
                    "data": deepcopy(self.selectedSample)
                }
            )

    def sample_scanned(self, jsample, code):
        sample = json.loads(jsample)
        self.ui.metaDataText.setText(code)
        if self.metaDataFrame is not None:
            try:
                meta = self.metaDataFrame.loc[code].to_dict()
                print(meta)
                self.ui.metaDataText.setText(json.dumps(meta))
                sample["metaData"].update(meta)
            except KeyError:
                print(f"{code} not found in metadata")
        idx = (len(self.cassettes) // 2) + int(sample["cassette"])
        cassette = self.cassettes[idx]
        cassette.set_metadata(sample)

    def handle_buffer(self, buffer):
        print(buffer)

    # Check state
    def scan_all_samples(self, _):
        cassette = self._selected_cassette()
        for button in cassette.sampleButtons:
            sample = button.to_dict()
            self.taskQueue.put(
                "Scan Sample " + self.get_sample_label(sample),
                {
                    "task": "scan",
                    "data": deepcopy(sample)
                }
            )

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
        command = self._get_spec_command()
        if command is not None:
            self.taskQueue.put(
                "Spec Scan",
                {
                    "task": "spec_scan",
                    "data": command
                }
            )

    def _get_spec_command(self):
        command = None
        if self.ui.scanComboBox.currentText() == "ascan":
            motor = self.ui.motorSelectorA.currentText()
            start = self.ui.startSpinBoxA.value()
            stop = self.ui.stopSpinBoxA.value()
            steps = self.ui.stepsSpinBoxA.value()
            count = self.ui.timeSpinBoxA.value()
            command = f"ascan {motor} {start} {stop} {steps} {count}"
            print(command)
        elif self.ui.scanComboBox.currentText() == "pscan":
            motor = self.ui.motorSelectorP.currentText()
            start = self.ui.startSpinBoxP.value()
            stop = self.ui.stopSpinBoxP.value()
            power1 = self.ui.stepPowerP.value()
            minTime = self.ui.minTimeP.value()
            maxTime = self.ui.maxTimeP.value()
            power2 = self.ui.timePowerP.value()
            steps = self.ui.stepsSpinBoxA.value()
            command = (f"pscan {motor} {start} {stop} {power1} " +
                       f"{minTime} {maxTime} {power2} {steps}")
            print(command)
        return command

    # Check state
    def run_all_samples(self, _):
        cassette = self._selected_cassette()
        command = self._get_spec_command()
        for button in cassette.sampleButtons:
            sample = button.to_dict()
            self.taskQueue.put(
                "Mount Sample " + self.get_sample_label(sample),
                {
                    "task": "mount",
                    "data": deepcopy(sample)
                }
            )
            self.taskQueue.put(
                "Spec Scan",
                {
                    "task": "spec_scan",
                    "data": command
                }
            )
            self.taskQueue.put("Dismount Sample", "dismount")

    def closeEvent(self, event):
        print("Sending finish command to thread")
        splash = QtWidgets.QSplashScreen()
        splash.show()
        splash.showMessage("Closing down roboto thread...", 1, QtCore.Qt.white)
        self.taskQueue.put("Finish", {"task": "finish"}, True)
        self.taskQueue.set_paused(pause=False)
        self.robotoThread.wait()
        splash.finsih()
        print("Closing")
        super(MrRobotoGui, self).closeEvent(event)
