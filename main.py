from PyQt5.QtWidgets import QApplication
import os
import sys
import qdarkstyle

from roboto_gui.gui import MrRobotoGui

if __name__ == "__main__":
    app = QApplication(sys.argv)
    os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api=os.environ['PYQTGRAPH_QT_LIB']))
    w = MrRobotoGui()
    w.show()
    sys.exit(app.exec_())
