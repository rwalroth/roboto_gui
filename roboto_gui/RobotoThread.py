import copy
from copy import deepcopy
from datetime import datetime
import json
from queue import Queue
import traceback

from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox

# from .mr_roboto.mr_roboto_funcs import *
from .mr_roboto import *
from .qkeylog import QKeyLog
from .tsstring import TSString


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

        # QKeyLog Setup
        self.commandQueue = Queue()
        self.tsString = TSString()
        self.keylog = QKeyLog(self.commandQueue, self.tsString, parent=self)
        self.keylog.sigKeyboard.connect(self.newKeyboard.emit)
        self.timer = QTimer()

    def set_state(self, state):
        self.state = state
        self.stateChanged.emit(state)

    def _check_safe(self, safeState):
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

    def check_state(self, safeState=True, grabbed=False, mounted=False, cassette=True):
        """

        Args:
            cassette (bool, None):
            mounted (bool, None):
            grabbed (bool, None):
            safeState (bool, None):
        """
        if safeState is not None:
            if not self._check_safe(safeState):
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

    def register_scanner(self, _):
        self.commandQueue.put("CLEAR")
        self.commandQueue.put("REGISTER")

    # Check state
    def load_cassette(self, idx):
        if not self.check_state(safeState=None, cassette=None):
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
        if not self.check_state():
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
        if not self.check_state(grabbed=True, mounted=None, cassette=None):
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
        if not self.check_state():
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
        if not self.check_state(mounted=True, cassette=None):
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
        if not self.check_state():
            return -1
        if self.selectedSample is not None:
            self.grab_selected_sample()
            self.commandQueue.put("CLEAR")
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

    # Check state
    def scan_grabbed_sample(self, barcode_joints, code):
        if not self.check_state(grabbed=True, mounted=None, cassette=None):
            return -1
        self.set_state("Scanning")
        self.roboto.MoveJoints(*barcode_joints)
        code = self.read_scanner_data(1)
        self.set_state("Safe")
        return code

    def read_scanner_data(self, timeout):
        time.sleep(timeout)
        code = self.tsString.get_data()
        return code

    def run_sample(self, command):
        if not self.check_state(safeState=True, grabbed=None, mounted=True,
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
            self.taskQueue.wait_for_paused()
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
                self.commandQueue.put("REGISTER")

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
            self.keylog.start()
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
            print("Sending close command to QKeyLog")
            self.commandQueue.put("QUIT")
            self.keylog.wait()

    def roboto_disconnect(self):
        if self.roboto is not None:
            print("Deactivating Mr Roboto")
            self.roboto.MoveJoints(0,0,0,0,0,0)
            self.roboto.Delay(3)
            self.roboto.Deactivate()
            self.roboto.Disconnect()


