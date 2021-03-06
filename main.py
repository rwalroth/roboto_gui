from multiprocessing import active_children

from PyQt5.QtWidgets import QApplication
import os
import sys
import qdarkstyle

from roboto_gui.gui import MrRobotoGui


def myexcepthook(exctype, value, tb):
    for p in active_children():
        print(f"terminating {p}")
        p.terminate()
    sys.__excepthook__(exctype, value, tb)
    sys.exit(-1)


if __name__ == "__main__":
    sys.excepthook = myexcepthook
    app = QApplication(sys.argv)
    os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api=os.environ['PYQTGRAPH_QT_LIB']))
    w = MrRobotoGui(robotoRequired=False)
    w.show()
    sys.exit(app.exec_())
