# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QueueWidgetUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(255, 300)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.currentTaskLabel = QtWidgets.QLabel(Form)
        self.currentTaskLabel.setObjectName("currentTaskLabel")
        self.gridLayout.addWidget(self.currentTaskLabel, 0, 1, 1, 2)
        self.moveDownButton = QtWidgets.QPushButton(Form)
        self.moveDownButton.setObjectName("moveDownButton")
        self.gridLayout.addWidget(self.moveDownButton, 2, 2, 1, 1)
        self.queueList = QtWidgets.QListWidget(Form)
        self.queueList.setObjectName("queueList")
        self.gridLayout.addWidget(self.queueList, 1, 0, 1, 3)
        self.deleteButton = QtWidgets.QPushButton(Form)
        self.deleteButton.setCheckable(False)
        self.deleteButton.setChecked(False)
        self.deleteButton.setObjectName("deleteButton")
        self.gridLayout.addWidget(self.deleteButton, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.moveUpButton = QtWidgets.QPushButton(Form)
        self.moveUpButton.setObjectName("moveUpButton")
        self.gridLayout.addWidget(self.moveUpButton, 2, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.currentTaskLabel.setText(_translate("Form", "None"))
        self.moveDownButton.setText(_translate("Form", "v"))
        self.deleteButton.setText(_translate("Form", "x"))
        self.label.setText(_translate("Form", "Current task:"))
        self.moveUpButton.setText(_translate("Form", "^"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())