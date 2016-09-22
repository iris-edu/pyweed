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
import logging

# Vectors and dataframes
import numpy as np
import pandas as pd

# PyQt4 packages
from PyQt4 import QtCore
from PyQt4 import QtGui

# Pyweed UI components
import LoggingDialog
import EventQueryDialog
import StationQueryDialog
import WaveformDialog
import MainWindow

from pyweed_style import stylesheet

# Pyweed PyQt4 enhancements
from MyDoubleValidator import MyDoubleValidator
from MyNumericTableWidgetItem import MyNumericTableWidgetItem
from MyTextEditLoggingHandler import MyTextEditLoggingHandler

# Pyweed components

from preferences import Preferences
from eventsHandler import EventsHandler
from stationsHandler import StationsHandler
from waveformsHandler import WaveformsHandler
from seismap import Seismap

__appName__ = "PYWEED"
__version__ = "0.0.6"


class LoggingDialog(QtGui.QDialog, LoggingDialog.Ui_LoggingDialog):
    def __init__(self, parent=None, logger=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Logs')

        # Initialize loggingPlainTextEdit
        self.loggingPlainTextEdit.setReadOnly(True)
        
        # Add a widget logging handler to the logger
        loggingHandler = MyTextEditLoggingHandler(widget=self.loggingPlainTextEdit)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        loggingHandler.setFormatter(formatter)
        logger.addHandler(loggingHandler)
     

class EventQueryDialog(QtGui.QDialog, EventQueryDialog.Ui_EventQueryDialog):
    """Dialog window for event options used in creating a webservice query."""
    def __init__(self, parent=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Event Query Options')
        
        # Get references to MainWindow elements
        self.logger = parent.logger
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
        
        # Set tab order
        self.setTabOrder(self.minmagLineEdit, self.maxmagLineEdit)
        self.setTabOrder(self.maxmagLineEdit, self.mindepthLineEdit)        
        self.setTabOrder(self.mindepthLineEdit, self.maxdepthLineEdit)
        self.setTabOrder(self.maxdepthLineEdit, self.locationRangeNorthLineEdit)
        self.setTabOrder(self.locationRangeNorthLineEdit, self.locationRangeWestLineEdit)
        self.setTabOrder(self.locationRangeWestLineEdit, self.locationRangeEastLineEdit)
        self.setTabOrder(self.locationRangeEastLineEdit, self.locationRangeSouthLineEdit)
        self.setTabOrder(self.locationRangeSouthLineEdit, self.distanceFromPointMinRadiusLineEdit)
        self.setTabOrder(self.distanceFromPointMinRadiusLineEdit, self.distanceFromPointMaxRadiusLineEdit)
        self.setTabOrder(self.distanceFromPointMaxRadiusLineEdit, self.distanceFromPointEastLineEdit)
        self.setTabOrder(self.distanceFromPointEastLineEdit, self.distanceFromPointNorthLineEdit)

        # Initialize input fields using preferences
        prefs = parent.preferences.EventOptions
        self.minmagLineEdit.setText(prefs.minmag)
        self.maxmagLineEdit.setText(prefs.maxmag)
        self.mindepthLineEdit.setText(prefs.mindepth)
        self.maxdepthLineEdit.setText(prefs.maxdepth)
        self.locationRangeWestLineEdit.setText(prefs.locationRangeWest)
        self.locationRangeEastLineEdit.setText(prefs.locationRangeEast)
        self.locationRangeSouthLineEdit.setText(prefs.locationRangeSouth)
        self.locationRangeNorthLineEdit.setText(prefs.locationRangeNorth)
        self.distanceFromPointMinRadiusLineEdit.setText(prefs.distanceFromPointMinRadius)
        self.distanceFromPointMaxRadiusLineEdit.setText(prefs.distanceFromPointMaxRadius)
        self.distanceFromPointEastLineEdit.setText(prefs.distanceFromPointEast)
        self.distanceFromPointNorthLineEdit.setText(prefs.distanceFromPointNorth)
        
        # Initialize the date selectors # TODO: using preferences
        self.starttimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.endtimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        today = QtCore.QDateTime.currentDateTime()
        monthAgo = today.addMonths(-1)
        self.starttimeDateTimeEdit.setDateTime(monthAgo)
        self.endtimeDateTimeEdit.setDateTime(today)
        
        # Intialize time and location type selection using preferences
        getattr(self, prefs.selectedTimeButton).setChecked(True)
        getattr(self, prefs.selectedLocationButton).setChecked(True)
        

        
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
        self.setWindowTitle('Station Query Options')

        # Get references to MainWindow elements
        self.logger = parent.logger
        self.seismap = parent.seismap
        self.map_figure = parent.map_figure

        # Create buttonGroups
        self.timeButtonGroup = QtGui.QButtonGroup()
        self.timeButtonGroup.addButton(self.timeBetweenRadioButton,1)
        self.timeButtonGroup.addButton(self.timeDuringEventsRadioButton,2)
        
        self.locationButtonGroup = QtGui.QButtonGroup()
        self.locationButtonGroup.addButton(self.locationRangeRadioButton,1)
        self.locationButtonGroup.addButton(self.locationDistanceFromPointRadioButton,2)
        self.locationButtonGroup.addButton(self.locationDistanceFromEventsRadioButton,3)

        # Set validators for input fields # TODO:  What are appropriate valid ranges?
        self.locationRangeSouthLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.locationRangeSouthLineEdit))        
        self.locationRangeEastLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.locationRangeEastLineEdit))        
        self.locationRangeSouthLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.locationRangeSouthLineEdit))        
        self.locationRangeNorthLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.locationRangeNorthLineEdit))        
        self.distanceFromPointMinRadiusLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.distanceFromPointMinRadiusLineEdit))        
        self.distanceFromPointMaxRadiusLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.distanceFromPointMaxRadiusLineEdit))        
        self.distanceFromPointEastLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.distanceFromPointEastLineEdit))        
        self.distanceFromPointNorthLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.distanceFromPointNorthLineEdit))
        
        # Set tab order
        self.setTabOrder(self.networkLineEdit, self.stationLineEdit)
        self.setTabOrder(self.stationLineEdit, self.locationLineEdit)        
        self.setTabOrder(self.locationLineEdit, self.channelLineEdit)
        self.setTabOrder(self.channelLineEdit, self.locationRangeNorthLineEdit)
        self.setTabOrder(self.locationRangeNorthLineEdit, self.locationRangeWestLineEdit)
        self.setTabOrder(self.locationRangeWestLineEdit, self.locationRangeEastLineEdit)
        self.setTabOrder(self.locationRangeEastLineEdit, self.locationRangeSouthLineEdit)
        self.setTabOrder(self.locationRangeSouthLineEdit, self.distanceFromPointMinRadiusLineEdit)
        self.setTabOrder(self.distanceFromPointMinRadiusLineEdit, self.distanceFromPointMaxRadiusLineEdit)
        self.setTabOrder(self.distanceFromPointMaxRadiusLineEdit, self.distanceFromPointEastLineEdit)
        self.setTabOrder(self.distanceFromPointEastLineEdit, self.distanceFromPointNorthLineEdit)

        # Initialize input fields using preferences
        prefs = parent.preferences.StationOptions
        self.networkLineEdit.setText(prefs.network)
        self.stationLineEdit.setText(prefs.station)
        self.locationLineEdit.setText(prefs.location)
        self.channelLineEdit.setText(prefs.channel)
        self.locationRangeWestLineEdit.setText(prefs.locationRangeWest)
        self.locationRangeEastLineEdit.setText(prefs.locationRangeEast)
        self.locationRangeSouthLineEdit.setText(prefs.locationRangeSouth)
        self.locationRangeNorthLineEdit.setText(prefs.locationRangeNorth)
        self.distanceFromPointMinRadiusLineEdit.setText(prefs.distanceFromPointMinRadius)
        self.distanceFromPointMaxRadiusLineEdit.setText(prefs.distanceFromPointMaxRadius)
        self.distanceFromPointEastLineEdit.setText(prefs.distanceFromPointEast)
        self.distanceFromPointNorthLineEdit.setText(prefs.distanceFromPointNorth)

        # Initialize the date selectors # TODO: using preferences
        self.starttimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        self.endtimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        today = QtCore.QDateTime.currentDateTime()
        monthAgo = today.addMonths(-1)
        self.starttimeDateTimeEdit.setDateTime(monthAgo)
        self.endtimeDateTimeEdit.setDateTime(today)

        # TODO:  Intialize time and location type selection using preferences
        getattr(self, prefs.selectedTimeButton).setChecked(True)
        getattr(self, prefs.selectedLocationButton).setChecked(True)


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


