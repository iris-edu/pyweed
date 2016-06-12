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
        MainWindow.resize(982, 771)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.mapFrame = QtGui.QFrame(self.frame)
        self.mapFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.mapFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.mapFrame.setObjectName(_fromUtf8("mapFrame"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.mapFrame)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label = QtGui.QLabel(self.mapFrame)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_3.addWidget(self.label)
        self.verticalLayout_2.addWidget(self.mapFrame)
        self.frame_2 = QtGui.QFrame(self.frame)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame_2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.eventsFrame = QtGui.QFrame(self.frame_2)
        self.eventsFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.eventsFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.eventsFrame.setObjectName(_fromUtf8("eventsFrame"))
        self.gridLayout = QtGui.QGridLayout(self.eventsFrame)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.eventsTable = QtGui.QTableWidget(self.eventsFrame)
        self.eventsTable.setObjectName(_fromUtf8("eventsTable"))
        self.eventsTable.setColumnCount(0)
        self.eventsTable.setRowCount(0)
        self.gridLayout.addWidget(self.eventsTable, 0, 0, 1, 2)
        self.eventsOptions = QtGui.QPushButton(self.eventsFrame)
        self.eventsOptions.setObjectName(_fromUtf8("eventsOptions"))
        self.gridLayout.addWidget(self.eventsOptions, 1, 0, 1, 1)
        self.getEvents = QtGui.QPushButton(self.eventsFrame)
        self.getEvents.setObjectName(_fromUtf8("getEvents"))
        self.gridLayout.addWidget(self.getEvents, 1, 1, 1, 1)
        self.horizontalLayout.addWidget(self.eventsFrame)
        self.stationsFrame = QtGui.QFrame(self.frame_2)
        self.stationsFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.stationsFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.stationsFrame.setObjectName(_fromUtf8("stationsFrame"))
        self.gridLayout_2 = QtGui.QGridLayout(self.stationsFrame)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.stationsTable = QtGui.QTableWidget(self.stationsFrame)
        self.stationsTable.setObjectName(_fromUtf8("stationsTable"))
        self.stationsTable.setColumnCount(0)
        self.stationsTable.setRowCount(0)
        self.gridLayout_2.addWidget(self.stationsTable, 0, 0, 1, 2)
        self.stationOptions = QtGui.QPushButton(self.stationsFrame)
        self.stationOptions.setObjectName(_fromUtf8("stationOptions"))
        self.gridLayout_2.addWidget(self.stationOptions, 1, 0, 1, 1)
        self.getStations = QtGui.QPushButton(self.stationsFrame)
        self.getStations.setObjectName(_fromUtf8("getStations"))
        self.gridLayout_2.addWidget(self.getStations, 1, 1, 1, 1)
        self.horizontalLayout.addWidget(self.stationsFrame)
        self.verticalLayout_2.addWidget(self.frame_2)
        self.verticalLayout.addWidget(self.frame)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.label.setText(_translate("MainWindow", "Map Goes Here", None))
        self.eventsOptions.setText(_translate("MainWindow", "Event Optiopns", None))
        self.getEvents.setText(_translate("MainWindow", "Get Events", None))
        self.stationOptions.setText(_translate("MainWindow", "Station Options", None))
        self.getStations.setText(_translate("MainWindow", "Get Stations", None))

