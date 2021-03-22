import copy
from copy import deepcopy
from datetime import datetime
import json
from queue import Queue, Empty
import traceback

import serial
from serial.serialutil import SerialException, PortNotOpenError, SerialTimeoutException
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox

from .mr_roboto import *
from .zebra_ssi import *


class RobotoThread(QThread):
    taskStarted = pyqtSignal(str)
    taskFinished = pyqtSignal(str)
    sampleScanned = pyqtSignal(str, str)
    sampleMounted = pyqtSignal(str)
    sampleRunning = pyqtSignal(str, bool)
    createSpecFile = pyqtSignal(str)
    cassetteLoaded = pyqtSignal(str)
    stateChanged = pyqtSignal(str)
    newKeyboard = pyqtSignal(str)
    commandNotRun = pyqtSignal(str)

    def __init__(self, taskQueue, parent=None):
        """

        Parameters
        ----------
        qLock : threading.RLock
            Thread safe lock to control access to taskQueue
        """
        super(RobotoThread, self).__init__(parent)
        self.taskQueue = taskQueue

        self.state = "safe"

        self.mountedSample = None
        self.grabbedSample = None
        self.selectedSample = None
        self.currentCassette = 0

        self.roboto = None

        self.specPath = ""
        self.scanner = serial.Serial(None, 9600, stopbits=serial.STOPBITS_ONE,
                                     bytesize=serial.EIGHTBITS, timeout=0.1)
        self.scannerBuffer = Queue()
        self.scannerLive = Event()
        self.scannerThread = ScannerThread(self.scanner, self.scannerBuffer,
                                           self.scannerLive)
        self.scannerThread.start()


    def set_state(self, state):
        self.state = state
        self.stateChanged.emit(state)

    def _check_state(self, safeState):
        if safeState:
            if self.state.lower() != "safe":
                print(f"Cannot execute, robot not safe")
                self.commandNotRun.emit(f"Cannot execute, robot not safe")
                return False
        return True

    def _check_grabbed(self, grabbed):
        if grabbed:
            if self.grabbedSample is None:
                print(f"Cannot execute without a sample grabbed")
                self.commandNotRun.emit(f"Cannot execute without a sample grabbed")
                return False
        else:
            if self.grabbedSample is not None:
                print(f"Cannot execute with a sample grabbed")
                self.commandNotRun.emit(f"Cannot execute with a sample grabbed")
                return False
        return True

    def _check_mounted(self, mounted):
        if mounted:
            if self.mountedSample is None:
                print(f"Cannot execute without a sample mounted")
                self.commandNotRun.emit(f"Cannot execute without a sample mounted")
                return False
        else:
            if self.mountedSample is not None:
                print(f"Cannot execute with a sample mounted")
                self.commandNotRun.emit(f"Cannot execute with a sample mounted")
                return False
        return True

    def _check_cassette(self, cassette):
        if cassette:
            if self.selectedSample["cassette"] != self.currentCassette:
                self.load_cassette(self.selectedSample["cassette"])
        return True

    def check_safe(self, safeState=True, grabbed=False, mounted=False, cassette=True):
        """

        Args:
            cassette (bool, None):
            mounted (bool, None):
            grabbed (bool, None):
            safeState (bool, None):
        """
        if safeState is not None:
            if not self._check_state(safeState):
                return False

        if grabbed is not None:
            if not self._check_grabbed(grabbed):
                return False

        if mounted is not None:
            if not self._check_mounted(mounted):
                return False

        if cassette is not None:
            if not self._check_cassette(cassette):
                return False

        return True

    def register_scanner(self, port=None):
        try:
            if port is not None:
                self.scannerLive.clear()
                self.scanner.close()
                self.scanner.port = port
            self.scanner.open()
            self.scannerLive.set()
            send_scanner_message(self.scanner, PARAM_SEND, [0x01, 0xee, 1])
        except (SerialException, PortNotOpenError) as error:
            print(f"Failed to open scanner at port {port}")

    # Check state
    def load_cassette(self, idx):
        if not self.check_safe(safeState=None, cassette=None):
            return -1
        # self.ui.currentCassetteLabel.setText(self.ui.cassetteList.currentItem().text())
        self.set_state("Loading Cassette")
        move_sample_stage(int(idx))
        self.currentCassette = int(idx)
        self.cassetteLoaded.emit(str(idx))
        self.set_state("Safe")
        return 0

    # Check state
    def grab_selected_sample(self):
        if not self.check_safe():
            return -1
        self.set_state("Grabbing")
        GrabSample(
            self.roboto,
            int(self.selectedSample["column"]),
            int(self.selectedSample["row"])
        )
        self.grabbedSample = deepcopy(self.selectedSample)
        self.set_state("Safe")
        return 0

    # Check state
    def replace_current(self):
        if not self.check_safe(grabbed=True, mounted=None, cassette=None):
            return -1
        self.set_state("Replacing")
        ReplaceSample(
            self.roboto,
            int(self.grabbedSample["column"]),
            int(self.grabbedSample["row"])
        )
        self.set_state("Safe")
        self.grabbedSample = None
        return 0

    # Check state
    def mount_sample(self, _=None):
        if not self.check_safe():
            return -1
        self.grab_selected_sample()
        self.set_state("Mounting")
        MountSample(self.roboto)
        self.set_state("Safe")
        self.mountedSample = copy.deepcopy(self.grabbedSample)
        self.grabbedSample = None
        self.sampleMounted.emit(json.dumps(self.mountedSample))
        code = self.mountedSample["metaData"].get("id", "unscanned")
        self.create_SPEC_file(code)
        return 0

    def create_SPEC_file(self, code):
        """Create new calibration spec file with date time stamp"""
        if code == "unscanned":
            row = int(self.mountedSample["row"]) + 1
            column = int(self.mountedSample["column"]) + 1
            idx = row * 3 + column
            cidx = self.mountedSample["cassette"] + 2
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
    def dismount_sample(self, _=None):
        if not self.check_safe(mounted=True, cassette=None):
            return -1
        self.set_state("Dismounting")
        DismountSample(self.roboto)
        self.set_state("Safe")
        self.grabbedSample = deepcopy(self.mountedSample)
        self.mountedSample = None
        self.sampleMounted.emit(json.dumps(None))
        self.replace_current()
        return 0

    # Check state
    def scan_sample(self):
        if not self.check_safe():
            return -1
        if self.selectedSample is not None:
            self.grab_selected_sample()
            self.clear_scanner_buffer()
            self.set_state("Scanning")
            MovePose(self.roboto, BarcodeScanPose)
            time.sleep(1)
            self.set_state("Safe")
            self.replace_current()
            rawCode = self.read_scanner_data(1)
            if rawCode:
                code = rawCode.split('\n')[0]
                self.selectedSample["metaData"]["id"] = code
                self.sampleScanned.emit(json.dumps(self.selectedSample), code)
        return 0

    def clear_scanner_buffer(self):
        try:
            self.scanner.reset_output_buffer()
            self.scanner.reset_input_buffer()
            while not self.scannerBuffer.empty():
                try:
                    self.scannerBuffer.get(False)
                    self.scannerBuffer.task_done()
                except Empty:
                    continue
        except (SerialException, PortNotOpenError):
            print("Failed to clear buffer")

    def read_scanner_data(self, timeout):
        try:
            messageBytes = self.scannerBuffer.get(timeout=timeout)
            print(messageBytes)
            message = format_scanner_reply(messageBytes)
            if message["opcode"] == DECODE_DATA:
                return message["data"][1:].decode("ascii")
            else:
                print(message)
        except Empty:
            print("Scanner timeout")
        return ""

    def run_sample(self, command):
        if not self.check_safe(safeState=True, grabbed=None, mounted=True,
                               cassette=None):
            return -1
        try:
            SPEC_startspin()
            specCommand(command, queue=True)
            SPEC_stopspin()
            self._wait_for_spec()
        except:
            traceback.print_exc()
            return -1
        return 0

    def _wait_for_spec(self):
        self.set_state("Waiting for SPEC")
        wait_until_SPECfinished(5)
        self.set_state("Safe")

    def _run(self):
        while True:
            task, label = self.taskQueue.get()
            print(task)
            self.taskStarted.emit(json.dumps(task))

            if type(task) == dict:
                name = task["task"]
                data = task.get("data", None)
            else:
                name = str(task)
                data = None
            name = name.lower()

            result = 0

            if name.lower() == "finish":
                self.finish()
                break

            elif name == "register":
                self.register_scanner(data)

            elif name == "load_cassette":
                result = self.load_cassette(data)

            elif name == "mount":
                self.selectedSample = data
                result = self.mount_sample()

            elif name == "dismount":
                result = self.dismount_sample()

            elif name == "scan":
                self.selectedSample = data
                result = self.scan_sample()

            elif name == "spec_scan":
                result = self.run_sample(data)

            elif name == "spec_command":
                specCommand(data, queue=True)
                self._wait_for_spec()

            elif name == "set_spec_file":
                self.specPath = data

            if result == 0:
                self.taskFinished.emit(json.dumps(task))
                self.taskQueue.clear_task_label()
            else:
                self.taskQueue.set_paused(True)
                self.taskQueue.put(label, task, doNext=True)

    def finish(self):
        if self.mountedSample is not None:
            print(f"Closing while sample {self.mountedSample} is mounted")
            self.dismount_sample()
        if self.grabbedSample is not None:
            print(f"Closing while sample {self.grabbedSample} is grabbed")
            self.replace_current()
        self.taskQueue.clear()

    def run(self):
        try:
            self.register_scanner()
            self.taskQueue.clear()
            self.roboto = MrRobotoStart()
            if not NOCONNECT_IMPORTED:
                try:
                    test = list(self.roboto.GetJoints())
                except:
                    print("Roboto not able to connect")
            self._run()
        except:
            raise
        finally:
            self.roboto_disconnect()
            self.close_scanner()

    def close_scanner(self):
        self.scannerLive.clear()
        self.scannerThread.exit_event.set()
        self.scanner.close()
        self.scannerThread.join()

    def roboto_disconnect(self):
        if self.roboto is not None:
            print("Deactivating Mr Roboto")
            self.roboto.MoveJoints(0,0,0,0,0,0)
            self.roboto.Delay(3)
            self.roboto.Deactivate()
            self.roboto.Disconnect()


