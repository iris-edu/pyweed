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
from pyweed_utils import iter_channels, get_preferred_origin, get_preferred_magnitude, get_distance
from seismap import Seismap
from gui.EventOptionsWidget import EventOptionsWidget
from gui.StationOptionsWidget import StationOptionsWidget
from gui.TableItems import TableItems
from event_options import EventOptions

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
        'MagType',
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
                self.numericWidget(magnitude.mag),
                self.numericWidget(origin.longitude),
                self.numericWidget(origin.latitude),
                self.numericWidget(origin.depth / 1000),  # we wish to report in km
                self.stringWidget(magnitude.magnitude_type),
                self.stringWidget(event_description),
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
    ]

    def rows(self, data):
        """
        Turn the data into rows (an iterable of lists) of QTableWidgetItems
        """
        sncls = set()
        for (network, station, channel) in iter_channels(data):
            sncl = '.'.join((network.code, station.code, channel.location_code, channel.code))
            if sncl in sncls:
                LOGGER.info("Found duplicate SNCL: %s", sncl)
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

        # Options widgets, mostly common code
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

        # Main window buttons
        self.getWaveformsButton.setEnabled(False)
        self.getEventsButton.clicked.connect(self.getEvents)
        self.getStationsButton.pressed.connect(self.getStations)
        self.getWaveformsButton.pressed.connect(self.getWaveforms)

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

        # Map drawing mode
        self.drawMode = None
        # Indicates that we are actually drawing (ie. mouse button is down)
        self.drawing = False
        # If drawing, the start and end points
        self.drawPoints = []
        # Handler functions for mouse down/move/up, these are created when drawing is activated
        self.drawHandlers = []
        # Map of buttons to the relevant draw modes
        self.drawButtons = {
            'events.box': self.eventOptionsWidget.drawLocationRangeToolButton,
            'events.toroid': self.eventOptionsWidget.drawDistanceFromPointToolButton,
            'stations.box': self.stationOptionsWidget.drawLocationRangeToolButton,
            'stations.toroid': self.stationOptionsWidget.drawDistanceFromPointToolButton,
        }

        # Generate a handler to toggle a given drawing mode
        def drawModeFn(mode):
            return lambda checked: self.toggleDrawMode(mode, checked)
        # Register draw mode toggle handlers
        for mode, button in self.drawButtons.iteritems():
            button.clicked.connect(drawModeFn(mode))

    def setDrawMode(self, mode):
        """
        Initialize the given drawing mode
        """
        LOGGER.info("Drawing %s", mode)
        self.clearDrawMode()
        self.drawMode = mode
        # See http://matplotlib.org/users/event_handling.html
        self.drawHandlers = [
            self.mapCanvas.mpl_connect('button_press_event', self.onMapMouseClick),
            self.mapCanvas.mpl_connect('button_release_event', self.onMapMouseRelease),
            self.mapCanvas.mpl_connect('motion_notify_event', self.onMapMouseMove),
        ]

    def clearDrawMode(self):
        """
        Clear the drawing mode
        """
        # Ensure the button is unchecked
        if self.drawMode:
            self.drawButtons[self.drawMode].setChecked(False)
        self.drawing = False
        self.drawMode = None
        for handler in self.drawHandlers:
            self.mapCanvas.mpl_disconnect(handler)
        self.drawHandlers = []

    def toggleDrawMode(self, mode, checked):
        """
        Event handler when a draw mode button is clicked
        """
        if not checked:
            self.clearDrawMode()
        else:
            self.setDrawMode(mode)

    def drawPointsToBox(self):
        """
        Convert self.drawPoints to a tuple of (n, e, s, w)
        """
        (lat1, lon1) = self.drawPoints[0]
        (lat2, lon2) = self.drawPoints[1]
        return (
            max(lat1, lat2),
            max(lon1, lon2),
            min(lat1, lat2),
            min(lon1, lon2)
        )

    def drawPointsToToroid(self):
        """
        Convert self.drawPoints to a tuple of (lat, lon, radius)
        """
        (lat1, lon1) = self.drawPoints[0]
        (lat2, lon2) = self.drawPoints[1]
        radius = get_distance(lat1, lon1, lat2, lon2)
        return (lat1, lon1, radius)

    def onMapMouseClick(self, event):
        """
        Handle a mouse click on the map, this should only be called if drawMode is active
        """
        if self.drawMode:
            (lat, lon) = self.seismap.get_latlon(event.xdata, event.ydata)
            if lat is not None and lon is not None:
                self.drawing = True
                self.drawPoints = [[lat, lon], [lat, lon]]

    def onMapMouseRelease(self, event):
        """
        Handle a mouse up event, this should only be called while the user is drawing on the map
        """
        if self.drawing:
            options = {}
            # Build options values based on box or toroid
            if 'box' in self.drawMode:
                (n, e, s, w) = self.drawPointsToBox()
                options = {
                    'location_choice': EventOptions.LOCATION_BOX,  # StationOptions must use the same value here!
                    'maxlatitude': n,
                    'maxlongitude': e,
                    'minlatitude': s,
                    'minlongitude': w,
                }
            elif 'toroid' in self.drawMode:
                (lat, lon, dist) = self.drawPointsToToroid()
                options = {
                    'location_choice': EventOptions.LOCATION_POINT,  # StationOptions must use the same value here!
                    'latitude': lat,
                    'longitude': lon,
                    'maxradius': dist
                }
            # Set event or station options
            if 'events' in self.drawMode:
                self.pyweed.set_event_options(options)
            elif 'stations' in self.drawMode:
                self.pyweed.set_station_options(options)
            # Exit drawing mode
            self.clearDrawMode()

    def onMapMouseMove(self, event):
        """
        Handle a mouse move event, this should only be called while the user is drawing on the map
        """
        if self.drawing:
            (lat, lon) = self.seismap.get_latlon(event.xdata, event.ydata)
            if lat is not None and lon is not None:
                self.drawPoints[1] = [lat, lon]
                LOGGER.debug("Draw points: %s" % self.drawPoints)
                self.updateDrawBounds()

    def updateDrawBounds(self):
        """
        Update the displayed bounding box/toroid as the user is drawing it
        """
        # Build options values based on box or toroid
        if 'box' in self.drawMode:
            (n, e, s, w) = self.drawPointsToBox()
            if 'events' in self.drawMode:
                self.seismap.add_events_box(n, e, s, w)
            elif 'stations' in self.drawMode:
                self.seismap.add_stations_box(n, e, s, w)
        elif 'toroid' in self.drawMode:
            (lat, lon, maxradius) = self.drawPointsToToroid()
            if 'events' in self.drawMode:
                self.seismap.add_events_toroid(lat, lon, 0, maxradius)
            elif 'stations' in self.drawMode:
                self.seismap.add_stations_toroid(lat, lon, 0, maxradius)

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
        self.statusBar.showMessage('Loading events...')

        self.updateOptions()
        self.pyweed.fetch_events()

    def onEventsLoaded(self, events):
        """
        Handler triggered when the EventsHandler finishes loading events
        """
        self.getEventsButton.setEnabled(True)

        if isinstance(events, Exception):
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

        numEvents = len(events)
        status = 'Loaded %d events' % numEvents
        LOGGER.info(status)
        self.statusBar.showMessage(status)

    def getStations(self):
        """
        Trigger the channel metadata retrieval from web services
        """
        self.getStationsButton.setEnabled(False)
        LOGGER.info('Loading channels...')
        self.statusBar.showMessage('Loading channels...')

        self.updateOptions()
        self.pyweed.fetch_stations()

    def onStationsLoaded(self, stations):
        """
        Handler triggered when the StationsHandler finishes loading stations
        """

        self.getStationsButton.setEnabled(True)

        if isinstance(stations, Exception):
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

        numChannels = sum(1 for _ in iter_channels(stations))
        status = 'Loaded %d channels' % numChannels
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

        LOGGER.debug('%d events currently selected', len(ids))

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

        LOGGER.debug('%d stations currently selected', len(sncls))

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
