import copy
import json
from queue import Queue
import traceback

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from .mr_roboto.mr_roboto_funcs import *
from .qkeylog import QKeyLog
from .tsstring import TSString


class RobotoThread(QThread):
    taskStarted = pyqtSignal(str)
    taskFinished = pyqtSignal(str)
    sampleScanned = pyqtSignal(str)
    sampleMounted = pyqtSignal(str, bool)
    sampleRunning = pyqtSignal(str, bool)
    createSpecFile = pyqtSignal(str)
    cassetteLoaded = pyqtSignal(str)
    stateChanged = pyqtSignal(str)
    newKeyboard = pyqtSignal(str)

    def __init__(self, taskQueue, robotoRequired, parent=None):
        """

        Parameters
        ----------
        qLock : threading.RLock
            Thread safe lock to control access to taskQueue
        """
        super(RobotoThread, self).__init__(parent)
        self.taskQueue = taskQueue
        self.robotoRequired = robotoRequired

        self.state = "safe"

        self.mountedSample = None
        self.grabbedSample = None
        self.selectedSample = None
        self.currentCassette = 0

        self.roboto = None

        # QKeyLog Setup
        self.commandQueue = Queue()
        self.tsString = TSString()
        self.keylog = QKeyLog(self.commandQueue, self.tsString, parent=self)
        self.keylog.sigKeyboard.connect(self.newKeyboard.emit)
        self.timer = QtCore.QTimer()

    def set_state(self, state):
        self.state = state
        self.stateChanged.emit(state)

    def _check_safe(self, safeState):
        if safeState:
            if self.state.lower() != "safe":
                print(f"Cannot execute, robot not safe")
                return False
        return True

    def _check_grabbed(self, grabbed):
        if grabbed:
            if self.grabbedSample is None:
                print(f"Cannot execute without a sample grabbed")
                return False
        else:
            if self.grabbedSample is not None:
                print(f"Cannot execute with a sample grabbed")
                return False
        return True

    def _check_mounted(self, mounted):
        if mounted:
            if self.mountedSample is None:
                print(f"Cannot execute without a sample mounted")
                return False
        else:
            if self.mountedSample is not None:
                print(f"Cannot execute with a sample mounted")
                return False
        return True

    def _check_cassette(self, cassette):
        if cassette:
            if self.selectedSample["cassette"] != self.currentCassette:
                reply = QMessageBox.question(
                    None,
                    "test",
                    "Scanning this requires loading a new cassette, proceed?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.load_cassette(self.selectedSample["cassette"])
                else:
                    return False
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
            return
        # self.ui.currentCassetteLabel.setText(self.ui.cassetteList.currentItem().text())
        self.set_state("Loading Cassette")
        move_sample_stage(int(idx))
        self.currentCassette = int(idx)
        self.cassetteLoaded.emit(idx)
        self.set_state("Safe")

    # Check state
    def grab_selected_sample(self):
        if not self.check_state():
            return
        self.set_state("Grabbing")
        GrabSample(
            self.roboto,
            int(self.selectedSample["column"]),
            int(self.selectedSample["row"])
        )
        self.grabbedSample = deepcopy(self.selectedSample)
        self.set_state("Safe")

    # Check state
    def replace_current(self):
        if not self.check_state(grabbed=True, mounted=None, cassette=None):
            return
        self.set_state("Replacing")
        ReplaceSample(
            self.roboto,
            int(self.grabbedSample["column"]),
            int(self.grabbedSample["row"])
        )
        self.set_state("Safe")
        self.grabbedSample = None

    # Check state
    def mount_sample(self, _=None):
        if not self.check_state():
            return
        self.grab_selected_sample()
        self.set_state("Mounting")
        MountSample(self.roboto)
        self.set_state("Safe")
        self.mountedSample = copy.deepcopy(self.grabbedSample)
        self.grabbedSample = None
        self.sampleMounted.emit(json.dumps(self.mountedSample))
        code = self.mountedSample["metaData"].get("id", "unscanned")
        self.createSpecFile.emit(code)

    # Check state
    def dismount_sample(self, _=None):
        if not self.check_state(mounted=True, cassette=None):
            return
        self.set_state("Dismounting")
        DismountSample(self.roboto)
        self.set_state("Safe")
        self.grabbedSample = deepcopy(self.mountedSample)
        self.sampleMounted.emit(json.dumps(None))
        self.replace_current()

    # Check state
    def scan_sample(self, cassette):
        if not self.check_state():
            return
        if self.selectedSample is not None:
            self.grab_selected_sample()
            self.commandQueue.put("CLEAR")
            self.set_state("Scanning")
            self.roboto.MovePose(*BarcodeScanPose)
            time.sleep(1)
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
        time.sleep(1)
        code = self.tsString.get_data()
        return code

    def _run(self):
        while True:
            task = self.taskQueue.get()
            print(task)
            self.taskStarted.emit(json.dumps(task))

            if type(task) == dict:
                name = task["task"]
                data = task["data"]
            else:
                name = str(task)
            if name.lower() == "finish":
                if self.mountedSample is not None:
                    print(f"Closing while sample {self.mountedSample} is mounted")
                    self.dismount_sample()
                if self.grabbedSample is not None:
                    print(f"Closing while sample {self.grabbedSample} is grabbed")
                    self.replace_current()
                self.taskQueue.clear()
                break

    def run(self):
        try:
            self.roboto = MrRobotoStart()
            self.keylog.start()
            self.taskQueue.clear()
            try:
                test = list(self.roboto.GetJoints())
            except:
                print("Roboto not able to connect")
            self._run()
        except:
            raise
        finally:
            self.roboto_disconnect()
            print("Sending kill command to QKeyLog")
            self.commandQueue.put("QUIT")
            self.keylog.wait()

    def roboto_disconnect(self):
        if self.roboto is not None:
            print("Deactivating Mr Roboto")
            self.roboto.MoveJoints(0,0,0,0,0,0)
            self.roboto.Delay(3)
            self.roboto.Deactivate()
            self.roboto.Disconnect()


