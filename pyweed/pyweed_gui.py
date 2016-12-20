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
import os
import sys
import string
import logging
import time # TODO:  remove?

# Vectors and dataframes
import numpy as np
import pandas as pd

# Threads, Multiprocessing and Queues
import threading
import multiprocessing

# ObsPy
import obspy
from obspy import UTCDateTime
from obspy.clients import fdsn

# PyQt4 packages
import os
os.environ['QT_API'] = 'pyqt'
import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)
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
from MyTableWidgetImageWidget import MyTableWidgetImageWidget
from MyTableWidgetImageItem import MyTableWidgetImageItem
from MyTextEditLoggingHandler import MyTextEditLoggingHandler
from MyQt4MplCanvas import MyQt4MplCanvas

# Pyweed components

from preferences import Preferences
from eventsHandler import EventsHandler
from stationsHandler import StationsHandler
from waveformsHandler import WaveformsHandler
from seismap import Seismap

from pyweed_utils import manageCache
from console import ConsoleDialog

__appName__ = "PYWEED"
__version__ = "0.1.0"


LOGGER = logging.getLogger(__name__)


class LoggingDialog(QtGui.QDialog, LoggingDialog.Ui_LoggingDialog):
    """
    Dialog window displaying all logs.
    """
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
    """
    Dialog window for event options used in creating a webservice query.
    """
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
        #self.starttimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        #self.endtimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        today = QtCore.QDateTime.currentDateTimeUtc()
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
        All dictionary values are properly formatted for use in querying event services.

        Names of event options must match argument names defined here:
          https://docs.obspy.org/packages/autogen/obspy.clients.fdsn.client.Client.get_events.html
        """
        options = {}

        # times, magnitudes and depths are all guaranteed to be present
        options['starttime'] = str(self.starttimeDateTimeEdit.text()).rstrip(' UTC').replace(' ','T')
        options['endtime'] = str(self.endtimeDateTimeEdit.text()).rstrip(' UTC').replace(' ','T')
        options['minmagnitude'] = str(self.minmagLineEdit.text())
        options['maxmagnitude'] = str(self.maxmagLineEdit.text())
        options['mindepth'] = str(self.mindepthLineEdit.text())
        options['maxdepth'] = str(self.maxdepthLineEdit.text())

        # catalog, type, and lat-lon ranges are optional
        #if str(self.catalogComboBox.currentText()) != 'All Catalogs':
            #options['catalog'] = str(self.type.currentText())
        if str(self.magtypeComboBox.currentText()) != 'All Types':
            options['magnitudetype'] = str(self.magtypeComboBox.currentText())
        if self.locationRangeRadioButton.isChecked():
            if str(self.locationRangeWestLineEdit.text()) != '':
                options['minlongitude'] = str(self.locationRangeWestLineEdit.text())
            if str(self.locationRangeEastLineEdit.text()) != '':
                options['maxlongitude'] = str(self.locationRangeEastLineEdit.text())
            if str(self.locationRangeSouthLineEdit.text()) != '':
                options['minlatitude'] = str(self.locationRangeSouthLineEdit.text())
            if str(self.locationRangeNorthLineEdit.text()) != '':
                options['maxlatitude'] = str(self.locationRangeNorthLineEdit.text())
        if self.locationDistanceFromPointRadioButton.isChecked():
            if str(self.distanceFromPointMinRadiusLineEdit.text()) != '':
                options['minradius'] = str(self.distanceFromPointMinRadiusLineEdit.text())
            if str(self.distanceFromPointMaxRadiusLineEdit.text()) != '':
                options['maxradius'] = str(self.distanceFromPointMaxRadiusLineEdit.text())
            if str(self.distanceFromPointEastLineEdit.text()) != '':
                options['longitude'] = str(self.distanceFromPointEastLineEdit.text())
            if str(self.distanceFromPointNorthLineEdit.text()) != '':
                options['latitude'] = str(self.distanceFromPointNorthLineEdit.text())

        return options


class StationQueryDialog(QtGui.QDialog, StationQueryDialog.Ui_StationQueryDialog):
    """
    Dialog window for station options used in creating a webservice query.
    """
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
        self.locationButtonGroup.buttonClicked['int'].connect(self.onLocationButtonClicked)


        # Set validators for input fields # TODO:  What are appropriate valid ranges?
        self.locationRangeWestLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.locationRangeWestLineEdit))
        self.locationRangeEastLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.locationRangeEastLineEdit))
        self.locationRangeSouthLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.locationRangeSouthLineEdit))
        self.locationRangeNorthLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.locationRangeNorthLineEdit))
        self.distanceFromPointMinRadiusLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.distanceFromPointMinRadiusLineEdit))
        self.distanceFromPointMaxRadiusLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.distanceFromPointMaxRadiusLineEdit))
        self.distanceFromPointEastLineEdit.setValidator(MyDoubleValidator(-180.0,180.0,2,self.distanceFromPointEastLineEdit))
        self.distanceFromPointNorthLineEdit.setValidator(MyDoubleValidator(-90.0,90.0,2,self.distanceFromPointNorthLineEdit))

        # Set tab order
#         self.setTabOrder(self.networkLineEdit, self.stationLineEdit)
#         self.setTabOrder(self.stationLineEdit, self.locationLineEdit)
#         self.setTabOrder(self.locationLineEdit, self.channelLineEdit)
#         self.setTabOrder(self.channelLineEdit, self.locationRangeNorthLineEdit)
#         self.setTabOrder(self.locationRangeNorthLineEdit, self.locationRangeWestLineEdit)
#         self.setTabOrder(self.locationRangeWestLineEdit, self.locationRangeEastLineEdit)
#         self.setTabOrder(self.locationRangeEastLineEdit, self.locationRangeSouthLineEdit)
#         self.setTabOrder(self.locationRangeSouthLineEdit, self.distanceFromPointMinRadiusLineEdit)
#         self.setTabOrder(self.distanceFromPointMinRadiusLineEdit, self.distanceFromPointMaxRadiusLineEdit)
#         self.setTabOrder(self.distanceFromPointMaxRadiusLineEdit, self.distanceFromPointEastLineEdit)
#         self.setTabOrder(self.distanceFromPointEastLineEdit, self.distanceFromPointNorthLineEdit)

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
        #self.starttimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss')
        #self.endtimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss')
        today = QtCore.QDateTime.currentDateTimeUtc()
        monthAgo = today.addMonths(-1)
        self.starttimeDateTimeEdit.setDateTime(monthAgo)
        self.endtimeDateTimeEdit.setDateTime(today)

        # TODO:  Intialize time and location type selection using preferences
        getattr(self, prefs.selectedTimeButton).setChecked(True)
        getattr(self, prefs.selectedLocationButton).setChecked(True)

    @QtCore.pyqtSlot(int)
    def onLocationButtonClicked(self, button_id):
        def enableItem(item, enabled):
            if isinstance(item, QtGui.QLayout):
                for i in range(item.count()):
                    enableItem(item.itemAt(i), enabled)
            elif hasattr(item, 'setEnabled'):
                item.setEnabled(enabled)
        enableItem(self.locationRangeLayout, button_id == 1)

    @QtCore.pyqtSlot()
    def getOptions(self):
        """
        Return a dictionary containing everything specified in the StationQueryDialog.
        All dictionary values are properly formatted for use in querying station services.

        # NOTE:  Names of event options must match argument names defined here:
        # NOTE:    https://docs.obspy.org/packages/autogen/obspy.clients.fdsn.client.Client.get_stations.html
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
                options['minlongitude'] = str(self.locationRangeWestLineEdit.text())
            if str(self.locationRangeEastLineEdit.text()) != '':
                options['maxlongitude'] = str(self.locationRangeEastLineEdit.text())
            if str(self.locationRangeSouthLineEdit.text()) != '':
                options['minlatitude'] = str(self.locationRangeSouthLineEdit.text())
            if str(self.locationRangeNorthLineEdit.text()) != '':
                options['maxlatitude'] = str(self.locationRangeNorthLineEdit.text())
        if self.locationDistanceFromPointRadioButton.isChecked():
            if str(self.distanceFromPointMinRadiusLineEdit.text()) != '':
                options['minradius'] = str(self.distanceFromPointMinRadiusLineEdit.text())
            if str(self.distanceFromPointMaxRadiusLineEdit.text()) != '':
                options['maxradius'] = str(self.distanceFromPointMaxRadiusLineEdit.text())
            if str(self.distanceFromPointEastLineEdit.text()) != '':
                options['longitude'] = str(self.distanceFromPointEastLineEdit.text())
            if str(self.distanceFromPointNorthLineEdit.text()) != '':
                options['latitude'] = str(self.distanceFromPointNorthLineEdit.text())

        return options


