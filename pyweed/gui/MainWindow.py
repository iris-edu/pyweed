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
from preferences import Preferences
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

    def __init__(self, manager):

        self.manager = manager
        self.pyweed = manager.pyweed
        self.preferences = manager.pyweed.preferences

        super(self.__class__, self).__init__()
        self.setupUi(self)

        # Set MainWindow properties
        self.setWindowTitle('%s version %s' % (self.preferences.App.name, self.preferences.App.version))

        # Get the Figure object from the map_canvas
        LOGGER.info('Setting up main map...')
        self.map_figure = self.mapCanvas.fig
        self.map_axes = self.map_figure.add_axes([0.01, 0.01, .98, .98])
        self.map_axes.clear()
        self.seismap = Seismap(projection=self.preferences.Map.projection, ax=self.map_axes) # 'cyl' or 'robin' or 'mill'
        self.map_figure.canvas.draw()

        self.eventOptionsWidget = EventOptionsWidget(self)
        self.eventOptionsDockWidget.setWidget(self.eventOptionsWidget)
        self.toggleEventOptions.toggled.connect(self.eventOptionsDockWidget.setVisible)
        self.eventOptionsDockWidget.visibilityChanged.connect(self.toggleEventOptions.setChecked)

        self.stationOptionsWidget = StationOptionsWidget(self)
        self.stationOptionsDockWidget.setWidget(self.stationOptionsWidget)
        self.toggleStationOptions.toggled.connect(self.stationOptionsDockWidget.setVisible)
        self.stationOptionsDockWidget.visibilityChanged.connect(self.toggleStationOptions.setChecked)

        # Connect signals associated with table clicks
        # see:  http://zetcode.com/gui/pyqt4/eventsandsignals/
        # see:  https://wiki.python.org/moin/PyQt/Sending%20Python%20values%20with%20signals%20and%20slots
        QtCore.QObject.connect(self.eventsTable, QtCore.SIGNAL('cellClicked(int, int)'), self.eventsTableClicked)
        QtCore.QObject.connect(self.stationsTable, QtCore.SIGNAL('cellClicked(int, int)'), self.stationsTableClicked)

        self.getWaveformsButton.setEnabled(False)

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

        parameters = self.eventOptionsWidget.getOptions()
        self.manager.getEvents(parameters)

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
        parameters = self.stationOptionsWidget.getOptions()
        # TODO:  handle errors when querying stations
        self.stationsHandler.load_data(parameters=parameters)

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
        self.eventsHandler.set_selected_ids(eventIDs)

        self.seismap.add_events_highlighting(lons, lats)

        self.manageGetWaveformsButton()


    @QtCore.pyqtSlot(int, int)
    def stationsTableClicked(self, row, col):
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

