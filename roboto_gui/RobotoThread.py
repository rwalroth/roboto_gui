import copy
import json
from queue import Queue

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

    def __init__(self, qLock, taskQueue, robotoRequired, parent=None):
        """

        Parameters
        ----------
        qLock : threading.RLock
            Thread safe lock to control access to taskQueue
        """
        super(RobotoThread, self).__init__(parent)
        self.qLock = qLock
        self.taskQueue = taskQueue
        self.robotoRequired = robotoRequired

        self.state = "safe"

        self.mountedSample = None
        self.grabbedSample = None
        self.selectedSample = None
        self.currentCassette = 0

        # QKeyLog Setup
        self.commandQueue = Queue()
        self.tsString = TSString()
        self.keylog = QKeyLog(self.commandQueue, self.tsString, parent=self)
        self.keylog.sigKeyboard.connect(self.new_keyboard)
        self.keylog.sigBuffer.connect(self.handle_buffer)
        self.keylog.start()

        self.roboto = None

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

    def _run(self):
        while True:
            task = None
            with self.qLock:
                if self.taskQueue:
                    task = self.taskQueue.pop(0)
                    self.taskStarted.emit(task)

            if task is not None:
                if task["task"].lower() == "finish":
                    if self.mountedSample is not None:
                        print(f"Closing while sample {self.mountedSample} is mounted")
                        self.dismount_sample()
                    if self.grabbedSample is not None:
                        print(f"Closing while sample {self.grabbedSample} is grabbed")
                        self.replace_current()
                    break

    def run(self):
        try:
            self.roboto = MrRobotoStart()
            try:
                test = list(self.roboto.GetJoints())
            except:
                print("Roboto not able to connect")
            self._run()
        except:
            raise
        finally:
            self.roboto_disconnect()

    def roboto_disconnect(self):
        if self.roboto is not None:
            print("Deactivating Mr Roboto")
            self.roboto.MoveJoints(0,0,0,0,0,0)
            self.roboto.Delay(3)
            self.roboto.Deactivate()
            self.roboto.Disconnect()


