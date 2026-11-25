# -*- coding: utf-8 -*-
"""
Seismap is a subclass of Basemap, specialized for handling seismic data.

Ideas and code borrowed from:
 * https://github.com/matplotlib/basemap/blob/master/examples/allskymap.py

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

import html

import numpy as np

from mpl_toolkits.basemap import Basemap
from pyweed.pyweed_utils import get_bounding_circle, get_preferred_origin, get_distance
from logging import getLogger
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal

LOGGER = getLogger(__name__)

def _event_tooltip(event, origin):
    """
    Rich-text summary of an event for the map tooltip.
    """
    try:
        mag = event.preferred_magnitude() or (event.magnitudes[0] if event.magnitudes else None)
        head = "M ?"
        if mag is not None and mag.mag is not None:
            head = "M %.1f" % mag.mag
            if mag.magnitude_type:
                head += " %s" % mag.magnitude_type
        lines = ["<b>%s</b>" % html.escape(head)]
        if origin.time is not None:
            lines.append(origin.time.strftime("%Y-%m-%d %H:%M:%S"))
        lines.append("lat %.3f, lon %.3f" % (origin.latitude, origin.longitude))
        if origin.depth is not None:
            lines.append("depth %.1f km" % (origin.depth / 1000.0))
        if event.event_descriptions:
            lines.append(html.escape(event.event_descriptions[0].text or ""))
        return "<br>".join(lines)
    except Exception:
        LOGGER.warning("Could not build event tooltip", exc_info=True)
        return "?"


def _station_tooltip(network, station):
    """
    Rich-text summary of a station for the map tooltip.
    """
    try:
        lines = ["<b>%s.%s</b>" % (html.escape(network.code), html.escape(station.code))]
        lines.append("lat %.3f, lon %.3f" % (station.latitude, station.longitude))
        if station.elevation is not None:
            lines.append("elev %.0f m" % station.elevation)
        site = getattr(station, "site", None)
        if site is not None and getattr(site, "name", None):
            lines.append(html.escape(site.name))
        n = len(station.channels or [])
        if n:
            lines.append("%d channel(s)" % n)
        return "<br>".join(lines)
    except Exception:
        LOGGER.warning("Could not build station tooltip", exc_info=True)
        return "?"

class MapMarkers(object):
    """
    Configures and tracks the markers (for items on the map and bounding boxes/toroids) on the map.
    This handles a single type, so there is one instance of this class for events and one for stations.
    """
    color = '#FFFFFF'
    highlight_color = '#FFFF00'
    marker_type = 'o'
    marker_size = 6
    highlight_marker_size = 12
    bounds_linewidth = 2
    bounds_linestyle = 'dashed'
    bounds_alpha = 0.5
    markers = None
    highlights = None
    box_markers = None
    toroid_markers = None

    def __init__(self):
        self.markers = []
        self.highlights = []
        self.box_markers = []
        self.toroid_markers = []


class EventMarkers(MapMarkers):
    color = '#FFFF00'
    highlight_color = '#FFA500'
    marker_type = 'o'  # circle


class StationMarkers(MapMarkers):
    color = '#FF0000'
    highlight_color = '#CD0000'
    marker_type = 'v'  # inverted triangle


class DrawEvent(object):
    """
    Event emitted when drawing on the map starts/stops.
    """
    def __init__(self, mode, points=None):
        #: The drawing mode being started/stopped
        self.mode = mode
        #: When stopping, we may pass back points representing the drawn area
        self.points = points


class Seismap(QtCore.QObject):
    """
    Map display using Basemap
    """
    # Default kwargs
    DEFAULT_BASEMAP_KWARGS = dict(
        projection='cyl',  # We only support cylindrical projection for now
        resolution='l',  # c/l/i/h/f
    )

    # Signals emitted when starting/ending a draw operation
    drawStart = pyqtSignal(object)
    drawEnd = pyqtSignal(object)
    #: Emitted when a marker is clicked: (kind, key).
    #: kind is 'event' or 'station'; key is a catalog index or (network, station) codes.
    markerClicked = pyqtSignal(str, object)

    # Cursors for pan and draw modes
    panCursor = QtCore.Qt.PointingHandCursor
    drawCursor = QtCore.Qt.CrossCursor
    # Tolerance for clicking / hovering markers
    pickRadius = 8    # points
    hoverRadius = 10  # pixels

    # Markers
    eventMarkers = None
    stationMarkers = None

    def __init__(self, canvas):
        super(Seismap, self).__init__()
        self.canvas = canvas
        self.mapFigure = canvas.fig
        self.mapAxes = self.mapFigure.add_axes([0.01, 0.01, .98, .98])

        # Trackers for the markers
        self.eventMarkers = EventMarkers()
        self.stationMarkers = StationMarkers()

        # Basic map features
        self.initBasemap()

        self.initDrawing()

    def initBasemap(self):
        # NOTE:  http://matplotlib.org/basemap/api/basemap_api.html
        # NOTE:  https://gist.github.com/dannguyen/eb1c4e70565d8cb82d63
        self.mapAxes.clear()

        basemap_kwargs = {}
        basemap_kwargs.update(self.DEFAULT_BASEMAP_KWARGS)
        basemap_kwargs.update(
            ax=self.mapAxes
        )
        self.basemap = Basemap(**basemap_kwargs)

        self.basemap.bluemarble(scale=0.25, alpha=0.42)
        self.basemap.drawcoastlines(color='#555566', linewidth=1)
        self.basemap.drawmeridians(np.arange(0, 360, 30))
        self.basemap.drawparallels(np.arange(-90, 90, 30))

        self.canvas.draw_idle()

    def getLatLon(self, x, y):
        """
        Translate a canvas x/y coordinate to lat/lon
        """
        (lon, lat) = self.basemap(x, y, inverse=True)
        return (lat, lon)

    def addMarkers(self, markers, points):
        """
        Display marker locations

        @param markers: either self.eventMarkers or self.stationMarkers
        @param points: a list of (lat, lon) values
        """

        self.clearMarkers(markers, redraw=False)
        self.clearHighlights(markers, redraw=False)

        # See http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
        if len(points):
            (lats, lons) = zip(*points)
            # Plot in projection coordinates
            x, y = self.basemap(lons, lats)
            markers.markers.extend(
                self.basemap.plot(
                    x, y, linestyle='None', marker=markers.marker_type, markersize=markers.marker_size,
                    color=markers.color, markeredgecolor=markers.color
                )
            )

        self.canvas.draw_idle()

    def addHighlights(self, markers, points):
        """
        Highlight selected items

        @param markers: either self.eventMarkers or self.stationMarkers
        @param points: a list of (lat, lon) values
        """

        self.clearHighlights(markers, redraw=False)

        if len(points):
            (lats, lons) = zip(*points)
            # Plot in projection coordinates
            # TODO:  Use self.scatter() with zorder=99 to keep highlighting on top?
            x, y = self.basemap(lons, lats)
            markers.highlights.extend(
                self.basemap.plot(
                    x, y, linestyle='None', marker=markers.marker_type, markersize=markers.highlight_marker_size,
                    color=markers.highlight_color
                )
            )

        self.canvas.draw_idle()

    def addMarkerBox(self, markers, n, e, s, w):
        """
        Display a bounding box
        """
        # Check for box wrapping around the map edge
        if e < w:
            # Need to create two paths
            paths = [
                [[s, 180], [s, w], [n, w], [n, 180]],
                [[s, -180], [s, e], [n, e], [n, -180]]
            ]
        else:
            paths = [
                [[n, w], [n, e], [s, e], [s, w], [n, w]]
            ]

        for path in paths:
            (lats, lons) = zip(*path)
            (x, y) = self.basemap(lons, lats)
            markers.box_markers.extend(
                self.basemap.plot(
                    x, y,
                    color=markers.color,
                    linewidth=markers.bounds_linewidth,
                    linestyle=markers.bounds_linestyle,
                    alpha=markers.bounds_alpha
                ))

        self.canvas.draw_idle()

    def addMarkerToroid(self, markers, lat, lon, minradius, maxradius):
        """
        Display a toroidal bounding area
        """
        for r in (minradius, maxradius):
            if r > 0:
                paths = self.wrapPath(get_bounding_circle(lat, lon, r))
                for path in paths:
                    (lats, lons) = zip(*path)
                    (x, y) = self.basemap(lons, lats)
                    markers.toroid_markers.extend(
                        self.basemap.plot(
                            x, y,
                            color=markers.color,
                            linewidth=markers.bounds_linewidth,
                            linestyle=markers.bounds_linestyle,
                            alpha=markers.bounds_alpha
                        ))

        self.canvas.draw_idle()

    def clearMarkers(self, markers, redraw=True):
        """
        Remove existing marker elements
        """
        # See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        try:
            while markers.markers:
                markers.markers.pop(0).remove()
            markers.markers = []
        except IndexError:
            pass
        if redraw:
            self.canvas.draw_idle()

    def clearHighlights(self, markers, redraw=True):
        """
        Remove existing highlights
        """
        try:
            while markers.highlights:
                markers.highlights.pop(0).remove()
            markers.highlights = []
        except IndexError:
            pass
        if redraw:
            self.canvas.draw_idle()

    def clearBoundingMarkers(self, markers, redraw=True):
        """
        Remove existing bounding box/toroid markers
        """
        try:
            while markers.box_markers:
                markers.box_markers.pop(0).remove()
            markers.box_markers = []
            while markers.toroid_markers:
                markers.toroid_markers.pop(0).remove()
            markers.toroid_markers = []
        except IndexError:
            pass
        if redraw:
            self.canvas.draw_idle()

    def addEvents(self, catalog):
        """
        Display event locations
        """
        points, keys, tooltips = [], [], []
        for i, event in enumerate(catalog):
            origin = get_preferred_origin(event)
            if not origin:
                continue
            points.append((origin.latitude, origin.longitude))
            keys.append(i)
            tooltips.append(_event_tooltip(event, origin))
        self.addMarkers(self.eventMarkers, points)
        self.tagMarkers(self.eventMarkers, 'event', keys, tooltips)

    def addEventsHighlighting(self, points):
        """
        Highlights selected events
        """
        self.addHighlights(self.eventMarkers, points)

    def addEventsBox(self, n, e, s, w):
        """
        Display event box
        """
        self.addMarkerBox(self.eventMarkers, n, e, s, w)

    def addEventsToroid(self, lat, lon, minradius, maxradius):
        """
        Display event locations
        """
        self.addMarkerToroid(self.eventMarkers, lat, lon, minradius, maxradius)

    def clearEventsBounds(self):
        """
        Clear event bounding markers
        """
        self.clearBoundingMarkers(self.eventMarkers)

    def addStations(self, inventory):
        """
        Display station locations
        """
        points, keys, tooltips = [], [], []
        for network in inventory.networks:
            for station in network.stations:
                points.append((station.latitude, station.longitude))
                keys.append((network.code, station.code))
                tooltips.append(_station_tooltip(network, station))
        self.addMarkers(self.stationMarkers, points)
        self.tagMarkers(self.stationMarkers, 'station', keys, tooltips)

    def addStationsHighlighting(self, points):
        """
        Highlight selected stations
        """
        self.addHighlights(self.stationMarkers, points)

    def addStationsBox(self, n, e, s, w):
        """
        Display station box outline
        """
        self.addMarkerBox(self.stationMarkers, n, e, s, w)

    def addStationsToroid(self, lat, lon, minradius, maxradius):
        """
        Display station locations
        """
        self.addMarkerToroid(self.stationMarkers, lat, lon, minradius, maxradius)

    def clearStationsBounds(self):
        """
        Clear station bounding markers
        """
        self.clearBoundingMarkers(self.stationMarkers)

    def wrapPath(self, path):
        """
        Split a path of (lat, lon) values into a list of paths none of which crosses the map boundary

        This is a workaround for https://github.com/matplotlib/basemap/issues/214
        """
        lastPoint = None
        currentSubpath = []
        subpaths = [currentSubpath]
        for point in path:
            # Detect the path wrapping around the map boundary
            midpoints = self.wrapPoint(lastPoint, point)
            if midpoints:
                # The first midpoint goes at the end of the previous subpath
                currentSubpath.append(midpoints[0])
                currentSubpath = []
                subpaths.append(currentSubpath)
                # The second midpoint goes at the start of the new subpath
                currentSubpath.append(midpoints[1])
            currentSubpath.append(point)
            lastPoint = point
        # If the path crosses the map boundary, we will (usually?) have 3 subpaths, and the
        # first and last subpaths are actually contiguous so join them together
        if len(subpaths) > 2:
            subpaths[-1].extend(subpaths[0])
            subpaths = subpaths[1:]
        return subpaths

    def wrapPoint(self, p1, p2):
        """
        Given two lat/lon pairs representing a line segment to be plotted, if the segment crosses
        the map boundary this returns two points (one at each edge of the map) where the segment
        crosses the boundary, or None if the segment doesn't cross the boundary.

        For example:
        wrapPoint([20, 170], [10, -170])
        returns
        [[15, 180], [15, -180]]

        This means that the segment should be split into:
        [20, 170] - [15, 180]
        [15, -180] - [10, -170]
        """
        if p1 and p2:
            dlon = p2[1] - p1[1]
            if abs(dlon) > 180:
                # Interpolate the point where the segment crosses the boundary
                dlat = p2[0] - p1[0]
                if dlon < 0:
                    # Wraps from east to west
                    midlat = p1[0] + (180 - p1[1]) * dlat / (dlon + 360)
                    return [[midlat, 180], [midlat, -180]]
                else:
                    # Wraps from west to east
                    midlat = p1[0] + (-180 - p1[1]) * dlat / (dlon - 360)
                    return [[midlat, -180], [midlat, 180]]
        return None

    def zoomIn(self):
        """
        Zoom into the map
        """
        # Zoom in by 2, by trimming 1/4 from each edge
        xlim = self.mapAxes.get_xlim()
        xdelta = (xlim[1] - xlim[0]) / 4
        ylim = self.mapAxes.get_ylim()
        ydelta = (ylim[1] - ylim[0]) / 4

        self.mapAxes.set_xlim(xlim[0] + xdelta, xlim[1] - xdelta)
        self.mapAxes.set_ylim(ylim[0] + ydelta, ylim[1] - ydelta)
        self.canvas.draw_idle()

    def zoomOut(self):
        """
        Zoom out on the map
        """
        # Zoom out by 2, by adding 1/2 to each edge
        xlim = self.mapAxes.get_xlim()
        xdelta = (xlim[1] - xlim[0]) / 2
        ylim = self.mapAxes.get_ylim()
        ydelta = (ylim[1] - ylim[0]) / 2

        self.mapAxes.set_xlim(xlim[0] - xdelta, xlim[1] + xdelta)
        self.mapAxes.set_ylim(ylim[0] - ydelta, ylim[1] + ydelta)
        self.canvas.draw_idle()

    def zoomReset(self):
        """
        Zoom all the way out of the map
        """
        self.mapAxes.set_xlim(-180, 180)
        self.mapAxes.set_ylim(-90, 90)
        self.canvas.draw_idle()

    def fitCanvas(self, *args):
        canvas_w = self.canvas.width()
        canvas_h = self.canvas.height()
        map_xlim = self.mapAxes.get_xlim()
        map_ylim = self.mapAxes.get_ylim()

        map_w = map_xlim[1] - map_xlim[0]
        map_h = map_ylim[1] - map_ylim[0]
        prop_map_h = ((map_w * canvas_h) / canvas_w)

        adjustment = ((prop_map_h - map_h) / 2)

        self.mapAxes.set_ylim(map_ylim[0] - adjustment, map_ylim[1] + adjustment)
        self.canvas.draw_idle()

    def initDrawing(self):
        # Map drawing mode
        self.draw_mode = None
        # Indicates that we are actually drawing (ie. mouse button is down)
        self.drawing = False
        # If drawing, the start and end points
        self.draw_points = []
        # Handler functions for mouse down/move/up, these are created when drawing is activated
        # See http://matplotlib.org/users/event_handling.html
        self.draw_handlers = {
            'click': self.canvas.mpl_connect('button_press_event', self.onMouseDown),
            'scroll_wheel': self.canvas.mpl_connect('scroll_event', self.onScrollWheel),
            'resize': self.canvas.mpl_connect('resize_event', self.fitCanvas),
        }
        self.hover_marker = None
        self.canvas.mpl_connect('pick_event', self.onMarkerPick)
        self.canvas.mpl_connect('motion_notify_event', self.onMarkerHover)
        self.canvas.mpl_connect('figure_leave_event', self.onFigureLeave)
        self.updateCursor()

    def setDrawMode(self, mode):
        """
        Initialize the given drawing mode
        """
        LOGGER.info("Drawing mode set to %s", mode)
        self.drawing = False
        self.draw_mode = mode
        self.drawStart.emit(DrawEvent(mode))
        self.updateCursor()

    def clearDrawMode(self):
        """
        Clear any active drawing mode
        """
        if self.draw_mode:
            points = None
            if self.drawing:
                # If we finished drawing bounds, pass back the parameters indicated
                if self.draw_points:
                    if 'box' in self.draw_mode:
                        points = self.drawPointsToBox()
                    elif 'toroid' in self.draw_mode:
                        points = self.drawPointsToToroid()
            self.drawEnd.emit(DrawEvent(self.draw_mode, points))
        self.drawing = False
        self.draw_mode = None
        self.updateCursor()

    def toggleDrawMode(self, mode, toggle):
        """
        Event handler when a draw mode button is clicked
        """
        if toggle:
            self.setDrawMode(mode)
        else:
            self.clearDrawMode()

    def updateCursor(self):
        """
        Set the cursor on the canvas according to the current mode
        """
        if self.draw_mode:
            self.canvas.setCursor(self.drawCursor)
        else:
            self.canvas.setCursor(self.panCursor)

    def drawPointsToBox(self):
        """
        Convert self.draw_points to a tuple of (n, e, s, w)
        """
        (lat1, lon1) = self.draw_points[0]
        (lat2, lon2) = self.draw_points[1]
        return (
            max(lat1, lat2),
            max(lon1, lon2),
            min(lat1, lat2),
            min(lon1, lon2)
        )

    def drawPointsToToroid(self):
        """
        Convert self.draw_points to a tuple of (lat, lon, radius)
        """
        (lat1, lon1) = self.draw_points[0]
        (lat2, lon2) = self.draw_points[1]
        radius = get_distance(lat1, lon1, lat2, lon2)
        return (lat1, lon1, radius)

    def onMouseDown(self, event):
        """
        Handle a mouse click on the map
        """
        if self.draw_mode:
            # Start a drawing operation
            (lat, lon) = self.getLatLon(event.xdata, event.ydata)
            if lat is not None and lon is not None:
                self.drawing = True
                self.draw_points = [[lat, lon], [lat, lon]]
        else:
            # If there's no draw operation, pan the map
            if event.inaxes == self.mapAxes:
                LOGGER.debug("Starting pan")
                self.drawing = True
                self.mapAxes.start_pan(event.x, event.y, event.button)
        # If we've started a drawing operation, connect listeners for activity
        if self.drawing:
            self.draw_handlers['release'] = self.canvas.mpl_connect('button_release_event', self.onMouseUp)
            self.draw_handlers['move'] = self.canvas.mpl_connect('motion_notify_event', self.onMouseMove)

    def onMouseUp(self, event):
        """
        Handle a mouse up event, this should only be called while the user is drawing on the map
        """
        # Disconnect the release/move handlers
        for event in ('release', 'move',):
            if event in self.draw_handlers:
                self.canvas.mpl_disconnect(self.draw_handlers[event])
                del self.draw_handlers[event]

        # If there's no draw mode, we are probably panning so turn that off
        if not self.draw_mode:
            self.mapAxes.end_pan()

        # Exit drawing mode
        self.clearDrawMode()

    def onMouseMove(self, event):
        """
        Handle a mouse move event, this should only be called while the user is drawing on the map
        """
        if self.drawing:
            if self.draw_mode:
                (lat, lon) = self.getLatLon(event.xdata, event.ydata)
                if lat is not None and lon is not None:
                    self.draw_points[1] = [lat, lon]
                    LOGGER.debug("Draw points: %s" % self.draw_points)
                    self.updateDrawBounds()
            else:
                # If we aren't drawing anything, pan the map
                self.mapAxes.drag_pan(event.button, event.key, event.x, event.y)
                self.canvas.draw_idle()

    def updateDrawBounds(self):
        """
        Update the displayed bounding box/toroid as the user is drawing it
        """
        # Clear any existing bounds
        if 'events' in self.draw_mode:
            self.clearEventsBounds()
        elif 'stations' in self.draw_mode:
            self.clearStationsBounds()
        # Build options values based on box or toroid
        if 'box' in self.draw_mode:
            (n, e, s, w) = self.drawPointsToBox()
            if 'events' in self.draw_mode:
                self.addEventsBox(n, e, s, w)
            elif 'stations' in self.draw_mode:
                self.addStationsBox(n, e, s, w)
        elif 'toroid' in self.draw_mode:
            (lat, lon, maxradius) = self.drawPointsToToroid()
            if 'events' in self.draw_mode:
                self.addEventsToroid(lat, lon, 0, maxradius)
            elif 'stations' in self.draw_mode:
                self.addStationsToroid(lat, lon, 0, maxradius)

    def onScrollWheel(self, event):
        """
        Zoom on scroll wheel
        """
        if event.step:
            if event.step > 0:
                self.zoomIn()
            else:
                self.zoomOut()

    def tagMarkers(self, markers, kind, keys, tooltips):
        """
        Attach pick/hover metadata to freshly drawn marker artists.
        """
        artists = markers.markers
        if not artists:
            return
        n = len(artists[0].get_xydata())
        if n != len(keys):
            LOGGER.warning("Marker/key count mismatch: %d vs %d", n, len(keys))
            return
        for artist in artists:
            artist.set_picker(self.pickRadius)
            artist._markerKind = kind
            artist._markerKeys = keys
            artist._markerTooltips = tooltips

    def nearestMarker(self, artist, ind, mouse):
        """
        Pick the closest of several candidate points under the cursor.
        """
        if len(ind) == 1 or mouse.xdata is None:
            return int(ind[0])
        xy = artist.get_xydata()
        d = (xy[ind, 0] - mouse.xdata) ** 2 + (xy[ind, 1] - mouse.ydata) ** 2
        return int(ind[int(np.argmin(d))])

    def onMarkerPick(self, event):
        """
        Emit markerClicked when a marker is clicked outside of a draw mode.
        """
        artist = event.artist
        kind = getattr(artist, '_markerKind', None)
        if kind is None or self.draw_mode or self.drawing:
            return
        mouse = event.mouseevent
        if mouse.button != 1:
            return
        ind = getattr(event, 'ind', None)
        if ind is None or len(ind) == 0:
            return
        i = self.nearestMarker(artist, ind, mouse)
        self.markerClicked.emit(kind, artist._markerKeys[i])

    def onMarkerHover(self, mouse):
        """
        Show a tooltip for the marker under the cursor. Uses QToolTip rather than a
        canvas annotation to avoid redrawing the basemap background on every move.
        """
        if (self.draw_mode or self.drawing
                or mouse.inaxes is not self.mapAxes or mouse.x is None):
            self.hideMarkerTooltip()
            return
        best, best_d = None, self.hoverRadius ** 2
        for markers in (self.eventMarkers, self.stationMarkers):
            for artist in markers.markers:
                tooltips = getattr(artist, '_markerTooltips', None)
                if not tooltips:
                    continue
                xy = artist.get_transform().transform(artist.get_xydata())
                d = (xy[:, 0] - mouse.x) ** 2 + (xy[:, 1] - mouse.y) ** 2
                i = int(np.argmin(d))
                if d[i] < best_d:
                    best_d, best = d[i], (id(artist), i, tooltips[i])
        if best is None:
            self.hideMarkerTooltip()
            return
        key = (best[0], best[1])
        if self.hover_marker == key and QtWidgets.QToolTip.isVisible():
            return
        self.hover_marker = key
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos() + QtCore.QPoint(14, 18),
                                    best[2], self.canvas)

    def hideMarkerTooltip(self):
        if self.hover_marker is not None:
            QtWidgets.QToolTip.hideText()
            self.hover_marker = None

    def onFigureLeave(self, event):
        self.hideMarkerTooltip()
