# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\walroth\Documents\repos\roboto_gui\roboto_gui/sample_gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.3
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(838, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.leftFrame = QtWidgets.QFrame(self.centralwidget)
        self.leftFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.leftFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.leftFrame.setObjectName("leftFrame")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.leftFrame)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.stateFrame = QtWidgets.QFrame(self.leftFrame)
        self.stateFrame.setMaximumSize(QtCore.QSize(16777215, 75))
        self.stateFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.stateFrame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.stateFrame.setLineWidth(0)
        self.stateFrame.setObjectName("stateFrame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.stateFrame)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_4 = QtWidgets.QLabel(self.stateFrame)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)
        self.stateLabel = QtWidgets.QLabel(self.stateFrame)
        self.stateLabel.setObjectName("stateLabel")
        self.gridLayout_2.addWidget(self.stateLabel, 0, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.stateFrame)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        self.currentCassetteLabel = QtWidgets.QLabel(self.stateFrame)
        self.currentCassetteLabel.setObjectName("currentCassetteLabel")
        self.gridLayout_2.addWidget(self.currentCassetteLabel, 2, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.stateFrame)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.currentSampleLabel = QtWidgets.QLabel(self.stateFrame)
        self.currentSampleLabel.setObjectName("currentSampleLabel")
        self.gridLayout_2.addWidget(self.currentSampleLabel, 1, 1, 1, 1)
        self.gridLayout_3.addWidget(self.stateFrame, 0, 0, 1, 2)
        self.cassetteList = QtWidgets.QListWidget(self.leftFrame)
        self.cassetteList.setMaximumSize(QtCore.QSize(25, 16777215))
        self.cassetteList.setObjectName("cassetteList")
        self.gridLayout_3.addWidget(self.cassetteList, 1, 0, 1, 1)
        self.cassetteStack = QtWidgets.QStackedWidget(self.leftFrame)
        self.cassetteStack.setObjectName("cassetteStack")
        self.gridLayout_3.addWidget(self.cassetteStack, 1, 1, 1, 1)
        self.cassetteControlFrame = QtWidgets.QFrame(self.leftFrame)
        self.cassetteControlFrame.setMaximumSize(QtCore.QSize(16777215, 50))
        self.cassetteControlFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.cassetteControlFrame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.cassetteControlFrame.setLineWidth(0)
        self.cassetteControlFrame.setObjectName("cassetteControlFrame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.cassetteControlFrame)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.loadButton = QtWidgets.QPushButton(self.cassetteControlFrame)
        self.loadButton.setObjectName("loadButton")
        self.horizontalLayout_3.addWidget(self.loadButton)
        self.gridLayout_3.addWidget(self.cassetteControlFrame, 2, 0, 1, 2)
        self.horizontalLayout.addWidget(self.leftFrame)
        self.sampleFrame = QtWidgets.QFrame(self.centralwidget)
        self.sampleFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.sampleFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.sampleFrame.setObjectName("sampleFrame")
        self.gridLayout = QtWidgets.QGridLayout(self.sampleFrame)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtWidgets.QFrame(self.sampleFrame)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.mountButton = QtWidgets.QPushButton(self.frame)
        self.mountButton.setObjectName("mountButton")
        self.horizontalLayout_2.addWidget(self.mountButton)
        self.scanButton = QtWidgets.QPushButton(self.frame)
        self.scanButton.setObjectName("scanButton")
        self.horizontalLayout_2.addWidget(self.scanButton)
        self.scanAllButton = QtWidgets.QPushButton(self.frame)
        self.scanAllButton.setObjectName("scanAllButton")
        self.horizontalLayout_2.addWidget(self.scanAllButton)
        self.gridLayout.addWidget(self.frame, 1, 1, 1, 1)
        self.scanStack = QtWidgets.QStackedWidget(self.sampleFrame)
        self.scanStack.setObjectName("scanStack")
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setObjectName("page_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.page_3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_2 = QtWidgets.QLabel(self.page_3)
        self.label_2.setObjectName("label_2")
        self.gridLayout_4.addWidget(self.label_2, 0, 0, 1, 1)
        self.motorSelectorA = QtWidgets.QComboBox(self.page_3)
        self.motorSelectorA.setObjectName("motorSelectorA")
        self.motorSelectorA.addItem("")
        self.gridLayout_4.addWidget(self.motorSelectorA, 0, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.page_3)
        self.label_5.setObjectName("label_5")
        self.gridLayout_4.addWidget(self.label_5, 0, 2, 1, 1)
        self.startSpinBoxA = QtWidgets.QDoubleSpinBox(self.page_3)
        self.startSpinBoxA.setDecimals(4)
        self.startSpinBoxA.setMinimum(-180.0)
        self.startSpinBoxA.setMaximum(180.0)
        self.startSpinBoxA.setObjectName("startSpinBoxA")
        self.gridLayout_4.addWidget(self.startSpinBoxA, 0, 3, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.page_3)
        self.label_6.setObjectName("label_6")
        self.gridLayout_4.addWidget(self.label_6, 0, 4, 1, 1)
        self.stopSpinBoxA = QtWidgets.QDoubleSpinBox(self.page_3)
        self.stopSpinBoxA.setDecimals(4)
        self.stopSpinBoxA.setMinimum(-180.0)
        self.stopSpinBoxA.setMaximum(180.0)
        self.stopSpinBoxA.setObjectName("stopSpinBoxA")
        self.gridLayout_4.addWidget(self.stopSpinBoxA, 0, 5, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.page_3)
        self.label_7.setObjectName("label_7")
        self.gridLayout_4.addWidget(self.label_7, 1, 0, 1, 1)
        self.stepsSpinBoxA = QtWidgets.QSpinBox(self.page_3)
        self.stepsSpinBoxA.setObjectName("stepsSpinBoxA")
        self.gridLayout_4.addWidget(self.stepsSpinBoxA, 1, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.page_3)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 1, 2, 1, 1)
        self.timeSpinBoxA = QtWidgets.QDoubleSpinBox(self.page_3)
        self.timeSpinBoxA.setObjectName("timeSpinBoxA")
        self.gridLayout_4.addWidget(self.timeSpinBoxA, 1, 3, 1, 1)
        self.estimatedTimeA = QtWidgets.QLabel(self.page_3)
        self.estimatedTimeA.setObjectName("estimatedTimeA")
        self.gridLayout_4.addWidget(self.estimatedTimeA, 1, 4, 1, 2)
        self.scanStack.addWidget(self.page_3)
        self.page_4 = QtWidgets.QWidget()
        self.page_4.setObjectName("page_4")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.page_4)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_15 = QtWidgets.QLabel(self.page_4)
        self.label_15.setObjectName("label_15")
        self.gridLayout_5.addWidget(self.label_15, 3, 5, 1, 1)
        self.motorSelectorP = QtWidgets.QComboBox(self.page_4)
        self.motorSelectorP.setObjectName("motorSelectorP")
        self.motorSelectorP.addItem("")
        self.gridLayout_5.addWidget(self.motorSelectorP, 4, 2, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.page_4)
        self.label_14.setObjectName("label_14")
        self.gridLayout_5.addWidget(self.label_14, 3, 3, 1, 1)
        self.maxTimeP = QtWidgets.QDoubleSpinBox(self.page_4)
        self.maxTimeP.setObjectName("maxTimeP")
        self.gridLayout_5.addWidget(self.maxTimeP, 3, 4, 1, 1)
        self.stopSpinBoxP = QtWidgets.QDoubleSpinBox(self.page_4)
        self.stopSpinBoxP.setDecimals(4)
        self.stopSpinBoxP.setObjectName("stopSpinBoxP")
        self.gridLayout_5.addWidget(self.stopSpinBoxP, 0, 4, 1, 1)
        self.stepsSpinBoxP = QtWidgets.QSpinBox(self.page_4)
        self.stepsSpinBoxP.setMaximum(1000)
        self.stepsSpinBoxP.setObjectName("stepsSpinBoxP")
        self.gridLayout_5.addWidget(self.stepsSpinBoxP, 4, 4, 1, 1)
        self.minTimeP = QtWidgets.QDoubleSpinBox(self.page_4)
        self.minTimeP.setObjectName("minTimeP")
        self.gridLayout_5.addWidget(self.minTimeP, 3, 2, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.page_4)
        self.label_11.setObjectName("label_11")
        self.gridLayout_5.addWidget(self.label_11, 0, 3, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.page_4)
        self.label_16.setObjectName("label_16")
        self.gridLayout_5.addWidget(self.label_16, 4, 3, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.page_4)
        self.label_12.setObjectName("label_12")
        self.gridLayout_5.addWidget(self.label_12, 0, 5, 1, 1)
        self.startSpinBoxP = QtWidgets.QDoubleSpinBox(self.page_4)
        self.startSpinBoxP.setDecimals(4)
        self.startSpinBoxP.setObjectName("startSpinBoxP")
        self.gridLayout_5.addWidget(self.startSpinBoxP, 0, 2, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.page_4)
        self.label_10.setObjectName("label_10")
        self.gridLayout_5.addWidget(self.label_10, 0, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.page_4)
        self.label_13.setObjectName("label_13")
        self.gridLayout_5.addWidget(self.label_13, 3, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.page_4)
        self.label_9.setObjectName("label_9")
        self.gridLayout_5.addWidget(self.label_9, 4, 1, 1, 1)
        self.estimatedTimeP = QtWidgets.QLabel(self.page_4)
        self.estimatedTimeP.setObjectName("estimatedTimeP")
        self.gridLayout_5.addWidget(self.estimatedTimeP, 4, 5, 1, 2)
        self.stepPowerP = QtWidgets.QDoubleSpinBox(self.page_4)
        self.stepPowerP.setObjectName("stepPowerP")
        self.gridLayout_5.addWidget(self.stepPowerP, 0, 6, 1, 1)
        self.timePowerP = QtWidgets.QDoubleSpinBox(self.page_4)
        self.timePowerP.setObjectName("timePowerP")
        self.gridLayout_5.addWidget(self.timePowerP, 3, 6, 1, 1)
        self.scanStack.addWidget(self.page_4)
        self.gridLayout.addWidget(self.scanStack, 3, 1, 1, 1)
        self.metaDataText = QtWidgets.QTextEdit(self.sampleFrame)
        self.metaDataText.setReadOnly(True)
        self.metaDataText.setObjectName("metaDataText")
        self.gridLayout.addWidget(self.metaDataText, 0, 1, 1, 1)
        self.frame_3 = QtWidgets.QFrame(self.sampleFrame)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.runButton = QtWidgets.QPushButton(self.frame_3)
        self.runButton.setObjectName("runButton")
        self.horizontalLayout_4.addWidget(self.runButton)
        self.runAllButton = QtWidgets.QPushButton(self.frame_3)
        self.runAllButton.setObjectName("runAllButton")
        self.horizontalLayout_4.addWidget(self.runAllButton)
        self.gridLayout.addWidget(self.frame_3, 4, 1, 1, 1)
        self.scanComboBox = QtWidgets.QComboBox(self.sampleFrame)
        self.scanComboBox.setObjectName("scanComboBox")
        self.scanComboBox.addItem("")
        self.scanComboBox.addItem("")
        self.gridLayout.addWidget(self.scanComboBox, 2, 1, 1, 1)
        self.horizontalLayout.addWidget(self.sampleFrame)
        self.queueFrame = QtWidgets.QFrame(self.centralwidget)
        self.queueFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.queueFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.queueFrame.setObjectName("queueFrame")
        self.horizontalLayout.addWidget(self.queueFrame)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 838, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuStaff_Only = QtWidgets.QMenu(self.menubar)
        self.menuStaff_Only.setObjectName("menuStaff_Only")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSetup = QtWidgets.QAction(MainWindow)
        self.actionSetup.setObjectName("actionSetup")
        self.actionLoadMetadata = QtWidgets.QAction(MainWindow)
        self.actionLoadMetadata.setObjectName("actionLoadMetadata")
        self.actionSavePath = QtWidgets.QAction(MainWindow)
        self.actionSavePath.setObjectName("actionSavePath")
        self.actionSetSpecFile = QtWidgets.QAction(MainWindow)
        self.actionSetSpecFile.setObjectName("actionSetSpecFile")
        self.menuFile.addAction(self.actionLoadMetadata)
        self.menuFile.addAction(self.actionSavePath)
        self.menuFile.addAction(self.actionSetSpecFile)
        self.menuStaff_Only.addAction(self.actionSetup)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuStaff_Only.menuAction())

        self.retranslateUi(MainWindow)
        self.scanStack.setCurrentIndex(0)
        self.scanComboBox.currentIndexChanged['int'].connect(self.scanStack.setCurrentIndex)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_4.setText(_translate("MainWindow", "Mounted Sample ID:"))
        self.stateLabel.setText(_translate("MainWindow", "Unsafe"))
        self.label_3.setText(_translate("MainWindow", "Current Cassette:"))
        self.currentCassetteLabel.setText(_translate("MainWindow", "1"))
        self.label.setText(_translate("MainWindow", "State:"))
        self.currentSampleLabel.setText(_translate("MainWindow", "None"))
        self.loadButton.setText(_translate("MainWindow", "Load Cassette"))
        self.mountButton.setText(_translate("MainWindow", "Mount"))
        self.scanButton.setText(_translate("MainWindow", "Scan"))
        self.scanAllButton.setText(_translate("MainWindow", "Scan All"))
        self.label_2.setText(_translate("MainWindow", "Motor"))
        self.motorSelectorA.setItemText(0, _translate("MainWindow", "tth"))
        self.label_5.setText(_translate("MainWindow", "Start"))
        self.label_6.setText(_translate("MainWindow", "Stop"))
        self.label_7.setText(_translate("MainWindow", "Steps"))
        self.label_8.setText(_translate("MainWindow", "Time"))
        self.estimatedTimeA.setText(_translate("MainWindow", "Estimated time:"))
        self.label_15.setText(_translate("MainWindow", "Power"))
        self.motorSelectorP.setItemText(0, _translate("MainWindow", "tth"))
        self.label_14.setText(_translate("MainWindow", "Max. Time"))
        self.label_11.setText(_translate("MainWindow", "Stop:"))
        self.label_16.setText(_translate("MainWindow", "Steps"))
        self.label_12.setText(_translate("MainWindow", "Power"))
        self.label_10.setText(_translate("MainWindow", "Start:"))
        self.label_13.setText(_translate("MainWindow", "Min. Time"))
        self.label_9.setText(_translate("MainWindow", "Motor:"))
        self.estimatedTimeP.setText(_translate("MainWindow", "Estimated Time:"))
        self.runButton.setText(_translate("MainWindow", "Run"))
        self.runAllButton.setText(_translate("MainWindow", "Run All"))
        self.scanComboBox.setItemText(0, _translate("MainWindow", "ascan"))
        self.scanComboBox.setItemText(1, _translate("MainWindow", "pscan"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuStaff_Only.setTitle(_translate("MainWindow", "Staff Only"))
        self.actionSetup.setText(_translate("MainWindow", "Setup"))
        self.actionLoadMetadata.setText(_translate("MainWindow", "Load Metadata"))
        self.actionSavePath.setText(_translate("MainWindow", "Set PD Save Path"))
        self.actionSetSpecFile.setText(_translate("MainWindow", "Set Spec Path"))
