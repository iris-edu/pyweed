#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

# Basic packages
import sys
import string

# PyQt4 packages
from PyQt4 import QtCore
from PyQt4 import QtGui

import EventQueryDialog
import StationQueryDialog
import MainWindow

from pyweed_style import stylesheet

# Pyweed PyQt4 enhancements
from MyDoubleValidator import MyDoubleValidator
from MyNumericTableWidgetItem import MyNumericTableWidgetItem

# Pyweed components
from events import Events
from stations import Stations
from seismap import Seismap


class EventQueryDialog(QtGui.QDialog, EventQueryDialog.Ui_EventQueryDialog):
    """Dialog window for event options used in creating a webservice query."""
    def __init__(self, parent=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Start/End Time')
        
        # Get a reference to the MainWindow map
        self.seismap = parent.seismap
        self.map_figure = parent.map_figure

        # Create buttonGroups
        self.timeButtonGroup = QtGui.QButtonGroup()
        self.timeButtonGroup.addButton(self.timeBetweenRadioButton,1)
        self.timeButtonGroup.addButton(self.timeDuringStationsRadioButton,2)
        
        self.locationButtonGroup = QtGui.QButtonGroup()
        self.locationButtonGroup.addButton(self.locationRangeRadioButton,1)
        self.locationButtonGroup.addButton(self.locationDistanceFromPointRadioButton,2)
        self.locationButtonGroup.addButton(self.locationDistanceFromStationsRadioButton,3)

        # Initialize the date selectors
        self.starttimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.endtimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        today = QtCore.QDateTime.currentDateTime()
        monthAgo = today.addMonths(-1)
        self.starttimeDateTimeEdit.setDateTime(monthAgo)
        self.endtimeDateTimeEdit.setDateTime(today)
        
        # Set validators for input fields # TODO:  What are appropriate valid ranges?
        self.minmagLineEdit.setValidator(MyDoubleValidator(0.0,10.0,2,self.minmagLineEdit))        
        self.maxmagLineEdit.setValidator(MyDoubleValidator(0.0,10.0,2,self.maxmagLineEdit))        
        self.mindepthLineEdit.setValidator(MyDoubleValidator(0.0,6371.0,2,self.mindepthLineEdit))        
        self.maxdepthLineEdit.setValidator(MyDoubleValidator(0.0,6371.0,2,self.maxdepthLineEdit))        
        self.locationRangeWestLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.locationRangeWestLineEdit))        
        self.locationRangeEastLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.locationRangeEastLineEdit))        
        self.locationRangeSouthLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.locationRangeSouthLineEdit))        
        self.locationRangeNorthLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.locationRangeNorthLineEdit))
        self.distanceFromPointMinRadiusLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.distanceFromPointMinRadiusLineEdit))        
        self.distanceFromPointMaxRadiusLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.distanceFromPointMaxRadiusLineEdit))        
        self.distanceFromPointEastLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.distanceFromPointEastLineEdit))        
        self.distanceFromPointNorthLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.distanceFromPointNorthLineEdit))
        
        # Set default values for input fields # TODO:  What are appropriate valid defaults?
        self.minmagLineEdit.setText('4.0')
        self.maxmagLineEdit.setText('10.0')
        self.mindepthLineEdit.setText('0.0')
        self.maxdepthLineEdit.setText('6371.0')
        self.locationRangeWestLineEdit.setText('-180.0')
        self.locationRangeEastLineEdit.setText('180.0')
        self.locationRangeSouthLineEdit.setText('-90.0')
        self.locationRangeNorthLineEdit.setText('90.0')
        self.distanceFromPointMinRadiusLineEdit.setText('0.0')
        self.distanceFromPointMaxRadiusLineEdit.setText('90.0')
        self.distanceFromPointEastLineEdit.setText('0.0')
        self.distanceFromPointNorthLineEdit.setText('0.0')
        
        
    @QtCore.pyqtSlot()    
    def getOptions(self):
        """
        Return a dictionary containing everything specified in the EventQueryDialog.
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
        #if str(self.catalogComboBox.currentText()) != 'All Catalogs':
            #options['catalog'] = str(self.type.currentText())
        if str(self.magtypeComboBox.currentText()) != 'All Types':
            options['magtype'] = str(self.magtypeComboBox.currentText()) 
        if self.locationRangeRadioButton.isChecked():         
            if str(self.locationRangeWestLineEdit.text()) != '':
                options['minlon'] = str(self.locationRangeWestLineEdit.text())            
            if str(self.locationRangeEastLineEdit.text()) != '':
                options['maxlon'] = str(self.locationRangeEastLineEdit.text())            
            if str(self.locationRangeSouthLineEdit.text()) != '':
                options['minlat'] = str(self.locationRangeSouthLineEdit.text())            
            if str(self.locationRangeNorthLineEdit.text()) != '':
                options['maxlat'] = str(self.locationRangeNorthLineEdit.text())
        if self.locationDistanceFromPointRadioButton.isChecked():         
            if str(self.distanceFromPointMinRadiusLineEdit.text()) != '':
                options['minradius'] = str(self.distanceFromPointMinRadiusLineEdit.text())            
            if str(self.distanceFromPointMaxRadiusLineEdit.text()) != '':
                options['maxradius'] = str(self.distanceFromPointMaxRadiusLineEdit.text())            
            if str(self.distanceFromPointEastLineEdit.text()) != '':
                options['lon'] = str(self.distanceFromPointEastLineEdit.text())            
            if str(self.distanceFromPointNorthLineEdit.text()) != '':
                options['lat'] = str(self.distanceFromPointNorthLineEdit.text())
            
        return options


class StationQueryDialog(QtGui.QDialog, StationQueryDialog.Ui_StationQueryDialog):
    """Dialog window for station options used in creating a webservice query."""
    def __init__(self, parent=None, windowTitle='Start/End Time'):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Start/End Time')

        # Get a reference to the MainWindow map
        self.seismap = parent.seismap
        self.map_figure = parent.map_figure

        # Initialize the date selectors
        self.starttimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.endtimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        today = QtCore.QDateTime.currentDateTime()
        monthAgo = today.addMonths(-1)
        self.starttimeDateTimeEdit.setDateTime(monthAgo)
        self.endtimeDateTimeEdit.setDateTime(today)
        
        # Set validators for input fields # TODO:  What are appropriate valid ranges?
        self.locationRangeSouthLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.locationRangeSouthLineEdit))        
        self.locationRangeEastLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.locationRangeEastLineEdit))        
        self.locationRangeSouthLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.locationRangeSouthLineEdit))        
        self.locationRangeNorthLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.locationRangeNorthLineEdit))        
        self.distanceFromPointMinRadiusLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.distanceFromPointMinRadiusLineEdit))        
        self.distanceFromPointMaxRadiusLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.distanceFromPointMaxRadiusLineEdit))        
        self.distanceFromPointEastLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.distanceFromPointEastLineEdit))        
        self.distanceFromPointNorthLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.distanceFromPointNorthLineEdit))
        
        # Set default values for input fields # TODO:  What are appropriate valid defaults?
        self.networkLineEdit.setText('_GSN')
        self.stationLineEdit.setText('*')
        self.locationLineEdit.setText('*')
        self.channelLineEdit.setText('?HZ')
        self.locationRangeWestLineEdit.setText('-180.0')
        self.locationRangeEastLineEdit.setText('180.0')
        self.locationRangeSouthLineEdit.setText('-90.0')
        self.locationRangeNorthLineEdit.setText('90.0')
        self.distanceFromPointMinRadiusLineEdit.setText('0.0')
        self.distanceFromPointMaxRadiusLineEdit.setText('90.0')
        self.distanceFromPointEastLineEdit.setText('0.0')
        self.distanceFromPointNorthLineEdit.setText('0.0')


    @QtCore.pyqtSlot()    
    def getOptions(self):
        """
        Return a dictionary containing everything specified in the EventQueryDialog.
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
        if self.locationRangeRadioButton.isChecked():         
            if str(self.locationRangeWestLineEdit.text()) != '':
                options['minlon'] = str(self.locationRangeWestLineEdit.text())            
            if str(self.locationRangeEastLineEdit.text()) != '':
                options['maxlon'] = str(self.locationRangeEastLineEdit.text())            
            if str(self.locationRangeSouthLineEdit.text()) != '':
                options['minlat'] = str(self.locationRangeSouthLineEdit.text())            
            if str(self.locationRangeNorthLineEdit.text()) != '':
                options['maxlat'] = str(self.locationRangeNorthLineEdit.text())
        if self.locationDistanceFromPointRadioButton.isChecked():         
            if str(self.distanceFromPointMinRadiusLineEdit.text()) != '':
                options['minradius'] = str(self.distanceFromPointMinRadiusLineEdit.text())            
            if str(self.distanceFromPointMaxRadiusLineEdit.text()) != '':
                options['maxradius'] = str(self.distanceFromPointMaxRadiusLineEdit.text())            
            if str(self.distanceFromPointEastLineEdit.text()) != '':
                options['lon'] = str(self.distanceFromPointEastLineEdit.text())            
            if str(self.distanceFromPointNorthLineEdit.text()) != '':
                options['lat'] = str(self.distanceFromPointNorthLineEdit.text())
            
        return options


