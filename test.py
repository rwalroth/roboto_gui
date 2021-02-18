import sys
from multiprocessing import active_children
from queue import Queue
from roboto_gui.qkeylog import QKeyLog
from PyQt5.QtWidgets import QApplication, QMainWindow

def myexcepthook(exctype, value, tb):
    for p in active_children():
        print(f"terminating {p}")
        p.terminate()
    sys.__excepthook__(exctype, value, tb)
    sys.exit(-1)

if __name__ == "__main__":
    sys.excepthook = myexcepthook
    app = QApplication(sys.argv)
    mw = QMainWindow()
    log = QKeyLog(Queue(), "", mw)
    log.start()
    mw.show()
    sys.exit(app.exec_())
