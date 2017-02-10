"""
Main window

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

from PyQt4 import QtGui, QtCore
from gui.uic import MainWindow
from preferences import Preferences, safe_int, safe_bool, bool_to_str
import logging
from gui.LoggingDialog import LoggingDialog
from gui.SplashScreenHandler import SplashScreenHandler
import os
from pyweed_utils import manageCache
from obspy.clients import fdsn
from seismap import Seismap
from events_handler import EventsHandler
from stations_handler import StationsHandler
from gui.WaveformDialog import WaveformDialog
from gui.ConsoleDialog import ConsoleDialog
import numpy as np
from gui.MyNumericTableWidgetItem import MyNumericTableWidgetItem
from gui.EventOptionsWidget import EventOptionsWidget
from gui.StationOptionsWidget import StationOptionsWidget

LOGGER = logging.getLogger(__name__)


class MainWindow(QtGui.QMainWindow, MainWindow.Ui_MainWindow):

    def __init__(self, pyweed):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.pyweed = pyweed

    def initialize(self):
        prefs = self.pyweed.preferences
        # Set MainWindow properties
        self.setWindowTitle('%s version %s' % (prefs.App.name, prefs.App.version))

        self.eventOptionsWidget = EventOptionsWidget(parent=self)
        self.eventOptionsWidget.setOptions(self.pyweed.event_options)
        self.eventOptionsDockWidget.setWidget(self.eventOptionsWidget)
        self.toggleEventOptions.toggled.connect(self.eventOptionsDockWidget.setVisible)
        self.eventOptionsDockWidget.visibilityChanged.connect(self.toggleEventOptions.setChecked)

        self.stationOptionsWidget = StationOptionsWidget(parent=self)
        self.stationOptionsWidget.setOptions(self.pyweed.station_options)
        self.stationOptionsDockWidget.setWidget(self.stationOptionsWidget)
        self.toggleStationOptions.toggled.connect(self.stationOptionsDockWidget.setVisible)
        self.stationOptionsDockWidget.visibilityChanged.connect(self.toggleStationOptions.setChecked)

        self.eventsTable.itemSelectionChanged.connect(self.onEventSelectionChanged)
        self.stationsTable.itemSelectionChanged.connect(self.onStationSelectionChanged)

        self.getWaveformsButton.setEnabled(False)

        # Connect the main window buttons
        self.getEventsButton.clicked.connect(self.getEvents)
        self.getStationsButton.pressed.connect(self.getStations)
        self.getWaveformsButton.pressed.connect(self.getWaveforms)

        # Get the Figure object from the map_canvas
        LOGGER.info('Setting up main map...')
        self.map_figure = self.mapCanvas.fig
        self.map_axes = self.map_figure.add_axes([0.01, 0.01, .98, .98])
        self.map_axes.clear()
        self.seismap = Seismap(projection=prefs.Map.projection, ax=self.map_axes) # 'cyl' or 'robin' or 'mill'
        self.map_figure.canvas.draw()

        # TODO: Basic mouse event handling
        def on_press(event):
            LOGGER.debug('you pressed', event.button, event.xdata, event.ydata)
        cid = self.mapCanvas.mpl_connect('button_press_event', on_press)

        self.resize(
            safe_int(prefs.MainWindow.width, 1000),
            safe_int(prefs.MainWindow.height, 800))
        self.eventOptionsDockWidget.setFloating(safe_bool(prefs.MainWindow.eventOptionsFloat, False))
        self.stationOptionsDockWidget.setFloating(safe_bool(prefs.MainWindow.stationOptionsFloat, False))


    def fillTable(self, table, dataframe, visibleColumns, numericColumns):
        """
        Common code for filling event/station tables with data
        """
        LOGGER.info("Filling table")

        # Clear existing contents
        table.clearSelection() # This is important!
        while (table.rowCount() > 0):
            table.removeRow(0)

        # Column names
        columnNames = dataframe.columns.tolist()

        # Create new table
        table.setRowCount(dataframe.shape[0])
        table.setColumnCount(dataframe.shape[1])
        table.setHorizontalHeaderLabels(columnNames)
        table.verticalHeader().hide()

        # Hidden columns
        for i, column in enumerate(columnNames):
            table.setColumnHidden(i, column not in visibleColumns)

        # Add new contents
        for i in range(dataframe.shape[0]):
            for j in range(dataframe.shape[1]):
                # Guarantee that all elements are converted to strings for display but apply proper sorting
                if columnNames[j] in numericColumns:
                    table.setItem(i, j, MyNumericTableWidgetItem(str(dataframe.iat[i, j])))
                else:
                    table.setItem(i, j, QtGui.QTableWidgetItem(str(dataframe.iat[i, j])))

        # Tighten up the table
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

    @QtCore.pyqtSlot()
    def getEvents(self):
        """
        Get events dataframe from IRIS.
        """
        self.getEventsButton.setEnabled(False)
        LOGGER.info('Loading events...')
        self.statusBar.showMessage('Loading events...')

        options = self.eventOptionsWidget.getOptions()
        self.pyweed.set_event_options(options)

        self.pyweed.fetch_events()

    def onEventsLoaded(self, eventsDF):
        """
        Handler triggered when the EventsHandler finishes loading events
        """
        self.getEventsButton.setEnabled(True)

        if isinstance(eventsDF, Exception):
            msg = "Error loading events: %s" % eventsDF
            LOGGER.error(msg)
            self.statusBar.showMessage(msg)
            return

        visibleColumns = [
            'Time', 'Magnitude', 'Longitude', 'Latitude', 'Depth/km',
            'MagType', 'EventLocationName',
        ]
        numericColumns = [
            'Magnitude', 'Longitude', 'Latitude', 'Depth/km',
        ]

        self.fillTable(self.eventsTable, eventsDF, visibleColumns, numericColumns)

        # Add items to the map -------------------------------------------------

        self.seismap.add_events(eventsDF)

        if self.eventOptionsWidget.locationRangeRadioButton.isChecked():
            n = self.eventOptionsWidget.locationRangeNorthDoubleSpinBox.value()
            e = self.eventOptionsWidget.locationRangeEastDoubleSpinBox.value()
            s = self.eventOptionsWidget.locationRangeSouthDoubleSpinBox.value()
            w = self.eventOptionsWidget.locationRangeWestDoubleSpinBox.value()
            self.seismap.add_events_box(n, e, s, w)
        elif self.eventOptionsWidget.locationDistanceFromPointRadioButton.isChecked():
            n = self.eventOptionsWidget.distanceFromPointNorthDoubleSpinBox.value()
            e = self.eventOptionsWidget.distanceFromPointEastDoubleSpinBox.value()
            minradius = self.eventOptionsWidget.distanceFromPointMinRadiusDoubleSpinBox.value()
            maxradius = self.eventOptionsWidget.distanceFromPointMaxRadiusDoubleSpinBox.value()
            self.seismap.add_events_toroid(n, e, minradius, maxradius)

        LOGGER.info('Loaded %d events', eventsDF.shape[0])
        self.statusBar.showMessage('Loaded %d events' % (eventsDF.shape[0]))

    @QtCore.pyqtSlot()
    def getStations(self):
        """
        Get events dataframe from IRIS.
        """
        self.getStationsButton.setEnabled(False)
        LOGGER.info('Loading channels...')
        self.statusBar.showMessage('Loading channels...')

        # Get stations and subset to desired columns
        options = self.stationOptionsWidget.getOptions()

        self.pyweed.set_station_options(options)
        self.pyweed.fetch_stations()

    def onStationsLoaded(self, stationsDF):
        """
        Handler triggered when the StationsHandler finishes loading stations
        """

        self.getStationsButton.setEnabled(True)

        if isinstance(stationsDF, Exception):
            msg = "Error loading stations: %s" % stationsDF
            LOGGER.error(msg)
            self.statusBar.showMessage(msg)
            return

        visibleColumns = [
            'Network', 'Station', 'Location', 'Channel', 'Longitude', 'Latitude',
        ]
        numericColumns = [
            'Longitude', 'Latitude', 'Elevation', 'Depth', 'Azimuth', 'Dip',
            'Scale', 'ScaleFreq', 'ScaleUnits', 'SampleRate',
        ]

        self.fillTable(self.stationsTable, stationsDF, visibleColumns, numericColumns)

        # Add items to the map -------------------------------------------------

        self.seismap.add_stations(stationsDF)

        if self.stationOptionsWidget.locationRangeRadioButton.isChecked():
            n = self.stationOptionsWidget.locationRangeNorthDoubleSpinBox.value()
            e = self.stationOptionsWidget.locationRangeEastDoubleSpinBox.value()
            s = self.stationOptionsWidget.locationRangeSouthDoubleSpinBox.value()
            w = self.stationOptionsWidget.locationRangeWestDoubleSpinBox.value()
            self.seismap.add_stations_box(n, e, s, w)
        elif self.stationOptionsWidget.locationDistanceFromPointRadioButton.isChecked():
            n = self.stationOptionsWidget.distanceFromPointNorthDoubleSpinBox.value()
            e = self.stationOptionsWidget.distanceFromPointEastDoubleSpinBox.value()
            minradius = self.stationOptionsWidget.distanceFromPointMinRadiusDoubleSpinBox.value()
            maxradius = self.stationOptionsWidget.distanceFromPointMaxRadiusDoubleSpinBox.value()
            self.seismap.add_stations_toroid(n, e, minradius, maxradius)

        LOGGER.info('Loaded %d channels', stationsDF.shape[0])
        self.statusBar.showMessage('Loaded %d channels' % (stationsDF.shape[0]))

    @QtCore.pyqtSlot()
    def getWaveforms(self):
        self.pyweed.open_waveforms_dialog()

    def onEventSelectionChanged(self):
        """
        Handle a click anywhere in the table.
        """
        # Get selected rows
        rows = []
        for idx in self.eventsTable.selectionModel().selectedRows():
            rows.append(idx.row())

        LOGGER.debug('%d events currently selected', len(rows))

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

        # Update the events_handler with the latest selection information
        self.pyweed.set_selected_event_ids(eventIDs)

        self.seismap.add_events_highlighting(lons, lats)

        self.manageGetWaveformsButton()

    def onStationSelectionChanged(self):
        # Get selected rows
        rows = []
        for idx in self.stationsTable.selectionModel().selectedRows():
            rows.append(idx.row())

        LOGGER.debug('%d stations currently selected', len(rows))

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

        # Update the stations_handler with the latest selection information
        self.pyweed.set_selected_station_ids(SNCLs)

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

    def savePreferences(self):
        prefs = self.pyweed.preferences

        prefs.MainWindow.width = self.width()
        prefs.MainWindow.height = self.height()
        prefs.MainWindow.eventOptionsFloat = bool_to_str(self.eventOptionsDockWidget.isFloating())
        prefs.MainWindow.stationOptionsFloat = bool_to_str(self.stationOptionsDockWidget.isFloating())
