# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(607, 386)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.mapFrame = QtGui.QFrame(self.splitter)
        self.mapFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.mapFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.mapFrame.setObjectName(_fromUtf8("mapFrame"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.mapFrame)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.mapLabel = QtGui.QLabel(self.mapFrame)
        self.mapLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.mapLabel.setObjectName(_fromUtf8("mapLabel"))
        self.verticalLayout_2.addWidget(self.mapLabel)
        self.eventAndStationFrame = QtGui.QFrame(self.splitter)
        self.eventAndStationFrame.setFrameShape(QtGui.QFrame.NoFrame)
        self.eventAndStationFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.eventAndStationFrame.setObjectName(_fromUtf8("eventAndStationFrame"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.eventAndStationFrame)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.eventsFrame = QtGui.QFrame(self.eventAndStationFrame)
        self.eventsFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.eventsFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.eventsFrame.setObjectName(_fromUtf8("eventsFrame"))
        self.gridLayout_3 = QtGui.QGridLayout(self.eventsFrame)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.eventOptions = QtGui.QPushButton(self.eventsFrame)
        self.eventOptions.setObjectName(_fromUtf8("eventOptions"))
        self.gridLayout_3.addWidget(self.eventOptions, 1, 0, 1, 1)
        self.eventTable = QtGui.QTableWidget(self.eventsFrame)
        self.eventTable.setObjectName(_fromUtf8("eventTable"))
        self.eventTable.setColumnCount(0)
        self.eventTable.setRowCount(0)
        self.gridLayout_3.addWidget(self.eventTable, 0, 0, 1, 2)
        self.getEvent = QtGui.QPushButton(self.eventsFrame)
        self.getEvent.setObjectName(_fromUtf8("getEvent"))
        self.gridLayout_3.addWidget(self.getEvent, 1, 1, 1, 1)
        self.horizontalLayout.addWidget(self.eventsFrame)
        self.stationsFrame = QtGui.QFrame(self.eventAndStationFrame)
        self.stationsFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.stationsFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.stationsFrame.setObjectName(_fromUtf8("stationsFrame"))
        self.gridLayout_4 = QtGui.QGridLayout(self.stationsFrame)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.getStation = QtGui.QPushButton(self.stationsFrame)
        self.getStation.setStyleSheet(_fromUtf8(""))
        self.getStation.setObjectName(_fromUtf8("getStation"))
        self.gridLayout_4.addWidget(self.getStation, 1, 1, 1, 1)
        self.stationsOptions = QtGui.QPushButton(self.stationsFrame)
        self.stationsOptions.setObjectName(_fromUtf8("stationsOptions"))
        self.gridLayout_4.addWidget(self.stationsOptions, 1, 0, 1, 1)
        self.stationsTable = QtGui.QTableWidget(self.stationsFrame)
        self.stationsTable.setObjectName(_fromUtf8("stationsTable"))
        self.stationsTable.setColumnCount(0)
        self.stationsTable.setRowCount(0)
        self.gridLayout_4.addWidget(self.stationsTable, 0, 0, 1, 2)
        self.horizontalLayout.addWidget(self.stationsFrame)
        self.verticalLayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.mapLabel.setText(_translate("MainWindow", "Map Goes Here", None))
        self.eventOptions.setText(_translate("MainWindow", "Event Options", None))
        self.getEvent.setText(_translate("MainWindow", "Get Events", None))
        self.getStation.setText(_translate("MainWindow", "Get Stations", None))
        self.stationsOptions.setText(_translate("MainWindow", "Station Options", None))

