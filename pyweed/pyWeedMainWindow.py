# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 13:51:59 2016

@author: RowanCallahan
"""

from __future__ import (absolute_import, division, print_function)

import sys

from PyQt4 import QtCore, QtGui

import eventOptions
import mainWindow

from events import Events


class EventsDialog(QtGui.QDialog, eventOptions.Ui_Dialog):
    """Dialog window for events options."""
    def __init__(self, parent=None, windowTitle='Start/End Time'):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        # setup title and the date selectors
        self.setWindowTitle(windowTitle)
        self.endDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.startDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.startDateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.endDateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime())
        
        # connect the close button to the clsoe slot
        self.closeButton.clicked.connect(self.close)


class StationsDialog(QtGui.QDialog):
    """Dialog window for stations options."""
    def __init__(self, parent=None, windowTitle='Start/End Time'):
        super(StationsDialog, self).__init__(parent)
        
        # create the ok/cancel button box
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
        
        # setup the date selectors
        self.startDateTimeEdit = QtGui.QDateTimeEdit(self)
        self.startDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.endDateTimeEdit = QtGui.QDateTimeEdit(self)
        self.endDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.startTime = self.startDateTimeEdit.dateTime()
        self.endTime = self.endDateTimeEdit.dateTime()

        # add the widgets to a vertical layour
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.startDateTimeEdit)
        self.verticalLayout.addWidget(self.endDateTimeEdit)
        self.verticalLayout.addWidget(self.buttonBox)
        self.setWindowTitle(windowTitle)


class MainWindow(QtGui.QMainWindow, mainWindow.Ui_MainWindow):
    
    def __init__(self,parent=None):

        super(self.__class__, self).__init__()
        self.setupUi(self)
        
        
        
        self.eventsDialogWindow = EventsDialog(self, 'Event Start/End Time')        
        self.stationsDialogWindow = StationsDialog(self, 'Station Start/End Time')
        
        # connect the buttons so that they open the dialog
        self.eventOptions.pressed.connect(self.eventsDialogWindow.show)
        self.stationsOptions.pressed.connect(self.openStationsDialog)
        
        
        self.setWindowTitle('Main window')    
        self.show()
   
    @QtCore.pyqtSlot()
    def openEventsDialog(self):        
        self.eventsDialogWindow.exec_()

    @QtCore.pyqtSlot()
    def openStationsDialog(self):
        self.stationsDialogWindow.show()

        
        
        
        
if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    GUI = MainWindow()
    sys.exit(app.exec_())
    
