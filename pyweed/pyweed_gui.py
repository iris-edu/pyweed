# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 13:51:59 2016

@author: RowanCallahan
"""

from __future__ import (absolute_import, division, print_function)

import sys
import string

from PyQt4 import QtCore
from PyQt4 import QtGui

import EventOptionsDialog
import StationOptionsDialog
import MainWindow

from events import Events
from stations import Stations
from utils import MyDoubleValidator
from pyweed_style import stylesheet


class EventOptionsDialog(QtGui.QDialog, EventOptionsDialog.Ui_EventOptionsDialog):
    """Dialog window for event options used in creating a webservice query."""
    def __init__(self, parent=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Start/End Time')

        # Initialize the date selectors
        self.starttimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.endtimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.starttimeDateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.endtimeDateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime())
        
        # Set validators for input fields
        self.minmagLineEdit.setValidator(MyDoubleValidator(0.0,10.0,2,self.minmagLineEdit))        
        self.maxmagLineEdit.setValidator(MyDoubleValidator(0.0,10.0,2,self.maxmagLineEdit))        
        self.mindepthLineEdit.setValidator(MyDoubleValidator(0.0,6371.0,2,self.mindepthLineEdit))        
        self.maxdepthLineEdit.setValidator(MyDoubleValidator(0.0,6371.0,2,self.maxdepthLineEdit))        
        self.minlonLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.minlonLineEdit))        
        self.maxlonLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.maxlonLineEdit))        
        self.minlatLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.minlatLineEdit))        
        self.maxlatLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.maxlatLineEdit))        
        
        # Set default values for input fields
        self.minmagLineEdit.setText('4.0')
        self.maxmagLineEdit.setText('10.0')
        self.mindepthLineEdit.setText('0.0')
        self.maxdepthLineEdit.setText('6371.0')
        self.minlonLineEdit.setText('-180.0')
        self.maxlonLineEdit.setText('180.0')
        self.minlatLineEdit.setText('-90.0')
        self.maxlatLineEdit.setText('90.0')
        
        # connect the close button to the close slot
        self.closeButton.clicked.connect(self.close)


    @QtCore.pyqtSlot()    
    def getOptions(self):
        """
        Return a dictionary containing everything specified in the EventOptionsDialog.
        All dictionary values are properly formatted for use in building an event service URL.
        """
        options = {}        
        
        # times, magnitudes and depths are all guaranteed to be present
        options['starttime'] = str(self.starttimeDateTimeEdit.text()).rstrip(' UTC').replace(' ','T')
        options['endtime'] = str(self.endtimeDateTimeEdit.text()).rstrip(' UTC').replace(' ','T')
        options['minmag'] = str(self.minmagLineEdit.text())
        options['maxmag'] = str(self.maxmagLineEdit.text())
        options['mindepth'] = str(self.mindepthLineEdit.text())
        options['maxdepth'] = str(self.maxdepthLineEdit.text())
        
        # catalog, type, and lat-lon ranges are optional
        if str(self.catalogComboBox.currentText()) != 'All Catalogs':
            options['catalog'] = str(self.type.currentText())
        if str(self.typeComboBox.currentText()) != 'All Types':
            options['type'] = str(self.type.currentText())            
        if str(self.minlatLineEdit.text()) != '':
            options['minlat'] = str(self.minlatLineEdit.text())            
        if str(self.maxlatLineEdit.text()) != '':
            options['maxlat'] = str(self.maxlatLineEdit.text())            
        if str(self.minlonLineEdit.text()) != '':
            options['minlon'] = str(self.minlonLineEdit.text())            
        if str(self.maxlonLineEdit.text()) != '':
            options['maxlon'] = str(self.maxlonLineEdit.text())
            
        return options


class StationOptionsDialog(QtGui.QDialog, StationOptionsDialog.Ui_StationOptionsDialog):
    """Dialog window for station options used in creating a webservice query."""
    def __init__(self, parent=None, windowTitle='Start/End Time'):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Start/End Time')

        # Initialize the date selectors
        self.starttimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.endtimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.starttimeDateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.endtimeDateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime())
        
        # Set validators for input fields
        self.minlonLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.minlonLineEdit))        
        self.maxlonLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.maxlonLineEdit))        
        self.minlatLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.minlatLineEdit))        
        self.maxlatLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.maxlatLineEdit))        
        
        # Set default values for input fields
        self.networkLineEdit.setText('_GSN')
        self.stationLineEdit.setText('*')
        self.locationLineEdit.setText('*')
        self.channelLineEdit.setText('?HZ')
        self.minlonLineEdit.setText('-180.0')
        self.maxlonLineEdit.setText('180.0')
        self.minlatLineEdit.setText('-90.0')
        self.maxlatLineEdit.setText('90.0')

        # connect the close button to the close slot
        self.closeButton.clicked.connect(self.close)


    @QtCore.pyqtSlot()    
    def getOptions(self):
        """
        Return a dictionary containing everything specified in the EventOptionsDialog.
        All dictionary values are properly formatted for use in building an event service URL.
        """
        options = {}        
        
        # times, magnitudes and depths are all guaranteed to be present
        options['starttime'] = str(self.starttimeDateTimeEdit.text()).rstrip(' UTC').replace(' ','T')
        options['endtime'] = str(self.endtimeDateTimeEdit.text()).rstrip(' UTC').replace(' ','T')
        
        # SNCL and lat-lon ranges are optional
        if str(self.networkLineEdit.text()) != '':
            options['network'] = str(self.networkLineEdit.text())            
        if str(self.networkLineEdit.text()) != '':
            options['station'] = str(self.stationLineEdit.text())            
        if str(self.stationLineEdit.text()) != '':
            options['location'] = str(self.locationLineEdit.text())            
        if str(self.locationLineEdit.text()) != '':
            options['channel'] = str(self.channelLineEdit.text())            
        if str(self.channelLineEdit.text()) != '':
            options['minlat'] = str(self.minlatLineEdit.text())            
        if str(self.maxlatLineEdit.text()) != '':
            options['maxlat'] = str(self.maxlatLineEdit.text())            
        if str(self.minlonLineEdit.text()) != '':
            options['minlon'] = str(self.minlonLineEdit.text())            
        if str(self.maxlonLineEdit.text()) != '':
            options['maxlon'] = str(self.maxlonLineEdit.text())
            
        return options


class MainWindow(QtGui.QMainWindow, MainWindow.Ui_MainWindow):
    
    def __init__(self,parent=None):

        super(self.__class__, self).__init__()
        self.setupUi(self)
        
        # Events
        self.eventOptionsDialog = EventOptionsDialog(self)        
        self.eventsHandler = Events()        
        self.eventsTable.setSortingEnabled(True)
        self.eventsTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # Stations
        self.stationOptionsDialog = StationOptionsDialog(self)
        self.stationsHandler = Stations()        
        self.stationsTable.setSortingEnabled(True)
        self.stationsTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # Connect the buttons so that they open the dialog
        self.eventOptionsButton.pressed.connect(self.eventOptionsDialog.show)
        self.stationOptionsButton.pressed.connect(self.stationOptionsDialog.show)
        self.getEventsButton.pressed.connect(self.queryEvents)
        self.getStationsButton.pressed.connect(self.queryStations)
        
        self.setWindowTitle('Main window')    
        self.show()
   
    @QtCore.pyqtSlot()
    def queryEvents(self):
        # Get events and subset to desired columns
        parameters = self.eventOptionsDialog.getOptions()
        # TODO:  handle errors when querying events
        eventsDF = self.eventsHandler.query(parameters=parameters)
        eventsDF = eventsDF[['Time','Latitude','Longitude','Depth/km','MagType','Magnitude']]
        
        self.eventsTable.setRowCount(eventsDF.shape[0])
        self.eventsTable.setColumnCount(eventsDF.shape[1])
        self.eventsTable.setHorizontalHeaderLabels(eventsDF.columns.tolist())
        self.eventsTable.verticalHeader().hide()
        
        for i in range(eventsDF.shape[0]):
            for j in range(eventsDF.shape[1]):
                # Guarantee that all elements are convenrted to strings
                self.eventsTable.setItem(i, j, QtGui.QTableWidgetItem(str(eventsDF.iat[i,j])))

        # Tighten up the table
        self.eventsTable.resizeColumnsToContents()
        self.eventsTable.resizeRowsToContents()
        
        ## TODO:  Remove console dump
        #print(eventsDF)

    @QtCore.pyqtSlot()
    def queryStations(self):
        # Get stations and subset to desired columns
        parameters = self.stationOptionsDialog.getOptions()
        # TODO:  handle errors when querying stations
        stationsDF = self.stationsHandler.query(parameters=parameters)
        stationsDF = stationsDF[['Network','Station','Location','Channel','Latitude','Longitude']]
        
        self.stationsTable.setRowCount(stationsDF.shape[0])
        self.stationsTable.setColumnCount(stationsDF.shape[1])
        self.stationsTable.setHorizontalHeaderLabels(stationsDF.columns.tolist())
        self.stationsTable.verticalHeader().hide()
        
        for i in range(stationsDF.shape[0]):
            for j in range(stationsDF.shape[1]):
                # Guarantee that all elements are convenrted to strings
                self.stationsTable.setItem(i, j, QtGui.QTableWidgetItem(str(stationsDF.iat[i,j])))

        # Tighten up the table
        self.stationsTable.resizeColumnsToContents()
        self.stationsTable.resizeRowsToContents()
        
        ## TODO:  Remove console dump
        #print(stationsDF)
           
        
        
if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    GUI = MainWindow()
    sys.exit(app.exec_())
    
