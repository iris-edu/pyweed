# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 21:31:01 2016

@author: RowanCallahan
"""

import sys
from PyQt4 import QtGui,QtCore


class DateTimeDialog(QtGui.QDialog):
    def __init__(self, parent=None, windowTitle='Start/End Time'):
        super(DateTimeDialog, self).__init__(parent)
        
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

class Example(QtGui.QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
        
    def initUI(self):               
        
        textEdit = QtGui.QTextEdit()
        self.setCentralWidget(textEdit)

        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        
        contextAction = QtGui.QAction('Settings',self)
        contextAction.triggered.connect(self.openDialog)


        
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('events')
        
        fileMenu.addAction(exitAction)
        fileMenu.addAction(contextAction)


        self.dialogWindow = DateTimeDialog(self, 'Event Start/End Time')
        self.dialogWindow.buttonBox.accepted.connect(self.printDate)
        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Main window')    
        self.show()
   
    @QtCore.pyqtSlot()
    def openDialog(self):
        self.dialogWindow.exec_()
    
    @QtCore.pyqtSlot()
    def printDate(self):
        self.dialogWindow.startTime = self.dialogWindow.startTimeBox.dateTime()
        self.dialogWindow.endTime = self.dialogWindow.endTimeBox.dateTime()        
        print(self.dialogWindow.endTime)
        
        
        

if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)

    main = Example()
    main.show()

    sys.exit(app.exec_())
    
