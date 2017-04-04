"""
Main window

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

from PyQt4 import QtGui
from gui.uic import MainWindow
from preferences import safe_int, safe_bool, bool_to_str
import logging
from pyweed_utils import iter_channels, get_preferred_origin, get_preferred_magnitude
from seismap import Seismap
from gui.EventOptionsWidget import EventOptionsWidget
from gui.StationOptionsWidget import StationOptionsWidget
from gui.TableItems import TableItems
from event_options import EventOptions
from PyQt4.QtCore import pyqtSlot

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


class EventTableItems(TableItems):
    """
    Defines the event table contents
    """
    columnNames = [
        'Id',
        'Time',
        'Magnitude',
        'Longitude',
        'Latitude',
        'Depth (km)',
        'Location'
    ]

    def rows(self, data):
        """
        Turn the data into rows (an iterable of lists) of QTableWidgetItems
        """
        for i, event in enumerate(data):
            origin = get_preferred_origin(event)
            if not origin:
                continue
            magnitude = get_preferred_magnitude(event)
            if not magnitude:
                continue
            time = origin.time.strftime("%Y-%m-%d %H:%M:%S")  # use strftime to remove milliseconds
            event_description = "no description"
            if len(event.event_descriptions) > 0:
                event_description = event.event_descriptions[0].text

            yield [
                self.numericWidget(i),
                self.stringWidget(time),
                self.numericWidget(magnitude.mag, "%s %s" % (magnitude.mag, magnitude.magnitude_type)),
                self.numericWidget(origin.longitude),
                self.numericWidget(origin.latitude),
                self.numericWidget(origin.depth / 1000),  # we wish to report in km
                self.stringWidget(event_description.title()),
            ]


class StationTableItems(TableItems):
    """
    Defines the event table contents
    """
    columnNames = [
        'SNCL',
        'Network',
        'Station',
        'Location',
        'Channel',
        'Longitude',
        'Latitude',
        'Description',
    ]

    def rows(self, data):
        """
        Turn the data into rows (an iterable of lists) of QTableWidgetItems
        """
        sncls = set()
        for (network, station, channel) in iter_channels(data):
            sncl = '.'.join((network.code, station.code, channel.location_code, channel.code))
            if sncl in sncls:
                LOGGER.debug("Found duplicate SNCL: %s", sncl)
            else:
                sncls.add(sncl)
                yield [
                    self.stringWidget(sncl),
                    self.stringWidget(network.code),
                    self.stringWidget(station.code),
                    self.stringWidget(channel.location_code),
                    self.stringWidget(channel.code),
                    self.numericWidget(channel.longitude),
                    self.numericWidget(channel.latitude),
                    self.stringWidget(station.site.name),
                ]


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
        self.setWindowTitle('%s version %s' % (self.pyweed.app_name, self.pyweed.app_version))

        # Common code for initializing event/station dock widgets
        def initializeOptionsWidget(widget, options, dockWidget, toggle):
            widget.setOptions(options)
            dockWidget.setWidget(widget)
            toggle.toggled.connect(dockWidget.setVisible)
            dockWidget.visibilityChanged.connect(toggle.setChecked)

        self.eventOptionsWidget = EventOptionsWidget(parent=self)
        initializeOptionsWidget(
            self.eventOptionsWidget,
            self.pyweed.event_options,
            self.eventOptionsDockWidget,
            self.toggleEventOptions
        )
        self.stationOptionsWidget = StationOptionsWidget(parent=self)
        initializeOptionsWidget(
            self.stationOptionsWidget,
            self.pyweed.station_options,
            self.stationOptionsDockWidget,
            self.toggleStationOptions
        )

        # Connect the mutually exclusive event/station options
        make_exclusive(
            self.eventOptionsWidget.timeFromStationsRadioButton,
            self.stationOptionsWidget.timeFromEventsRadioButton)
        make_exclusive(
            self.eventOptionsWidget.locationFromStationsRadioButton,
            self.stationOptionsWidget.locationFromEventsRadioButton)

        # Table selection
        self.eventsTable.itemSelectionChanged.connect(self.onEventSelectionChanged)
        self.stationsTable.itemSelectionChanged.connect(self.onStationSelectionChanged)
        self.clearEventSelectionButton.clicked.connect(self.eventsTable.clearSelection)
        self.clearStationSelectionButton.clicked.connect(self.stationsTable.clearSelection)

        # Main window buttons
        self.getEventsButton.clicked.connect(self.getEvents)
        self.getStationsButton.clicked.connect(self.getStations)
        self.getWaveformsButton.clicked.connect(self.getWaveforms)

        # Map
        self.initializeMap()

        # Size and placement according to preferences
        self.resize(
            safe_int(prefs.MainWindow.width, 1000),
            safe_int(prefs.MainWindow.height, 800))
        self.eventOptionsDockWidget.setFloating(safe_bool(prefs.MainWindow.eventOptionsFloat, False))
        self.stationOptionsDockWidget.setFloating(safe_bool(prefs.MainWindow.stationOptionsFloat, False))

    def initializeMap(self):
        LOGGER.info('Setting up main map...')
        self.seismap = Seismap(self.mapCanvas)

        # Map of buttons to the relevant draw modes
        self.drawButtons = {
            'events.box': self.eventOptionsWidget.drawLocationRangeToolButton,
            'events.toroid': self.eventOptionsWidget.drawDistanceFromPointToolButton,
            'stations.box': self.stationOptionsWidget.drawLocationRangeToolButton,
            'stations.toroid': self.stationOptionsWidget.drawDistanceFromPointToolButton,
        }

        # Generate a handler to toggle a given drawing mode
        def drawModeFn(mode):
            return lambda checked: self.seismap.toggle_draw_mode(mode, checked)
        # Register draw mode toggle handlers
        for mode, button in self.drawButtons.items():
            button.clicked.connect(drawModeFn(mode))

        self.mapZoomInButton.clicked.connect(self.seismap.zoom_in)
        self.mapZoomOutButton.clicked.connect(self.seismap.zoom_out)
        self.mapResetButton.clicked.connect(self.seismap.zoom_reset)

        self.seismap.drawEnd.connect(self.onMapDrawFinished)

    @pyqtSlot(object)
    def onMapDrawFinished(self, event):
        """
        Called when Seismap emits a DrawEvent upon completion
        """
        # If the user finished an operation associated with a button, uncheck it
        button = self.drawButtons.get(event.mode)
        if button:
            button.setChecked(False)

        # For box/toroid bounds drawing, handle the returned geo data
        options = {}
        if event.points:
            if 'box' in event.mode:
                (n, e, s, w) = event.points
                options = {
                    'location_choice': EventOptions.LOCATION_BOX,  # Assumes StationOptions.LOCATION_BOX is the same
                    'maxlatitude': n,
                    'maxlongitude': e,
                    'minlatitude': s,
                    'minlongitude': w,
                }
            elif 'toroid' in event.mode:
                (lat, lon, dist) = event.points
                options = {
                    'location_choice': EventOptions.LOCATION_POINT,  # Assumes StationOptions.LOCATION_POINT is the same
                    'latitude': lat,
                    'longitude': lon,
                    'maxradius': dist
                }
            # Set event or station options
            if 'events' in event.mode:
                self.pyweed.set_event_options(options)
            elif 'stations' in event.mode:
                self.pyweed.set_station_options(options)

    def updateOptions(self):
        """
        Update the event and station options from the GUI
        """
        self.pyweed.set_event_options(self.eventOptionsWidget.getOptions())
        self.pyweed.set_station_options(self.stationOptionsWidget.getOptions())

    def getEvents(self):
        """
        Trigger the event retrieval from web services
        """
        self.getEventsButton.setEnabled(False)
        LOGGER.info('Loading events...')
        self.eventSelectionLabel.setText('Loading events...')

        self.updateOptions()
        self.pyweed.fetch_events()

    def onEventsLoaded(self, events):
        """
        Handler triggered when the EventsHandler finishes loading events
        """
        self.getEventsButton.setEnabled(True)

        if isinstance(events, Exception):
            self.eventSelectionLabel.setText('Error! See log for details')
            msg = "Error loading events: %s" % events
            LOGGER.error(msg)
            self.statusBar.showMessage(msg)
            return

        if not self.eventTableItems:
            self.eventTableItems = EventTableItems(self.eventsTable)
        self.eventTableItems.fill(events)

        # Add items to the map -------------------------------------------------

        self.seismap.add_events(events)

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

        self.onEventSelectionChanged()
        status = 'Finished loading events'
        LOGGER.info(status)
        self.statusBar.showMessage(status)

    def getStations(self):
        """
        Trigger the channel metadata retrieval from web services
        """
        self.getStationsButton.setEnabled(False)
        LOGGER.info('Loading stations...')
        self.stationSelectionLabel.setText('Loading stations...')

        self.updateOptions()
        self.pyweed.fetch_stations()

    def onStationsLoaded(self, stations):
        """
        Handler triggered when the StationsHandler finishes loading stations
        """

        self.getStationsButton.setEnabled(True)

        if isinstance(stations, Exception):
            self.stationSelectionLabel.setText('Error! See log for details')
            msg = "Error loading stations: %s" % stations
            LOGGER.error(msg)
            self.statusBar.showMessage(msg)
            return

        if not self.stationTableItems:
            self.stationTableItems = StationTableItems(self.stationsTable)
        self.stationTableItems.fill(stations)

        # Add items to the map -------------------------------------------------

        self.seismap.add_stations(stations)

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

        self.onStationSelectionChanged()
        status = 'Finished loading stations'
        LOGGER.info(status)
        self.statusBar.showMessage(status)

    def getWaveforms(self):
        self.pyweed.open_waveforms_dialog()

    def onEventSelectionChanged(self):
        """
        Handle a click anywhere in the table.
        """
        # Get selected ids
        ids = []
        for idx in self.eventsTable.selectionModel().selectedRows():
            ids.append(int(self.eventsTable.item(idx.row(), 0).text()))

        numSelected = len(ids)
        numTotal = self.eventsTable.rowCount()
        self.eventSelectionLabel.setText(
            "Selected %d of %d events" % (numSelected, numTotal))

        # Get locations and event IDs
        points = []
        eventIDs = []
        for id in ids:
            event = self.pyweed.events[id]
            origin = get_preferred_origin(event)
            if not origin:
                continue
            points.append((origin.latitude, origin.longitude))
            eventIDs.append(event.resource_id.id)

        # Update the events_handler with the latest selection information
        self.pyweed.set_selected_event_ids(eventIDs)

        self.seismap.add_events_highlighting(points)

        self.manageGetWaveformsButton()

    def onStationSelectionChanged(self):
        # Get selected sncls
        sncls = []
        for idx in self.stationsTable.selectionModel().selectedRows():
            sncls.append(self.stationsTable.item(idx.row(), 0).text())

        numSelected = len(sncls)
        numTotal = self.stationsTable.rowCount()
        self.stationSelectionLabel.setText(
            "Selected %d of %d channels" % (numSelected, numTotal))

        # Get locations
        points = []
        for sncl in sncls:
            try:
                coordinates = self.pyweed.stations.get_coordinates(sncl)
                points.append((coordinates['latitude'], coordinates['longitude']))
            except:
                pass

        # Update the stations_handler with the latest selection information
        self.pyweed.set_selected_station_ids(sncls)

        self.seismap.add_stations_highlighting(points)

        self.manageGetWaveformsButton()

    def manageGetWaveformsButton(self):
        """
        Handle enabled/disabled status of the "Get Waveforms" button
        based on the presence/absence of selected events and stations
        """
        if self.pyweed.selected_event_ids and self.pyweed.selected_station_ids:
            self.getWaveformsButton.setEnabled(True)
        else:
            self.getWaveformsButton.setEnabled(False)

    def savePreferences(self):
        prefs = self.pyweed.preferences

        prefs.MainWindow.width = self.width()
        prefs.MainWindow.height = self.height()
        prefs.MainWindow.eventOptionsFloat = bool_to_str(self.eventOptionsDockWidget.isFloating())
        prefs.MainWindow.stationOptionsFloat = bool_to_str(self.stationOptionsDockWidget.isFloating())