class WaveformDialog(QtGui.QDialog, WaveformDialog.Ui_WaveformDialog):
    """Dialog window for selection and display of waveforms."""
    def __init__(self, parent=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Waveforms')

        # Get references to MainWindow elements
        self.logger = parent.logger

        # Waveforms
        self.waveformsHandler = WaveformsHandler(self.logger)

        # Get references to the Events and Stations objects
        self.eventsHandler = parent.eventsHandler
        self.stationsHandler = parent.stationsHandler

        # Selection table
        self.selectionTable.setSortingEnabled(True)
        self.selectionTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.selectionTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        
        # Connect signals associated with table clicks
        # NOTE:  http://zetcode.com/gui/pyqt4/eventsandsignals/
        # NOTE:  https://wiki.python.org/moin/PyQt/Sending%20Python%20values%20with%20signals%20and%20slots
        QtCore.QObject.connect(self.selectionTable, QtCore.SIGNAL('cellClicked(int, int)'), self.selectionTableClicked)
        
        # Connect signals associated with comboBoxes
        # NOTE:  http://www.tutorialspoint.com/pyqt/pyqt_qcombobox_widget.htm
        # NOTE:  currentIndexChanged() responds to both user and programmatic changes. Use activated() for user initiated changes
        self.eventComboBox.activated.connect(self.loadFilteredSelectionTable)
        self.networkComboBox.activated.connect(self.loadFilteredSelectionTable)
        self.stationComboBox.activated.connect(self.loadFilteredSelectionTable)
        
        
    @QtCore.pyqtSlot()    
    def loadWaveformChoices(self, filterColumn=None, filterText=None):
        """Fill the selectionTable with all SNCL-Events selected in the MainWindow."""
        
        ## Create a new dataframe with time, source_lat, source_lon, source_mag, source_depth, SNCL, network, station, receiver_lat, receiver_lon -- one for each waveform
        eventsDF = self.eventsHandler.get_selected_dataframe()
        stationsDF = self.stationsHandler.get_selected_dataframe()
        waveformsDF = self.waveformsHandler.create_waveformsDF(eventsDF, stationsDF)
                        
        # Add event-SNCL combintations to the selection table
        self.loadSelectionTable(waveformsDF)

        # Add unique events to the eventComboBox -------------------------------
        
        for i in range(self.eventComboBox.count()):
            self.eventComboBox.removeItem(i)
            
        self.eventComboBox.addItem('All events')
        for i in range(eventsDF.shape[0]):
            self.eventComboBox.addItem(eventsDF.Time.iloc[i])
        
        # Add unique networks to the networkComboBox ---------------------------
        
        for i in range(self.networkComboBox.count()):
            self.networkComboBox.removeItem(i)
            
        self.networkComboBox.addItem('All networks')
        for network in stationsDF.Network.unique().tolist():
            self.networkComboBox.addItem(network)

        # Add unique stations to the stationsComboBox --------------------------

        for i in range(self.stationComboBox.count()):
            self.stationComboBox.removeItem(i)

        self.stationComboBox.addItem('All stations')
        for station in stationsDF.Station.unique().tolist():
            self.stationComboBox.addItem(station)


    @QtCore.pyqtSlot()    
    def loadSelectionTable(self, waveformsDF):
        """
        Add event-SNCL combintations to the selection table
        """

        # NOTE:  Here is the list of all column names:
        # NOTE:         ['Time', 'Magnitude', 'Depth/km', 'Event_Lon', 'Event_Lat', 'SNCL', 'Network', 'Station', Station_Lon', 'Station_Lat', 'Distance']
        hidden_column =  [False,  False,       False,      False,       False,       False,  True,      True,     True,          True,          False]
        numeric_column = [False,  True,        True,       True,        True,        False,  False,     False,    True,          True,          True]

        # Clear existing contents
        # NOTE:  Doing clearSelection() first is important!
        self.selectionTable.clearSelection()
        while (self.selectionTable.rowCount() > 0):
            self.selectionTable.removeRow(0)
        
        # Create new table
        self.selectionTable.setRowCount(waveformsDF.shape[0])
        self.selectionTable.setColumnCount(waveformsDF.shape[1])
        self.selectionTable.setHorizontalHeaderLabels(waveformsDF.columns.tolist())
        self.selectionTable.verticalHeader().hide()
        # Hidden columns
        for i in np.arange(len(hidden_column)):
            if hidden_column[i]:
                self.selectionTable.setColumnHidden(i,True)
        
        # Add new contents
        for i in range(waveformsDF.shape[0]):
            for j in range(waveformsDF.shape[1]):
                # Guarantee that all elements are converted to strings for display but apply proper sorting
                if numeric_column[j]:
                    self.selectionTable.setItem(i, j, MyNumericTableWidgetItem(str(waveformsDF.iat[i,j])))
                else:
                    self.selectionTable.setItem(i, j, QtGui.QTableWidgetItem(str(waveformsDF.iat[i,j])))

        # Tighten up the table
        self.selectionTable.resizeColumnsToContents()
        self.selectionTable.resizeRowsToContents()

        
    @QtCore.pyqtSlot(int)
    def loadFilteredSelectionTable(self):
        waveformsDF = self.waveformsHandler.currentDF
        time = self.eventComboBox.currentText()
        network = self.networkComboBox.currentText()
        station = self.stationComboBox.currentText()
        if not time.startsWith('All'):
            waveformsDF = waveformsDF[waveformsDF.Time == time]
        if not network.startsWith('All'):
            waveformsDF = waveformsDF[waveformsDF.Network == network]
        if not station.startsWith('All'):
            waveformsDF = waveformsDF[waveformsDF.Station == station]
        self.loadSelectionTable(waveformsDF)
    
    
    @QtCore.pyqtSlot(int, int)
    def selectionTableClicked(self, row, col):
        # Get selected rows
        rows = []
        for idx in self.selectionTable.selectionModel().selectedRows():
            rows.append(idx.row())
        
        # Get ltime and SNCL
        # TODO:  Automatically detect time and SNCL columns
        times = []
        source_depths = []
        source_lons = []
        source_lats = []
        receiver_lons = []
        receiver_lats = []
        stationIDs = []
        # TODO:  Is there a more pandas-like way to extract this info?
        for row in rows:
            time = str(self.selectionTable.item(row,0).text())
            times.append(time)
            source_depth = float(self.selectionTable.item(row,2).text())
            source_depths.append(source_depth)
            source_lon = float(self.selectionTable.item(row,3).text())
            source_lons.append(source_lon)
            source_lat = float(self.selectionTable.item(row,4).text())
            source_lats.append(source_lat)
            stationID = str(self.selectionTable.item(row,5).text())
            stationIDs.append(stationID)
            receiver_lon = float(self.selectionTable.item(row,8).text())
            receiver_lons.append(receiver_lon)
            receiver_lat = float(self.selectionTable.item(row,9).text())
            receiver_lats.append(receiver_lat)
            
        # Update the waveformsHandler with the latest selection information
        self.waveformsHandler.set_selected_ids(stationIDs)

        # TODO:  Additional parameters will specify seconds before/after, ...
        parameters = {}
        parameters['times'] = times
        parameters['source_depths'] = source_depths
        parameters['source_lons'] = source_lons
        parameters['source_lats'] = source_lats
        parameters['stationIDs'] = stationIDs
        parameters['receiver_lons'] = receiver_lons
        parameters['receiver_lats'] = receiver_lats

        # TODO:  handle errors when loading waveforms into memory
        result = self.waveformsHandler.load_data(parameters=parameters)

        # TODO:  display/save waveform loading progress somewhere? 
        
        # TODO:  display waveform plots in lower table
        
        debugPoint = True
                

class MainWindow(QtGui.QMainWindow, MainWindow.Ui_MainWindow):
    
    def __init__(self,parent=None):

        super(self.__class__, self).__init__()
        self.setupUi(self)
        
        # Set MainWindow properties
        self.appName = __appName__
        self.version = __version__        
        self.setWindowTitle('%s version %s' % (self.appName, self.version))
        
        # Create StatusBar
        sb = QtGui.QStatusBar()
        sb.setFixedHeight(18)
        self.setStatusBar(sb)
        
        # TODO:  logging example   -- http://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
        # TODO:  logging example 2 -- http://stackoverflow.com/questions/24469662/how-to-redirect-logger-output-into-pyqt-text-widget
        
        # Load configurable preferences from ~/.pyweed/config.ini
        self.preferences = Preferences()
        try:
            self.preferences.load()
        except Exception as e:
            print("Unable to load configuration preferences -- using defaults.\n%s" % e)
            pass
        
        # Logging
        self.logger = logging.getLogger()
        try:
            logLevel = getattr(logging, self.preferences.Logging.level)
            self.logger.setLevel(logLevel)
        except Exception as e:
            self.logger.setLevel(logging.DEBUG)
        self.loggingDialog = LoggingDialog(self, self.logger)
        
        # Get the Figure object from the map_canvas
        self.logger.debug('Setting up main map...')
        self.map_figure = self.map_canvas.fig
        self.map_axes = self.map_figure.add_axes([0.01, 0.01, .98, .98])
        self.map_axes.clear()
        prefs = self.preferences.Map
        self.seismap = Seismap(projection=prefs.projection, ax=self.map_axes) # 'cyl' or 'robin' or 'mill'
        self.map_figure.canvas.draw()
        
        # Events
        self.logger.debug('Setting up event options dialog...')
        self.eventQueryDialog = EventQueryDialog(self)        
        self.eventsHandler = EventsHandler(self.logger)        
        self.eventsTable.setSortingEnabled(True)
        self.eventsTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.eventsTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # Stations
        self.logger.debug('Setting up station options dialog...')
        self.stationQueryDialog = StationQueryDialog(self)
        self.stationsHandler = StationsHandler(self.logger)        
        self.stationsTable.setSortingEnabled(True)
        self.stationsTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.stationsTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # Connect signals associated with table clicks
        # NOTE:  http://zetcode.com/gui/pyqt4/eventsandsignals/
        # NOTE:  https://wiki.python.org/moin/PyQt/Sending%20Python%20values%20with%20signals%20and%20slots
        QtCore.QObject.connect(self.eventsTable, QtCore.SIGNAL('cellClicked(int, int)'), self.eventsTableClicked)
        QtCore.QObject.connect(self.stationsTable, QtCore.SIGNAL('cellClicked(int, int)'), self.stationsTableClicked)

        # Waveforms
        self.logger.debug('Setting up wavaeforms dialog...')
        self.waveformsDialog = WaveformDialog(self)
        
        self.logger.debug('Setting up main window...')
        
        # Connect the main window buttons
        self.getEventsButton.pressed.connect(self.getEvents)
        self.getStationsButton.pressed.connect(self.getStations)
        self.getWaveformsButton.pressed.connect(self.getWaveforms)
        
        # Create menuBar
        # see:  http://doc.qt.io/qt-4.8/qmenubar.html
        # see:  http://zetcode.com/gui/pyqt4/menusandtoolbars/
        # see:  https://pythonprogramming.net/menubar-pyqt-tutorial/
        # see:  http://www.dreamincode.net/forums/topic/261282-a-basic-pyqt-tutorial-notepad/
        mainMenu = self.menuBar()
        mainMenu.setNativeMenuBar(False)

        fileMenu = mainMenu.addMenu('&File')
    
        quitAction = QtGui.QAction("&Quit", self)
        quitAction.setShortcut("Ctrl+Q")
        quitAction.triggered.connect(self.closeApplication)        
        fileMenu.addAction(quitAction)
    
        optionsMenu = mainMenu.addMenu('Options')

        eventOptionsAction = QtGui.QAction("Show Event Options", self)
        QtCore.QObject.connect(eventOptionsAction, QtCore.SIGNAL('triggered()'), self.eventQueryDialog.show)
        optionsMenu.addAction(eventOptionsAction)
        stationOptionsAction = QtGui.QAction("Show Station Options", self)
        QtCore.QObject.connect(stationOptionsAction, QtCore.SIGNAL('triggered()'), self.stationQueryDialog.show)
        optionsMenu.addAction(stationOptionsAction)
    
        helpMenu = mainMenu.addMenu('Help')
    
        aboutPyweedAction = QtGui.QAction("&About PYWEED", self)
        aboutPyweedAction.triggered.connect(self.aboutPyweed)        
        helpMenu.addAction(aboutPyweedAction)
        helpMenu.addSeparator()
        loggingDialogAction = QtGui.QAction("Show Logs", self)
        QtCore.QObject.connect(loggingDialogAction, QtCore.SIGNAL('triggered()'), self.loggingDialog.show)
        helpMenu.addAction(loggingDialogAction)
        
        # Display MainWindow
        self.statusBar().showMessage('Ready...')
        
        self.show()        
   
   
    @QtCore.pyqtSlot()
    def getEvents(self):
        # Get events and subset to desired columns
        parameters = self.eventQueryDialog.getOptions()
        # TODO:  handle errors when querying events
        eventsDF = self.eventsHandler.load_data(parameters=parameters)
        # NOTE:  Here is the list of all column names:
        # NOTE:         ['Time', 'Magnitude', 'Longitude', 'Latitude', 'Depth/km', 'MagType', 'EventLocationName', 'Author', 'Catalog', 'Contributor', 'ContributorID', 'MagAuthor', 'EventID']
        hidden_column = [ False,  False,       False,       False,      False,      False,     False,               True,     True,      True,          True,            True,        True]
        numeric_column = [False,  True,        True,        True,       True,       False,     False,               False,    False,     False,         False,           False,       False]
        
        # Add events to the events table ---------------------------------------

        self.logger.info('Loading %d events', eventsDF.shape[0])
        self.statusBar().showMessage('Loading %d events' % (eventsDF.shape[0]))

        # Clear existing contents
        # NOTE:  Doing clearSelection() first is important!
        self.eventsTable.clearSelection()
        while (self.eventsTable.rowCount() > 0):
            self.eventsTable.removeRow(0)
        
        # Create new table
        self.eventsTable.setRowCount(eventsDF.shape[0])
        self.eventsTable.setColumnCount(eventsDF.shape[1])
        self.eventsTable.setHorizontalHeaderLabels(eventsDF.columns.tolist())
        self.eventsTable.verticalHeader().hide()
        # Hidden columns
        for i in np.arange(len(hidden_column)):
            if hidden_column[i]:
                self.eventsTable.setColumnHidden(i,True)
        
        # Add new contents
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
    def getStations(self):
        # Get stations and subset to desired columns
        parameters = self.stationQueryDialog.getOptions()
        # TODO:  handle errors when querying stations
        stationsDF = self.stationsHandler.load_data(parameters=parameters)
        # NOTE:  Here is the list of all column names:
        # NOTE:         ['Network', 'Station', 'Location', 'Channel', 'Longitude', 'Latitude', 'Elevation', 'Depth', 'Azimuth', 'Dip', 'SensorDescription', 'Scale', 'ScaleFreq', 'ScaleUnits', 'SampleRate', 'StartTime', 'EndTime', 'SNCL']
        hidden_column = [ False,     False,     False,      False,     False,       False,      True,        True,    True,      True,  True,                True,    True,        True,         True,         True,        True,      True]
        numeric_column = [False,     False,     False,      False,     True,        True,       True,        True,    True,      True,  False,               True,    True,        False,        True,         False,       False,     False]

        # Add stations to the stations table -----------------------------------
        
        self.logger.info('Loading %d channels', stationsDF.shape[0])
        self.statusBar().showMessage('Loading %d channels' % (stationsDF.shape[0]))
        
        # Clear existing contents
        # NOTE:  Doing clearSelection() first is important!
        self.stationsTable.clearSelection()
        while (self.stationsTable.rowCount() > 0):
            self.stationsTable.removeRow(0)

        # Create new table
        self.stationsTable.setRowCount(stationsDF.shape[0])
        self.stationsTable.setColumnCount(stationsDF.shape[1])
        self.stationsTable.setHorizontalHeaderLabels(stationsDF.columns.tolist())
        self.stationsTable.verticalHeader().hide()
        # Hidden columns
        for i in np.arange(len(hidden_column)):
            if hidden_column[i]:
                self.stationsTable.setColumnHidden(i,True)

        # Add new contents
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

        

    @QtCore.pyqtSlot()
    def getWaveforms(self):
        self.waveformsDialog.show()
        self.waveformsDialog.loadWaveformChoices()


    @QtCore.pyqtSlot(int, int)
    def eventsTableClicked(self, row, col):
        """
        Handle a click anywhere in the table.
        """
        # Get selected rows
        rows = []
        for idx in self.eventsTable.selectionModel().selectedRows():
            rows.append(idx.row())
        
        self.logger.debug('%d events currently selected', len(rows))
        
        # Get lons, lats and 
        # TODO:  Automatically detect column indexes
        lons = []
        lats = []
        eventIDs = []
        for row in rows:
            lon = float(self.eventsTable.item(row,2).text())
            lons.append(lon)
            lat = float(self.eventsTable.item(row,3).text())
            lats.append(lat)
            eventID = str(self.eventsTable.item(row,12).text())
            eventIDs.append(eventID)
            
        # Update the eventsHandler with the latest selection information
        self.eventsHandler.set_selected_ids(eventIDs)

        self.seismap.add_events_highlighting(lons, lats)
        
        
    @QtCore.pyqtSlot(int, int)
    def stationsTableClicked(self, row, col):
        # Get selected rows
        rows = []
        for idx in self.stationsTable.selectionModel().selectedRows():
            rows.append(idx.row())
        
        self.logger.debug('%d channels currently selected', len(rows))

        # Get lons and lats
        # TODO:  Automatically detect longitude and latitude columns
        lons = []
        lats = []
        stationIDs = []
        for row in rows:
            lon = float(self.stationsTable.item(row,4).text())
            lons.append(lon)
            lat = float(self.stationsTable.item(row,5).text())
            lats.append(lat)
            stationID = str(self.stationsTable.item(row,17).text())
            stationIDs.append(stationID)
            
        # Update the stationsHandler with the latest selection information
        self.stationsHandler.set_selected_ids(stationIDs)

        self.seismap.add_stations_highlighting(lons, lats)            
                
        
    def aboutPyweed(self):
        """Display About message box."""
        # see:  http://www.programcreek.com/python/example/62361/PyQt4.QtGui.QMessageBox
        website = "https://github.com/iris-edu-int/pyweed"
        ###email = "adam@iris.washington.edu"
        license_link = "https://github.com/iris-edu-int/pyweed/blob/master/LICENSE"
        license_name = "MIT"
        
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle(self.tr("About " + self.appName))
        msgBox.setTextFormat(QtCore.Qt.RichText)
        ###msgBox.setIconPixmap(QtGui.QPixmap(ComicTaggerSettings.getGraphic('about.png')))
        msgBox.setText("<br><br><br>" +
                       self.appName +
                       " v" +
                       self.version +
                       "<br><br>" +
                       "Pyweed is a cross-platform GUI application for retrieving event-based seismic data." +
                       "<br><br>" +
                       "<a href='{0}'>{0}</a><br><br>".format(website) +
###                       "<a href='mailto:{0}'>{0}</a><br><br>".format(email) +
                       "License: <a href='{0}'>{1}</a>".format(license_link, license_name))

        msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
        msgBox.exec_()
        # NOTE:  For info on " modalSession has been exited prematurely" error on OS X see:
        # NOTE:    https://forum.qt.io/topic/43618/modal-sessions-with-pyqt4-and-os-x/2


    def closeApplication(self):
        # TODO:  Careful shutdown
        QtGui.QApplication.quit()
             

if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    GUI = MainWindow()
    sys.exit(app.exec_())
    