class MainWindow(QtGui.QMainWindow, MainWindow.Ui_MainWindow):
    
    def __init__(self,parent=None):

        super(self.__class__, self).__init__()
        self.setupUi(self)
        
        # Get the Figure object from the map_canvas
        self.map_figure = self.map_canvas.fig
        self.map_axes = self.map_figure.add_axes([0.01, 0.01, .98, .98])
        self.map_axes.clear()
        self.seismap = Seismap(projection='robin', ax=self.map_axes) # 'cyl' or 'robin' or 'mill'
        self.map_figure.canvas.draw()
        
        # Events
        self.eventQueryDialog = EventQueryDialog(self)        
        self.eventsHandler = Events()        
        self.eventsTable.setSortingEnabled(True)
        self.eventsTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.eventsTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # Stations
        self.stationQueryDialog = StationQueryDialog(self)
        self.stationsHandler = Stations()        
        self.stationsTable.setSortingEnabled(True)
        self.stationsTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.stationsTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # Connect signals
        # NOTE:  http://zetcode.com/gui/pyqt4/eventsandsignals/
        # NOTE:  https://wiki.python.org/moin/PyQt/Sending%20Python%20values%20with%20signals%20and%20slots
        QtCore.QObject.connect(self.eventsTable, QtCore.SIGNAL('cellClicked(int, int)'), self.eventsTableClicked)
        QtCore.QObject.connect(self.stationsTable, QtCore.SIGNAL('cellClicked(int, int)'), self.stationsTableClicked)

        # Connect the buttons so that they open the dialog
        self.eventOptionsButton.pressed.connect(self.eventQueryDialog.show)
        self.stationOptionsButton.pressed.connect(self.stationQueryDialog.show)
        self.getEventsButton.pressed.connect(self.queryEvents)
        self.getStationsButton.pressed.connect(self.queryStations)
        
        self.setWindowTitle('Main window')    
        self.show()
   
   
    @QtCore.pyqtSlot()
    def queryEvents(self):
        # Get events and subset to desired columns
        parameters = self.eventQueryDialog.getOptions()
        # TODO:  handle errors when querying events
        eventsDF = self.eventsHandler.get_dataframe(parameters=parameters)
        eventsDF = eventsDF[['Time','Latitude','Longitude','Depth/km','MagType','Magnitude']]
        numeric_column = [False,True,True,True,False,True]
        
        # Add events to the events table ---------------------------------------
        
        self.eventsTable.setRowCount(eventsDF.shape[0])
        self.eventsTable.setColumnCount(eventsDF.shape[1])
        self.eventsTable.setHorizontalHeaderLabels(eventsDF.columns.tolist())
        self.eventsTable.verticalHeader().hide()
        
        for i in range(eventsDF.shape[0]):
            for j in range(eventsDF.shape[1]):
                # Guarantee that all elements are converted to strings for display but apply proper sorting
                if numeric_column[j]:
                    self.eventsTable.setItem(i, j, MyNumericTableWidgetItem(str(eventsDF.iat[i,j])))
                else:
                    self.eventsTable.setItem(i, j, QtGui.QTableWidgetItem(str(eventsDF.iat[i,j])))

        # Tighten up the table
        self.eventsTable.resizeColumnsToContents()
        self.eventsTable.resizeRowsToContents()
        
        # Add items to the map -------------------------------------------------
                
        self.seismap.add_events(eventsDF)
        
        if self.eventQueryDialog.locationRangeRadioButton.isChecked():
            n = float(self.eventQueryDialog.locationRangeNorthLineEdit.text())
            e = float(self.eventQueryDialog.locationRangeEastLineEdit.text())
            s = float(self.eventQueryDialog.locationRangeSouthLineEdit.text())
            w = float(self.eventQueryDialog.locationRangeWestLineEdit.text())
            self.seismap.add_events_box(n, e, s, w)
        elif self.eventQueryDialog.locationDistanceFromPointRadioButton.isChecked():
            n = float(self.eventQueryDialog.distanceFromPointNorthLineEdit.text())
            e = float(self.eventQueryDialog.distanceFromPointEastLineEdit.text())
            minradius = float(self.eventQueryDialog.distanceFromPointMinRadiusLineEdit.text())
            maxradius = float(self.eventQueryDialog.distanceFromPointMaxRadiusLineEdit.text())
            self.seismap.add_events_toroid(n, e, minradius, maxradius)


    @QtCore.pyqtSlot()
    def queryStations(self):
        # Get stations and subset to desired columns
        parameters = self.stationQueryDialog.getOptions()
        # TODO:  handle errors when querying stations
        stationsDF = self.stationsHandler.get_dataframe(parameters=parameters)
        stationsDF = stationsDF[['Network','Station','Location','Channel','Latitude','Longitude']]
        numeric_column = [False,False,False,False,True,True]
        
        # Add stations to the stations table -----------------------------------
        
        self.stationsTable.setRowCount(stationsDF.shape[0])
        self.stationsTable.setColumnCount(stationsDF.shape[1])
        self.stationsTable.setHorizontalHeaderLabels(stationsDF.columns.tolist())
        self.stationsTable.verticalHeader().hide()
        
        for i in range(stationsDF.shape[0]):
            for j in range(stationsDF.shape[1]):
                # Guarantee that all elements are converted to strings for display but apply proper sorting
                if numeric_column[j]:
                    self.stationsTable.setItem(i, j, MyNumericTableWidgetItem(str(stationsDF.iat[i,j])))
                else:
                    self.stationsTable.setItem(i, j, QtGui.QTableWidgetItem(str(stationsDF.iat[i,j])))

        # Tighten up the table
        self.stationsTable.resizeColumnsToContents()
        self.stationsTable.resizeRowsToContents()
                   
        # Add items to the map -------------------------------------------------

        self.seismap.add_stations(stationsDF)
        
        if self.stationQueryDialog.locationRangeRadioButton.isChecked():
            n = float(self.stationQueryDialog.locationRangeNorthLineEdit.text())
            e = float(self.stationQueryDialog.locationRangeEastLineEdit.text())
            s = float(self.stationQueryDialog.locationRangeSouthLineEdit.text())
            w = float(self.stationQueryDialog.locationRangeWestLineEdit.text())
            self.seismap.add_stations_box(n, e, s, w)
        elif self.stationQueryDialog.locationDistanceFromPointRadioButton.isChecked():
            n = float(self.stationQueryDialog.distanceFromPointNorthLineEdit.text())
            e = float(self.stationQueryDialog.distanceFromPointEastLineEdit.text())
            minradius = float(self.stationQueryDialog.distanceFromPointMinRadiusLineEdit.text())
            maxradius = float(self.stationQueryDialog.distanceFromPointMaxRadiusLineEdit.text())
            self.seismap.add_stations_toroid(n, e, minradius, maxradius)


    @QtCore.pyqtSlot(int, int)
    def eventsTableClicked(self, row, col):
        """
        Handle a click anywhere in the table.
        """
        # Get selected rows
        rows = []
        for idx in self.eventsTable.selectionModel().selectedRows():
            rows.append(idx.row())
        
        # Update the eventsHandler with the latest selection information
        self.eventsHandler.set_selectedRows(rows)
        
        # Get lons and lats
        # TODO:  Automatically detect longitude and latitude columns
        lons = []
        lats = []
        for row in rows:
            lat = float(self.eventsTable.item(row,1).text())
            lats.append(lat)
            lon = float(self.eventsTable.item(row,2).text())
            lons.append(lon)
            
        self.seismap.add_events_highlighting(lons, lats)
        
        
    @QtCore.pyqtSlot(int, int)
    def stationsTableClicked(self, row, col):
        # Get selected rows
        rows = []
        for idx in self.stationsTable.selectionModel().selectedRows():
            rows.append(idx.row())
        
        # Update the eventsHandler with the latest selection information
        self.stationsHandler.set_selectedRows(rows)
        
        # Get lons and lats
        # TODO:  Automatically detect longitude and latitude columns
        lons = []
        lats = []
        for row in rows:
            lat = float(self.stationsTable.item(row,4).text())
            lats.append(lat)
            lon = float(self.stationsTable.item(row,5).text())
            lons.append(lon)
            
        self.seismap.add_stations_highlighting(lons, lats)            
        
        
if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    GUI = MainWindow()
    sys.exit(app.exec_())
    
