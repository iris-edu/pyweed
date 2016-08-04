# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

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
        
        # a figure instance to plot on
        self.figure = plt.figure()
    
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
    
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
        
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
        self.mapLabel.setStyleSheet(_fromUtf8(""))
        self.mapLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.mapLabel.setObjectName(_fromUtf8("mapLabel"))
        self.verticalLayout_2.addWidget(self.mapLabel)
        
        self.verticalLayout_2.addWidget(self.toolbar)
        self.verticalLayout_2.addWidget(self.canvas)
        
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
        self.eventOptionsButton = QtGui.QPushButton(self.eventsFrame)
        self.eventOptionsButton.setObjectName(_fromUtf8("eventOptionsButton"))
        self.gridLayout_3.addWidget(self.eventOptionsButton, 1, 0, 1, 1)
        self.eventsTable = QtGui.QTableWidget(self.eventsFrame)
        self.eventsTable.setStyleSheet(_fromUtf8(""))
        self.eventsTable.setShowGrid(False)
        self.eventsTable.setGridStyle(QtCore.Qt.SolidLine)
        self.eventsTable.setObjectName(_fromUtf8("eventsTable"))
        self.eventsTable.setColumnCount(0)
        self.eventsTable.setRowCount(0)
        self.gridLayout_3.addWidget(self.eventsTable, 0, 0, 1, 2)
        self.getEventsButton = QtGui.QPushButton(self.eventsFrame)
        self.getEventsButton.setObjectName(_fromUtf8("getEventsButton"))
        self.gridLayout_3.addWidget(self.getEventsButton, 1, 1, 1, 1)
        self.horizontalLayout.addWidget(self.eventsFrame)
        self.stationsFrame = QtGui.QFrame(self.eventAndStationFrame)
        self.stationsFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.stationsFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.stationsFrame.setObjectName(_fromUtf8("stationsFrame"))
        self.gridLayout_4 = QtGui.QGridLayout(self.stationsFrame)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.getStationsButton = QtGui.QPushButton(self.stationsFrame)
        self.getStationsButton.setStyleSheet(_fromUtf8(""))
        self.getStationsButton.setObjectName(_fromUtf8("getStationsButton"))
        self.gridLayout_4.addWidget(self.getStationsButton, 1, 1, 1, 1)
        self.stationOptionsButton = QtGui.QPushButton(self.stationsFrame)
        self.stationOptionsButton.setObjectName(_fromUtf8("stationOptionsButton"))
        self.gridLayout_4.addWidget(self.stationOptionsButton, 1, 0, 1, 1)
        self.stationsTable = QtGui.QTableWidget(self.stationsFrame)
        self.stationsTable.setStyleSheet(_fromUtf8(""))
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
        self.eventOptionsButton.setText(_translate("MainWindow", "Event Options", None))
        self.getEventsButton.setText(_translate("MainWindow", "Get Events", None))
        self.getStationsButton.setText(_translate("MainWindow", "Get Stations", None))
        self.stationOptionsButton.setText(_translate("MainWindow", "Station Options", None))