class WaveformDialog(QtGui.QDialog, WaveformDialog.Ui_WaveformDialog):
    """
    Dialog window for selection and display of waveforms.
    """
    def __init__(self, parent=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Waveforms')

        # Keep a reference to globally shared components
        self.logger = parent.logger
        self.preferences = parent.preferences
        self.client = parent.client

        # Configured properties
        self.waveformDirectory = os.path.expanduser('~') # TODO:  get configurable WaveformDirectory

        # Modify default GUI settings
        self.saveDirectoryPushButton.setText(self.waveformDirectory)
        self.saveDirectoryPushButton.setFocusPolicy(QtCore.Qt.NoFocus)

        # Fill the format combo box
        self.saveFormatComboBox.addItems(['ASCII','GSE2','MSEED','SAC'])
        self.saveFormatComboBox.setCurrentIndex(2)

        self.logger.debug('Initializing waveform dialog...')

        # Waveforms
        self.waveformsHandler = WaveformsHandler(self.logger, self.preferences, self.client)
        self.waveformsDownloadComplete = False
        self.waveformsSaveComplete = ""
        self.waveformsHandler.log.connect(self.on_log)
        self.waveformsHandler.progress.connect(self.on_waveform_downloaded)
        self.waveformsHandler.done.connect(self.on_all_downloaded)

        # Get references to the Events and Stations objects
        self.eventsHandler = parent.eventsHandler
        self.stationsHandler = parent.stationsHandler

        # Set up queues to request waveform downloads and respond with a status
        self.waveformRequestQueue = multiprocessing.Queue()
        self.waveformResponseQueue = multiprocessing.Queue()

        # Displayed waveforms
        self.visibleWaveformsDF = pd.DataFrame()

        # Selection table
        self.selectionTable.setSortingEnabled(True)
        self.selectionTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.selectionTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.selectionTable.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.selectionTable.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

        # Resize contents after sort
        self.selectionTable.horizontalHeader().sortIndicatorChanged.connect(self.selectionTable.resizeRowsToContents)

        # Connect the Download and Save GUI elements
        self.downloadToolButton.toggled.connect(self.toggledDownloadToolButton)
        self.saveToolButton.toggled.connect(self.toggledSaveToolButton)
        self.saveDirectoryPushButton.pressed.connect(self.getWaveformDirectory)
        self.saveFormatComboBox.activated.connect(self.resetSave)

        # Connect signals associated with comboBoxes
        # NOTE:  http://www.tutorialspoint.com/pyqt/pyqt_qcombobox_widget.htm
        # NOTE:  currentIndexChanged() responds to both user and programmatic changes. Use activated() for user initiated changes
        self.eventComboBox.activated.connect(self.loadFilteredSelectionTable)
        self.networkComboBox.activated.connect(self.loadFilteredSelectionTable)
        self.stationComboBox.activated.connect(self.loadFilteredSelectionTable)
        self.selectionTable.itemClicked.connect(self.handleTableItemClicked)

        # Connect signals associated with spinBoxes
        self.secondsBeforeSpinBox.valueChanged.connect(self.resetDownload)
        self.secondsAfterSpinBox.valueChanged.connect(self.resetDownload)

        # Set up a thread to watch for waveform requests that lasts as long as this dialog is open
        self.logger.debug('Starting waveformRequestWatcherThread')
        #self.waveformRequestWatcher = waveformRequestWatcherThread(self.waveformRequestQueue)
        #self.waveformRequestWatcher.waveformRequestSignal.connect(self.handleWaveformRequest)
        #self.waveformRequestWatcher.start()

        # Set up a thread to watch for waveforms that lasts as long as this dialog is open
        self.logger.debug('Starting waveformWatcher thread')
        #self.waveformResponseWatcher = waveformResponseWatcherThread(self.waveformResponseQueue)
        #self.waveformResponseWatcher.waveformResponseSignal.connect(self.handleWaveformResponse)
        #self.waveformResponseWatcher.start()

        self.logger.debug('Finished initializing waveform dialog')


    def handleWaveformRequest(self):
        """
        This funciton is invoked whenever the waveformRequestWatcherThread emits
        a waveformRequestSignal. This means that a new waveform request has been
        assembled and placed on the waveformRequestQueue.
        """

        # NOTE:  The watcher should guarantee there is something in the queue
        # NOTE:  before emitting the waveformRequestSignal that is connected
        # NOTE:  to this function. But it doesn't hurt to check again.

        if not self.waveformRequestQueue.empty():

            # Get the request
            request = self.waveformRequestQueue.get()

            # Attempt to download a waveform
            secondsBefore = self.secondsBeforeSpinBox.value()
            secondsAfter = self.secondsAfterSpinBox.value()
            (status, waveformID, mseedFile, message) = self.waveformsHandler.handleWaveformRequest(request, secondsBefore, secondsAfter)

            # Update GUI
            QtGui.QApplication.processEvents()

            ## Announce that the downloaded mseedFile is ready for plotting
            ## TODO:  Maybe change the status and message to reflect "MSEED_READY". It should not be up the the downloader to decide what happens next.
            #message = "Plotting %s" % request['waveformID']

            self.waveformResponseQueue.put( {"status":status, "waveformID":waveformID, "mseedFile":mseedFile, "message":message})

        return


    def handleWaveformResponse(self):
        """
        This funciton is invoked whenever the waveformResponseWatcherThread emits
        a waveformResponseSignal. This means that handleWaveformRequest()
        has written a new .MSEED file to disk and it is available for processing.
        """
        if not self.waveformResponseQueue.empty():

            # TODO:  plot_width, plot_height should come from preferences
            plot_width = 600
            plot_height = 200

            # Get selectionTable column names
            column_names = self.waveformsHandler.getColumnNames()

            # Get the message sent by handleWaveformRequest
            item = self.waveformResponseQueue.get()
            status = item['status']
            waveformID = item['waveformID']
            mseedFile = item['mseedFile']
            message = item['message']

            self.logger.debug("waveformResponseSignal: %s -- %s", status, waveformID)

            # WaveformDialog status text
            statusText = ''

            # Find selectionTable row
            row = 0
            for row in range(self.selectionTable.rowCount()):
                if self.selectionTable.item(row,column_names.index('WaveformID')).text() == waveformID:
                    break


            # Handle different status results
            if status == "MSEED_READY":

                # Update the statusLabel before the potentially slow plotting
                statusText = "Plotting %s" % waveformID
                self.downloadStatusLabel.setText(statusText)
                self.downloadStatusLabel.repaint()
                QtGui.QApplication.processEvents()

                try:
                    # Generate a plot
                    imagePath = mseedFile.replace('MSEED','png')
                    self.logger.debug('reading %s', mseedFile)
                    st = obspy.core.read(mseedFile)
                    self.logger.debug('plotting %s', imagePath)
                    st.plot(outfile=imagePath, size=(plot_width,plot_height))

                    # Update the waveformsHandler
                    self.waveformsHandler.setWaveformImagePath(waveformID, imagePath)

                    # Update the Table
                    # Add imagePath to the WaveformImagePath table cell
                    self.selectionTable.setItem(row, column_names.index('WaveformImagePath'), QtGui.QTableWidgetItem(imagePath))
                    # Add a pixmap to the Waveform table cell
                    imageItem = MyTableWidgetImageWidget(self, imagePath)
                    self.selectionTable.setCellWidget(row, column_names.index('Waveform'), imageItem)

                except Exception as e:
                    # Update the selectionTable
                    self.selectionTable.setItem(row, column_names.index('WaveformImagePath'), QtGui.QTableWidgetItem('NO DATA AVAILABLE'))
                    self.selectionTable.setItem(row, column_names.index('Waveform'), QtGui.QTableWidgetItem('NO DATA AVAILABLE'))
                    # Update the waveformsHandler
                    self.waveformsHandler.setWaveformImagePath(waveformID, 'NO DATA AVAILABLE')
                    statusText = "No data available for %s" % waveformID

            else:
                # Problem downloading
                if message.find("No data available") >= 0:
                    statusText = "No data available for %s" % waveformID
                else:
                    statusText = message

                # Update the waveformsHandler
                self.waveformsHandler.setWaveformImagePath(waveformID, 'NO DATA AVAILABLE')

                # Update the Table
                # Set the selectionTable Waveform and WaveformImagePath columns
                self.selectionTable.setItem(row, column_names.index('WaveformImagePath'), QtGui.QTableWidgetItem('NO DATA AVAILABLE'))
                self.selectionTable.setItem(row, column_names.index('Waveform'), QtGui.QTableWidgetItem('NO DATA AVAILABLE'))

            # Tighten up the table
            # self.selectionTable.resizeColumnsToContents()
            self.selectionTable.resizeRowsToContents()

            # Update GUI
            QtGui.QApplication.processEvents()

            if self.downloadToolButton.isChecked():
                # Update status text
                self.downloadStatusLabel.setText(statusText)
                self.downloadStatusLabel.repaint()
                # Request more data
                self.downloadWaveformData()
            else:
                # Update status text
                self.downloadStatusLabel.setText('')
                self.downloadStatusLabel.repaint()

        return


    # NOTE:  http://stackoverflow.com/questions/12366521/pyqt-checkbox-in-qtablewidget
    # NOTE:  http://stackoverflow.com/questions/30462078/using-a-checkbox-in-pyqt
    def handleTableItemClicked(self, item):
        """
        Triggered whenever an item in the waveforms table is clicked.
        """
        # The checkbox column is named 'Keep'
        row = item.row()
        col = item.column()
        column_names = self.waveformsHandler.getColumnNames()
        keepItem = self.selectionTable.item(row, column_names.index('Keep'))

        LOGGER.debug("Clicked on table row")

        # Toggle the and Keep state
        waveformID = str(self.selectionTable.item(row,column_names.index('WaveformID')).text())
        if keepItem.checkState() == QtCore.Qt.Checked:
            keepItem.setCheckState(QtCore.Qt.Unchecked)
            self.waveformsHandler.setWaveformKeep(waveformID, False)
        else:
            keepItem.setCheckState(QtCore.Qt.Checked)
            self.waveformsHandler.setWaveformKeep(waveformID, True)

        return


    @QtCore.pyqtSlot()
    def loadWaveformChoices(self, filterColumn=None, filterText=None):
        """
        Fill the selectionTable with all SNCL-Event combinations selected in the MainWindow.
        This funciton is triggered whenever the "Get Waveforms" button in the MainWindow is clicked.
        """

        self.logger.debug('Loading waveform choices...')

        self.waveformsDownloadComplete = False

        ## Create a new dataframe with time, source_lat, source_lon, source_mag, source_depth, SNCL, network, station, receiver_lat, receiver_lon -- one for each waveform
        eventsDF = self.eventsHandler.get_selected_dataframe()
        stationsDF = self.stationsHandler.get_selected_dataframe()

        self.downloadStatusLabel.setText("Calculating distances...")
        self.downloadStatusLabel.repaint()

        waveformsDF = self.waveformsHandler.createWaveformsDF(eventsDF, stationsDF)

        self.downloadStatusLabel.setText("")
        self.downloadStatusLabel.repaint()

        self.logger.debug('Finished building dataframe for %d waveforms', waveformsDF.shape[0])

        # Add event-SNCL combintations to the selection table
        self.loadSelectionTable(waveformsDF)

        # Tighten up the table
        self.selectionTable.resizeColumnsToContents()
        self.selectionTable.horizontalHeader().setStretchLastSection(True)

        # Add unique events to the eventComboBox -------------------------------

        for i in range(self.eventComboBox.count()):
            self.eventComboBox.removeItem(0)

        self.eventComboBox.addItem('All events')
        for i in range(eventsDF.shape[0]):
            self.eventComboBox.addItem(eventsDF.Time.iloc[i])

        # Add unique networks to the networkComboBox ---------------------------

        for i in range(self.networkComboBox.count()):
            self.networkComboBox.removeItem(0)

        self.networkComboBox.addItem('All networks')
        for network in stationsDF.Network.unique().tolist():
            self.networkComboBox.addItem(network)

        # Add unique stations to the stationsComboBox --------------------------

        for i in range(self.stationComboBox.count()):
            self.stationComboBox.removeItem(0)

        self.stationComboBox.addItem('All stations')
        for station in stationsDF.Station.unique().tolist():
            self.stationComboBox.addItem(station)

        self.logger.debug('Finished loading waveform choices')

        # Initialize saveToolButton to OFF/UP
        self.saveToolButton.setEnabled(True)
        self.saveToolButton.setChecked(False)
        self.saveToolButton.setDown(False)
        self.toggledSaveToolButton() # trigger toggled action

        # Initialize downloadToolButton to ON/DOWN
        self.downloadToolButton.setEnabled(True)
        self.downloadToolButton.setChecked(True)
        self.downloadToolButton.setDown(True)
        self.toggledDownloadToolButton() # trigger toggled action

        return



    @QtCore.pyqtSlot()
    def loadSelectionTable(self, waveformsDF):
        """
        Add event-SNCL combintations to the selection table
        """

        self.logger.debug('Loading waveform selection table...')

        self.visibleWaveformsDF = waveformsDF

        # NOTE:  You must disable sorting before populating the table. Otherwise rows get
        # NOTE:  sorted as soon as the sortable column gets filled in, thus invalidating
        # NOTE:  the row number
        self.selectionTable.setSortingEnabled(False)

        # Note:  Display information should be in the GUI code but needs to match
        # NOTE:  the columns which are created by the waveformsHandler.
        hidden_column = self.waveformsHandler.getColumnHidden()
        numeric_column = self.waveformsHandler.getColumnNumeric()

        # Clear existing contents
        self.selectionTable.clear() # This is important!
        while (self.selectionTable.rowCount() > 0):
            self.selectionTable.removeRow(0)

        # Create new table
        self.selectionTable.setRowCount(waveformsDF.shape[0])
        self.selectionTable.setColumnCount(waveformsDF.shape[1])
        self.selectionTable.setHorizontalHeaderLabels(waveformsDF.columns.tolist())
        self.selectionTable.horizontalHeader().setStretchLastSection(True)
        self.selectionTable.verticalHeader().hide()
        # Hidden columns
        for i in np.arange(len(hidden_column)):
            if hidden_column[i]:
                self.selectionTable.setColumnHidden(i,True)

        # Add new contents
        for i in range(waveformsDF.shape[0]):
            for j in range(waveformsDF.shape[1]):
                if numeric_column[j]:
                    # Guarantee that all elements are converted to strings for display but apply proper sorting
                    self.selectionTable.setItem(i, j, MyNumericTableWidgetItem(str(waveformsDF.iat[i,j])))

                elif waveformsDF.columns[j] == 'Waveform':
                    # NOTE:  What to put in the Waveform column depends on what is in the WaveformImagePath column.
                    # NOTE:  It could be plain text or an imageWidget.
                    if waveformsDF.WaveformImagePath.iloc[i] == '':
                        self.selectionTable.setItem(i, j, QtGui.QTableWidgetItem(''))
                    elif waveformsDF.WaveformImagePath.iloc[i] == 'NO DATA AVAILABLE':
                        self.selectionTable.setItem(i, j, QtGui.QTableWidgetItem('NO DATA AVAILABLE'))
                    else:
                        imagePath = waveformsDF.WaveformImagePath.iloc[i]
                        imageItem = MyTableWidgetImageItem(imagePath)
                        self.selectionTable.setItem(i, j, imageItem)

                elif waveformsDF.columns[j] == 'Keep':
                    checkBoxItem = QtGui.QTableWidgetItem()
                    checkBoxItem.setFlags(QtCore.Qt.ItemIsEnabled)
                    if self.waveformsHandler.getWaveformKeep(waveformsDF.WaveformID.iloc[i]):
                        checkBoxItem.setCheckState(QtCore.Qt.Checked)
                    else:
                        checkBoxItem.setCheckState(QtCore.Qt.Unchecked)
                    self.selectionTable.setItem(i, j, checkBoxItem)

                else:
                    # Anything else is converted to normal text
                    self.selectionTable.setItem(i, j, QtGui.QTableWidgetItem(str(waveformsDF.iat[i,j])))

        # Tighten up the table
        # self.selectionTable.resizeColumnsToContents()
        self.selectionTable.resizeRowsToContents()

        # Restore table sorting
        self.selectionTable.setSortingEnabled(True)

        self.logger.debug('Finished loading waveform selection table')

        self.downloadWaveformData()

        return


    @QtCore.pyqtSlot(int)
    def loadFilteredSelectionTable(self):
        """
        Filter waveformsDF based on filter selections and then reload the selectionTable.
        """
        waveformsDF = self.waveformsHandler.currentDF
        time = self.eventComboBox.currentText()
        network = self.networkComboBox.currentText()
        station = self.stationComboBox.currentText()
        self.logger.debug('Filtering waveformsDF...')
        if not time.startswith('All'):
            waveformsDF = waveformsDF[waveformsDF.Time == time]
        if not network.startswith('All'):
            waveformsDF = waveformsDF[waveformsDF.Network == network]
        if not station.startswith('All'):
            waveformsDF = waveformsDF[waveformsDF.Station == station]
        self.logger.debug('Finished filtering waveformsDF')
        self.loadSelectionTable(waveformsDF)

        # Tighten up the table
        #self.selectionTable.resizeColumnsToContents()
        #self.selectionTable.resizeRowsToContents()

        return


    @QtCore.pyqtSlot()
    def toggledDownloadToolButton(self):
        """
        Triggered after downloadToolButton is toggled.
        """

        if self.downloadToolButton.isChecked():
            if self.waveformsDownloadComplete:
                # pop the button back up and enable Download GUI elements
                self.downloadToolButton.setText('Download Finished')
                self.downloadGroupBox.setStyleSheet("QGroupBox { background-color: #e7e7e7 } ")
                self.secondsBeforeSpinBox.setEnabled(True)
                self.secondsAfterSpinBox.setEnabled(True)
                self.secondsBeforeLabel.setStyleSheet('color: black')
                self.secondsAfterLabel.setStyleSheet('color: black')
                self.downloadToolButton.setChecked(False)
                self.downloadToolButton.setDown(False)
            else:
                # leave the button down and disable Download GUI elements
                self.downloadToolButton.setText('Downloading...')
                self.downloadGroupBox.setStyleSheet("QGroupBox { background-color: #EEDC82 } ") # light goldenrod 2
                self.secondsBeforeSpinBox.setEnabled(False)
                self.secondsAfterSpinBox.setEnabled(False)
                self.secondsBeforeLabel.setStyleSheet('color: gray')
                self.secondsAfterLabel.setStyleSheet('color: gray')
                # Resume downloading
                self.downloadWaveformData()

        else:
            # leave the button up and enable Download GUI elements
            if self.waveformsDownloadComplete:
                self.downloadToolButton.setText('Download Finished')
            else:
                self.downloadToolButton.setText('Download Stopped')
            self.downloadGroupBox.setStyleSheet("QGroupBox { background-color: #e7e7e7 } ")
            self.secondsBeforeSpinBox.setEnabled(True)
            self.secondsAfterSpinBox.setEnabled(True)
            self.secondsBeforeLabel.setStyleSheet('color: black')
            self.secondsAfterLabel.setStyleSheet('color: black')


        return


    @QtCore.pyqtSlot()
    def toggledSaveToolButton(self):
        """
        Triggered after saveToolButton is toggled.
        """

        formatChoice = str(self.saveFormatComboBox.currentText())

        # Saving down/on
        if self.saveToolButton.isChecked():
            # disable GUI elements
            self.saveDirectoryPushButton.setEnabled(False)
            self.saveFormatComboBox.setEnabled(False)
            self.saveDirectoryLabel.setStyleSheet('color: gray')
            self.saveFormatLabel.setStyleSheet('color: gray')
            if self.waveformsDownloadComplete:
                if self.waveformsSaveComplete.find(formatChoice) >= 0:
                    self.saveToolButton.setText('Save Finished')
                else:
                    self.saveToolButton.setText('Saving...')
                    self.saveWaveformData()
            else:
                self.saveToolButton.setText('Save Scheduled')
                self.saveStatusLabel.setText("Wating for downloads to finish...")

        # Saving up/off
        else:
            # Enable GUI elements
            self.saveDirectoryPushButton.setEnabled(True)
            self.saveFormatComboBox.setEnabled(True)
            self.saveDirectoryLabel.setStyleSheet('color: black')
            self.saveFormatLabel.setStyleSheet('color: black')
            if self.waveformsDownloadComplete:
                if self.waveformsSaveComplete.find(formatChoice) >= 0:
                    self.saveToolButton.setText('Save Finished')
                else:
                    self.saveToolButton.setText('Save Stopped')
            else:
                self.saveToolButton.setText('No Save Scheduled')
                self.saveStatusLabel.setText("")

        return


    @QtCore.pyqtSlot()
    def resetDownload(self):
        """
        This function is triggered whenever the values in secondsBeforeSpinBox or
        secondsAfterSpinBox are changed. Any change means that we need to wipe out
        all the downloads that have occurred and start over.
        """
        self.waveformsDownloadComplete = False
        self.resetSave()
        self.waveformsHandler.currentDF.WaveformImagePath = ''
        self.loadSelectionTable(self.waveformsHandler.currentDF)


    @QtCore.pyqtSlot()
    def resetSave(self):
        """
        This function is triggered whenever the values in saveDirectory or
        saveFormat elements are changed. Any change means that we need to
        start saving from the beginning.
        """
        self.waveformsSaveComplete = ""
        if self.waveformsDownloadComplete:
            self.saveStatusLabel.setText("")
        else:
            self.saveStatusLabel.setText("Waiting for downloads to finish...")


    @QtCore.pyqtSlot()
    def downloadWaveformData(self):
        """
        This function is triggered after the selectionTable is initially loaded
        by loadWaveformChoices() and, after that, by handleWaveformResponse() after
        it has finished handling a waveform.

        This function looks at the current selectionTable view for any waveforms
        that have not yet been downloaded. After that table is exhausted, it goes
        through all not-yet-downloaded data in waveformHandler.currentDF.
        """

        # Update GUI in case we came from an internal call
        QtGui.QApplication.processEvents()

        # WaveformDialog status text
        statusText = ''

        secondsBefore = self.secondsBeforeSpinBox.value()
        secondsAfter = self.secondsAfterSpinBox.value()

        # Priority is given to waveforms shown on the screen
        priority_waveforms = self.visibleWaveformsDF
        all_waveforms = self.waveformsHandler.currentDF
        other_waveforms = all_waveforms[~all_waveforms.WaveformID.isin(priority_waveforms.WaveformID)]

        self.waveformsHandler.download_waveforms(
            priority_waveforms.WaveformID, other_waveforms.WaveformID,
            secondsBefore, secondsAfter)

    def on_log(self, msg):
        self.logger.debug(msg)

    def get_table_row(self, waveform_id):
        column_names = self.waveformsHandler.getColumnNames()
        row = 0
        for row in range(self.selectionTable.rowCount()):
            if self.selectionTable.item(row, column_names.index('WaveformID')).text() == waveform_id:
                return row
        return None

    def on_waveform_downloaded(self, result):
        waveform_id = result.waveform_id
        self.logger.debug("Ready to display waveform %s", waveform_id)

        row = self.get_table_row(waveform_id)
        if row is None:
            self.logger.error("Couldn't find a row for waveform %s", waveform_id)
            return

        column_names = self.waveformsHandler.getColumnNames()

        if isinstance(result.result, Exception):
            self.logger.error("Error retrieving %s: %s", waveform_id, result.result)
            self.selectionTable.setItem(row, column_names.index('WaveformImagePath'), QtGui.QTableWidgetItem('NO DATA AVAILABLE'))
            self.selectionTable.setItem(row, column_names.index('Waveform'), QtGui.QTableWidgetItem('NO DATA AVAILABLE'))
        else:
            image_path = result.result
            self.selectionTable.setItem(row, column_names.index('WaveformImagePath'), QtGui.QTableWidgetItem(image_path))
            # Add a pixmap to the Waveform table cell
            imageItem = MyTableWidgetImageWidget(self, image_path)
            self.selectionTable.setCellWidget(row, column_names.index('Waveform'), imageItem)

        self.logger.debug("Displayed waveform %s", waveform_id)

        # Tighten up the table
        self.selectionTable.resizeColumnsToContents()
        self.selectionTable.resizeRowsToContents()

    def on_all_downloaded(self, result):
        self.waveformsDownloadComplete = True
        self.downloadToolButton.setEnabled(True) # TODO:  set this to False
        self.downloadToolButton.setChecked(False) # up/off
        self.downloadToolButton.setDown(False) # up/off
        self.toggledDownloadToolButton()
        self.logger.debug('COMPLETED all downloads')

        statusText = "Completed all downloads"


        # Update GUI
        QtGui.QApplication.processEvents()

        # Update status text
        self.downloadStatusLabel.setText(statusText)
        self.downloadStatusLabel.repaint()

        # Save data if appropriate
        if self.waveformsDownloadComplete:
            if self.saveToolButton.isChecked():
                self.saveWaveformData()

        return


    @QtCore.pyqtSlot()
    def saveWaveformData(self):
        """
        Save waveforms after all downloads are complete.
        """

        inputDir = self.waveformsHandler.downloadDir
        outputDir = self.waveformDirectory # TODO:  change to saveDir

        # Handle user format choice
        formatChoice = str(self.saveFormatComboBox.currentText())
        if formatChoice == 'ASCII':
            outputFormat = 'TSPAIR'
            extension = 'ascii'
        elif formatChoice == 'GSE2':
            outputFormat = 'GSE2'
            extension = 'gse'
        elif formatChoice == 'MSEED':
            outputFormat = 'MSEED'
            extension = 'mseed'
        elif formatChoice == 'SAC':
            outputFormat = 'SAC'
            extension = 'sac'
        else:
            self.logger.error('Output format "%s" not recognized' % formatChoice)
            self.saveStatusLabel.setText('Output format "%s" not recognized' % formatChoice)
            self.saveStatusLabel.repaint()
            return

        self.saveGroupBox.setStyleSheet("QGroupBox { background-color: #EEDC82 } ") # light goldenrod 2
        self.saveToolButton.setText('Saving...')

        # Total to be saved
        keep = self.waveformsHandler.currentDF.Keep
        waveformImagePath = self.waveformsHandler.currentDF.WaveformImagePath
        waveformAvailable = np.invert( waveformImagePath.str.contains("NO DATA AVAILABLE"))
        totalCount = sum(keep & waveformAvailable)

        # Loop over the table, read in and convert all waveforms that are selected and available
        savedCount = 0
        for row in range(self.waveformsHandler.currentDF.shape[0]):
            keep = self.waveformsHandler.currentDF.Keep.iloc[row]
            waveformID = self.waveformsHandler.currentDF.WaveformID.iloc[row]
            waveformImagePath = self.waveformsHandler.currentDF.WaveformImagePath.iloc[row]
            if keep and (waveformImagePath != "NO DATA AVAILABLE"):
                mseedPath = waveformImagePath.replace('.png','.MSEED')
                mseedFile = os.path.basename(mseedPath)
                outputFile = mseedFile.replace('MSEED',extension)
                outputPath = os.path.join(outputDir,outputFile)
                # Don't repeat any work that has already been done
                if not os.path.exists(outputPath):
                    statusText = "Saving %s " % (outputFile)
                    self.logger.debug('reading %s', mseedFile)
                    st = obspy.core.read(mseedPath)
                    self.logger.debug('writing %s', outputPath)
                    st.write(outputPath, format=outputFormat)

                savedCount += 1
                self.saveStatusLabel.setText("Saved %d / %d waveforms as %s" % (savedCount,totalCount,formatChoice))
                self.saveStatusLabel.repaint()
                QtGui.QApplication.processEvents() # update GUI

                # Return early if the user has toggled off the saveToolButton
                if not self.saveToolButton.isChecked():
                    return

        # Toggle saveToolButton state
        self.waveformsSaveComplete += formatChoice + ","
        self.saveToolButton.setEnabled(True)
        self.saveToolButton.setChecked(False) # up/off
        self.saveToolButton.setDown(False) # up/off
        self.toggledSaveToolButton()
        self.saveGroupBox.setStyleSheet("QGroupBox { background-color: #e7e7e7 } ")

        self.logger.debug('COMPLETED saving all waveforms')


    @QtCore.pyqtSlot()
    def getWaveformDirectory(self):
        """
        This function is triggered whenever the user presses the "to <directory>" button.
        """

        # If the user quits or cancels this dialog, '' is returned
        newDirectory = str(QtGui.QFileDialog.getExistingDirectory(
            self,
            "Waveform Directory",
            os.path.expanduser("~"),
            QtGui.QFileDialog.ShowDirsOnly))

        if newDirectory != '':
            self.waveformDirectory = newDirectory
            self.saveDirectoryPushButton.setText(self.waveformDirectory)
            self.resetSave()


# ----- Request/Response watchers ----------------------------------------------

# NOTE:  http://stackoverflow.com/questions/9957195/updating-gui-elements-in-multithreaded-pyqt
class waveformResponseWatcherThread(QtCore.QThread):
    """
    This thread is started when the WaveformsDialog initializes.

    When a message appears on the waveformResponseQueue, this thread
    emits a waveformResponseSignal which then triggers waveformResponseHandler().
    """
    waveformResponseSignal = QtCore.pyqtSignal()

    def __init__(self, waveformResponseQueue):
        QtCore.QThread.__init__(self)
        self.waveformResponseQueue = waveformResponseQueue

    def run(self):
        """
        Wait for entries to appear on the queue and then signal the main
        thread that data are available.
        """
        while True:
            # NOTE:  A small sleep gives the main thread a chance to respond to GUI events
            time.sleep(0.2)
            if not self.waveformResponseQueue.empty():
                self.waveformResponseSignal.emit()


# NOTE:  http://stackoverflow.com/questions/9957195/updating-gui-elements-in-multithreaded-pyqt
class waveformRequestWatcherThread(QtCore.QThread):
    """
    This thread is started when the WaveformsDialog initializes.

    When a message appears on the waveformRequestQueue, this thread
    emits a waveformRequestSignal which then triggers waveformRequestHandler().
    """
    waveformRequestSignal = QtCore.pyqtSignal()

    def __init__(self, waveformRequestQueue):
        QtCore.QThread.__init__(self)
        self.waveformRequestQueue = waveformRequestQueue

    def run(self):
        """
        Wait for entries to appear on the queue and then signal the main
        thread that a request has been made.
        """
        while True:
            # NOTE:  A small sleep gives the main thread a chance to respond to GUI events
            time.sleep(0.2)
            if not self.waveformRequestQueue.empty():
                self.waveformRequestSignal.emit()


# ----- Splash Screen ------------------------------------------------------------

class SplashScreenHandler(logging.Handler):

    def __init__(self, mainWidget):
        super(SplashScreenHandler, self).__init__(level=logging.INFO)
        self.mainWidget = mainWidget
        pixmap = QtGui.QPixmap("splash.png")
        self.splash = QtGui.QSplashScreen(pixmap)
        self.splash.show()
        # self.splash.finish(mainWidget)

    def emit(self, record):
        msg = self.format(record)
        self.splash.showMessage(msg)
        QtGui.QApplication.processEvents()

    def close(self):
        super(SplashScreenHandler, self).close()
        self.splash.finish(self.mainWidget)


# ----- Main Window ------------------------------------------------------------

class MainWindow(QtGui.QMainWindow, MainWindow.Ui_MainWindow):

    def __init__(self,parent=None):

        # Load configurable preferences from ~/.pyweed/config.ini
        self.preferences = Preferences()
        try:
            self.preferences.load()
        except Exception as e:
            print("Unable to load configuration preferences -- using defaults.\n%s" % e)
            pass

        # Logging
        # see:  http://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
        # see:  http://stackoverflow.com/questions/24469662/how-to-redirect-logger-output-into-pyqt-text-widget
        self.logger = logging.getLogger()
        try:
            logLevel = getattr(logging, self.preferences.Logging.level)
            self.logger.setLevel(logLevel)
        except Exception as e:
            self.logger.setLevel(logging.DEBUG)
        self.loggingDialog = LoggingDialog(self, self.logger)

        splashScreenHandler = SplashScreenHandler(self)
        self.logger.addHandler(splashScreenHandler)
        self.logger.addHandler(logging.StreamHandler())

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

        # Make sure the waveform download directory exists and isn't full
        waveformDownloadDir = self.preferences.Waveforms.downloadDir
        waveformCacheSize = float(self.preferences.Waveforms.cacheSize)
        self.logger.info('Checking on download directory...')
        if os.path.exists(waveformDownloadDir):
            manageCache(waveformDownloadDir, waveformCacheSize, self.logger)
        else:
            try:
                os.makedirs(waveformDownloadDir, 0700)
            except Exception as e:
                self.logger.error("Creation of download directory failed with" + " error: \"%s\'""" % e)
                SystemExit()

        # Set up the ObsPy FDSN client
        # Important preferences
        self.dataCenter = "IRIS" # TODO:  dataCenter should be configurable

        # Instantiate a client
        self.logger.info("Creating ObsPy client for %s" % self.dataCenter)
        self.client = fdsn.Client(self.dataCenter)

        # Get the Figure object from the map_canvas
        self.logger.info('Setting up main map...')
        self.map_figure = self.map_canvas.fig
        self.map_axes = self.map_figure.add_axes([0.01, 0.01, .98, .98])
        self.map_axes.clear()
        prefs = self.preferences.Map
        self.seismap = Seismap(projection=prefs.projection, ax=self.map_axes) # 'cyl' or 'robin' or 'mill'
        self.map_figure.canvas.draw()

        # Events
        self.logger.info('Setting up event options dialog...')
        self.eventQueryDialog = EventQueryDialog(self)
        self.eventsHandler = EventsHandler(self.client)
        self.eventsHandler.done.connect(self.on_events_loaded)
        self.eventsHandler.log.connect(self.log)
        self.eventsTable.setSortingEnabled(True)
        self.eventsTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.eventsTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # Stations
        self.logger.info('Setting up station options dialog...')
        self.stationQueryDialog = StationQueryDialog(self)
        self.stationsHandler = StationsHandler(self.logger, self.preferences, self.client)
        self.stationsTable.setSortingEnabled(True)
        self.stationsTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.stationsTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # Connect signals associated with table clicks
        # see:  http://zetcode.com/gui/pyqt4/eventsandsignals/
        # see:  https://wiki.python.org/moin/PyQt/Sending%20Python%20values%20with%20signals%20and%20slots
        QtCore.QObject.connect(self.eventsTable, QtCore.SIGNAL('cellClicked(int, int)'), self.eventsTableClicked)
        QtCore.QObject.connect(self.stationsTable, QtCore.SIGNAL('cellClicked(int, int)'), self.stationsTableClicked)

        # Waveforms
        # NOTE:  The WaveformsHandler is created inside waveformsDialog.  It is only relevant to that Dialog.
        self.logger.info('Setting up waveforms dialog...')
        self.waveformsDialog = WaveformDialog(self)
        self.getWaveformsButton.setEnabled(False)

        self.logger.info('Setting up main window...')

        # Connect the main window buttons
        self.getEventsButton.clicked.connect(self.getEvents)
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

        console = ConsoleDialog(self)
        console.show()

        # Display MainWindow
        self.logger.info('Showing main window...')
        self.show()

        splashScreenHandler.close()

    def log(self, msg):
        self.logger.info(msg)

    @QtCore.pyqtSlot()
    def getEvents(self):
        """
        Get events dataframe from IRIS.
        """
        self.getEventsButton.setEnabled(False)
        self.logger.info('Loading events...')
        self.statusBar().showMessage('Loading events...')

        # Get events and subset to desired columns
        parameters = self.eventQueryDialog.getOptions()
        # TODO:  handle errors when querying events
        self.eventsHandler.load_data(parameters=parameters)

    def on_events_loaded(self, eventsDF):

        self.getEventsButton.setEnabled(True)

        if isinstance(eventsDF, Exception):
            msg = "Error loading events: %s" % eventsDF
            self.logger.error(msg)
            self.statusBar().showMessage(msg)
            return

        # NOTE:  Here is the list of all column names:
        # NOTE:         ['Time', 'Magnitude', 'Longitude', 'Latitude', 'Depth/km', 'MagType', 'EventLocationName', 'Author', 'Catalog', 'Contributor', 'ContributorID', 'MagAuthor', 'EventID']
        hidden_column = [ False,  False,       False,       False,      False,      False,     False,               True,     True,      True,          True,            True,        True]
        numeric_column = [False,  True,        True,        True,       True,       False,     False,               False,    False,     False,         False,           False,       False]

        # Add events to the events table ---------------------------------------

        self.logger.debug('Received %d events, ', eventsDF.shape[0])

        # Clear existing contents
        self.eventsTable.clearSelection() # This is important!
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

        self.logger.info('Loaded %d events', eventsDF.shape[0])
        self.statusBar().showMessage('Loaded %d events' % (eventsDF.shape[0]))

    @QtCore.pyqtSlot()
    def getStations(self):
        """
        Get stations dataframe from IRIS.
        """
        self.logger.info('Loading channels...')
        self.statusBar().showMessage('Loading channels...')

        # Get stations and subset to desired columns
        parameters = self.stationQueryDialog.getOptions()
        # TODO:  handle errors when querying stations
        stationsDF = self.stationsHandler.load_data(parameters=parameters)
        # NOTE:  Here is the list of all column names:
        # NOTE:         ['Network', 'Station', 'Location', 'Channel', 'Longitude', 'Latitude', 'Elevation', 'Depth', 'Azimuth', 'Dip', 'SensorDescription', 'Scale', 'ScaleFreq', 'ScaleUnits', 'SampleRate', 'StartTime', 'EndTime', 'SNCL']
        hidden_column = [ False,     False,     False,      False,     False,       False,      True,        True,    True,      True,  True,                True,    True,        True,         True,         True,        True,      True]
        numeric_column = [False,     False,     False,      False,     True,        True,       True,        True,    True,      True,  False,               True,    True,        False,        True,         False,       False,     False]

        # Add stations to the stations table -----------------------------------

        self.logger.debug('Received %d channels, ', stationsDF.shape[0])

        # Clear existing contents
        self.stationsTable.clearSelection() # This is important!
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

        self.logger.info('Loaded %d channels', stationsDF.shape[0])
        self.statusBar().showMessage('Loaded %d channels' % (stationsDF.shape[0]))


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

        self.manageGetWaveformsButton()


    @QtCore.pyqtSlot(int, int)
    def stationsTableClicked(self, row, col):
        # Get selected rows
        rows = []
        for idx in self.stationsTable.selectionModel().selectedRows():
            rows.append(idx.row())

        self.logger.debug('%d stations currently selected', len(rows))

        # Get lons and lats
        # TODO:  Automatically detect longitude and latitude columns
        lons = []
        lats = []
        SNCLs = []
        for row in rows:
            lon = float(self.stationsTable.item(row,4).text())
            lons.append(lon)
            lat = float(self.stationsTable.item(row,5).text())
            lats.append(lat)
            SNCL = str(self.stationsTable.item(row,17).text())
            SNCLs.append(SNCL)

        # Update the stationsHandler with the latest selection information
        self.stationsHandler.set_selected_ids(SNCLs)

        self.seismap.add_stations_highlighting(lons, lats)

        self.manageGetWaveformsButton()


    def manageGetWaveformsButton(self):
        """
        Handle enabled/disabled status of the "Get Waveforms" button
        based on the presence/absence of selected events and stations
        """
        # http://stackoverflow.com/questions/3345785/getting-number-of-elements-in-an-iterator-in-python
        selectedEventsCount = sum(1 for idx in self.eventsTable.selectionModel().selectedRows() )
        selectedStationsCount = sum(1 for idx in self.stationsTable.selectionModel().selectedRows() )

        if selectedEventsCount > 0 and selectedStationsCount > 0:
            self.getWaveformsButton.setEnabled(True)
        else:
            self.getWaveformsButton.setEnabled(False)


    def aboutPyweed(self):
        """Display About message box."""
        # see:  http://www.programcreek.com/python/example/62361/PyQt4.QtGui.QMessageBox
        website = "https://github.com/iris-edu-int/pyweed"
        ###email = "adam@iris.washington.edu"
        license_link = "https://github.com/iris-edu-int/pyweed/blob/master/LICENSE"
        license_name = "MIT"
        mazama_link = "http://mazamascience.com"
        mazama_name = "Mazama Science"
        iris_link = "http://ds.iris.edu/ds/nodes/dmc/"
        iris_name = "IRIS"

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
                       ###"<a href='mailto:{0}'>{0}</a><br><br>".format(email) +
                       "License: <a href='{0}'>{1}</a>".format(license_link, license_name) +
                       "<br><br>" +
                       "Developed by <a href='{0}'>{1}</a>".format(mazama_link, mazama_name) +
                       " for <a href='{0}'>{1}</a>".format(iris_link, iris_name) +
                       ".")

        msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
        msgBox.exec_()
        # NOTE:  For info on " modalSession has been exited prematurely" error on OS X see:
        # NOTE:    https://forum.qt.io/topic/43618/modal-sessions-with-pyqt4-and-os-x/2


    def closeApplication(self):
        # Manage the waveform cache
        waveformDownloadDir = self.preferences.Waveforms.downloadDir
        waveformCacheSize = self.preferences.Waveforms.cacheSize
        self.logger.debug('Managing the waveform cache...')
        if os.path.exists(waveformDownloadDir):
            manageCache(waveformDownloadDir, waveformCacheSize, self.logger)

        self.logger.info('Closing application...')
        QtGui.QApplication.quit()


if __name__ == "__main__":

    pd.set_option('mode.chained_assignment','raise')
    app = QtGui.QApplication(sys.argv)
    # app.setStyleSheet(stylesheet)
    GUI = MainWindow()
    sys.exit(app.exec_())

