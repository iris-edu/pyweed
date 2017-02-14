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
from gui.TableItems import TableItems

LOGGER = logging.getLogger(__name__)


def make_exclusive(widget1, widget2):
    """
    Make two widgets exclusive, so that if one is toggled the other is disabled and vice versa
    """
    widget1.toggled.connect(
        lambda b: widget2.setEnabled(not b))
    widget2.toggled.connect(
        lambda b: widget1.setEnabled(not b))
    widget2.setEnabled(not widget1.isChecked())
    widget1.setEnabled(not widget2.isChecked())


class MainWindow(QtGui.QMainWindow, MainWindow.Ui_MainWindow):

    eventTableItems = None
    stationTableItems = None

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

        # Connect the interdependent event/station options settings
        make_exclusive(
            self.eventOptionsWidget.timeFromStationsRadioButton,
            self.stationOptionsWidget.timeFromEventsRadioButton)
        make_exclusive(
            self.eventOptionsWidget.locationFromStationsRadioButton,
            self.stationOptionsWidget.locationFromEventsRadioButton)

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
        # See http://matplotlib.org/users/event_handling.html
        def on_press(event):
            (lon, lat) = self.seismap(event.xdata, event.ydata, inverse=True)
            if lat is None or lon is None:
                LOGGER.debug('Mouse click outside of map')
            else:
                LOGGER.debug('you pressed %d x %d', lat, lon)
                self.seismap.add_events_toroid(lat, lon, 0, 20)
        cid = self.mapCanvas.mpl_connect('button_press_event', on_press)

        # Size and placement according to preferences
        self.resize(
            safe_int(prefs.MainWindow.width, 1000),
            safe_int(prefs.MainWindow.height, 800))
        self.eventOptionsDockWidget.setFloating(safe_bool(prefs.MainWindow.eventOptionsFloat, False))
        self.stationOptionsDockWidget.setFloating(safe_bool(prefs.MainWindow.stationOptionsFloat, False))

    def updateOptions(self):
        """
        Update the event and station options from the GUI
        """
        self.pyweed.set_event_options(self.eventOptionsWidget.getOptions())
        self.pyweed.set_station_options(self.stationOptionsWidget.getOptions())

    @QtCore.pyqtSlot()
    def getEvents(self):
        """
        Get events dataframe from IRIS.
        """
        self.getEventsButton.setEnabled(False)
        LOGGER.info('Loading events...')
        self.statusBar.showMessage('Loading events...')

        self.updateOptions()
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

        if not self.eventTableItems:
            visibleColumns = [
                'Time', 'Magnitude', 'Longitude', 'Latitude', 'Depth/km',
                'MagType', 'EventLocationName',
            ]
            numericColumns = [
                'Magnitude', 'Longitude', 'Latitude', 'Depth/km',
            ]
            self.eventTableItems = TableItems(self.eventsTable, visibleColumns, numericColumns)

        self.eventTableItems.build(eventsDF)

        # Add items to the map -------------------------------------------------

        self.seismap.add_events(eventsDF)

        event_options = self.pyweed.event_options
        if event_options.location_choice == event_options.LOCATION_BOX:
            self.seismap.add_events_box(
                event_options.maxlatitude,
                event_options.maxlongitude,
                event_options.minlatitude,
                event_options.minlongitude
            )
        elif event_options.location_choice == event_options.LOCATION_POINT:
            self.seismap.add_events_toroid(
                event_options.latitude,
                event_options.longitude,
                event_options.minradius,
                event_options.maxradius
            )
        else:
            self.seismap.clear_events_bounds()

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

        self.updateOptions()
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

        if not self.stationTableItems:
            visibleColumns = [
                'Network', 'Station', 'Location', 'Channel', 'Longitude', 'Latitude',
            ]
            numericColumns = [
                'Longitude', 'Latitude', 'Elevation', 'Depth', 'Azimuth', 'Dip',
                'Scale', 'ScaleFreq', 'ScaleUnits', 'SampleRate',
            ]
            self.stationTableItems = TableItems(self.stationsTable, visibleColumns, numericColumns)

        self.stationTableItems.build(stationsDF)

        # Add items to the map -------------------------------------------------

        self.seismap.add_stations(stationsDF)

        station_options = self.pyweed.station_options
        if station_options.location_choice == station_options.LOCATION_BOX:
            self.seismap.add_stations_box(
                station_options.maxlatitude,
                station_options.maxlongitude,
                station_options.minlatitude,
                station_options.minlongitude
            )
        elif station_options.location_choice == station_options.LOCATION_POINT:
            self.seismap.add_stations_toroid(
                station_options.latitude,
                station_options.longitude,
                station_options.minradius,
                station_options.maxradius
            )
        else:
            self.seismap.clear_stations_bounds()

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
