from threading import Lock
from copy import deepcopy


class TSString:

    def __init__(self, val=''):
        self._data = val
        self._lock = Lock()

    def get_data(self):
        with self._lock:
            out = deepcopy(self._data)
        return out

    def set_data(self, newVal):
        with self._lock:
            self._data = newVal

    def append_data(self, data):
        with self._lock:
            self._data += data
