# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 13:51:59 2016

@author: RowanCallahan
"""


import sys
from PyQt4 import QtGui,QtCore



class EventsDialog(QtGui.QDialog):
    """
    This is the event Dialog window, we will call it later in the main loop.
    """
    def __init__(self, parent=None, windowTitle='Start/End Time'):
        super(EventsDialog, self).__init__(parent)
        
        # create the ok/cancel button box
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
        
        # setup the date selectors
        self.startTimeBox = QtGui.QDateTimeEdit(self)
        self.startTimeBox.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.endTimeBox = QtGui.QDateTimeEdit(self)
        self.endTimeBox.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.startTime = self.startTimeBox.dateTime()
        self.endTime = self.endTimeBox.dateTime()

        # add the widgets to a vertical layour
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.startTimeBox)
        self.verticalLayout.addWidget(self.endTimeBox)
        self.verticalLayout.addWidget(self.buttonBox)
        self.setWindowTitle(windowTitle)

class StationsDialog(QtGui.QDialog):
    def __init__(self, parent=None, windowTitle='Start/End Time'):
        super(StationsDialog, self).__init__(parent)
        
        # create the ok/cancel button box
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
        
        # setup the date selectors
        self.startTimeBox = QtGui.QDateTimeEdit(self)
        self.startTimeBox.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.endTimeBox = QtGui.QDateTimeEdit(self)
        self.endTimeBox.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.startTime = self.startTimeBox.dateTime()
        self.endTime = self.endTimeBox.dateTime()

        # add the widgets to a vertical layour
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.startTimeBox)
        self.verticalLayout.addWidget(self.endTimeBox)
        self.verticalLayout.addWidget(self.buttonBox)
        self.setWindowTitle(windowTitle)


class BrowserWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(BrowserWindow, self).__init__()
        
        self.initUI()
        
        
    def initUI(self):               
        
        # central widget, main window is a complicated class that allows toolbars and other nice goodies but first we need to make sure we have a sandbox that we can put all our widgets and other stuff intowithout it being unalbe to write into
        self.centralWidget= QtGui.QWidget()
        self.setCentralWidget(self.centralWidget)

        # set the top and bottom frames that will contain the map on top and both the information logs on bottom        
        
        self.mainMapFrame = QtGui.QFrame(self)
        self.informationLogFrame = QtGui.QFrame(self)
        self.verticalOverallBox = QtGui.QVBoxLayout()
        # format and position the widgets to the main window
        eventStateButton = QtGui.QPushButton("Show Event State")
        stationStateButton = QtGui.QPushButton("Show Station State")
        statePrintButtonsBox = QtGui.QHBoxLayout()
        statePrintButtonsBox.addWidget(eventStateButton)
        statePrintButtonsBox.addWidget(stationStateButton)
        
        
        eventStateList = QtGui.QListWidget()
        stationStateList = QtGui.QListWidget()
        statePrintBox = QtGui.QHBoxLayout()
        statePrintBox.addWidget(eventStateList)
        statePrintBox.addWidget(stationStateList)
        
        
        verticalInformationBox = QtGui.QVBoxLayout()
        verticalInformationBox.addLayout(statePrintBox)
        verticalInformationBox.addLayout(statePrintButtonsBox)
        self.informationLogFrame.setLayout(verticalInformationBox)
        
        
        mapInformationSplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        mapInformationSplitter.addWidget(self.mainMapFrame)
        mapInformationSplitter.addWidget(self.informationLogFrame)
        self.verticalOverallBox.addWidget(mapInformationSplitter)
        
        self.centralWidget.setLayout(self.verticalOverallBox)
     
        # create the options for the file menu bar
        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        
        eventDialogAction = QtGui.QAction('Event Search Settings',self)
        eventDialogAction.triggered.connect(self.openEventsDialog)
        stationsDialogAction= QtGui.QAction('Station Search Settings',self)
        stationsDialogAction.triggered.connect(self.openStationsDialog)

        #set up the menu bar and add the actions and menus
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('events')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(eventDialogAction)
        fileMenu.addAction(stationsDialogAction)
      
        self.eventsDialogWindow = EventsDialog(self, 'Event Start/End Time')
        self.eventsDialogWindow.buttonBox.accepted.connect(self.printDate)
        
        self.stationsDialogWindow = StationsDialog(self, 'Station Start/End Time')
        self.stationsDialogWindow.buttonBox.accepted.connect(self.printDate)



        self.setWindowTitle('Main window')    
        self.show()
   
    @QtCore.pyqtSlot()
    def openEventsDialog(self):
       self.eventsDialogWindow.exec_()

    @QtCore.pyqtSlot()
    def openStationsDialog(self):
       self.stationsDialogWindow.exec_()
    
    @QtCore.pyqtSlot()
    def printDate(self):
        self.eventsDialogWindow.startTime = self.eventsDialogWindow.startTimeBox.dateTime()
        self.eventsDialogWindow.endTime = self.eventsDialogWindow.endTimeBox.dateTime()        
        print(self.eventsDialogWindow.endTime)
        
        
        
        
if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)

    main = BrowserWindow()
    main.show()

    sys.exit(app.exec_())
    
