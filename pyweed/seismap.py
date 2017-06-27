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

import numpy as np

from mpl_toolkits.basemap import Basemap
from pyweed.pyweed_utils import get_bounding_circle, get_preferred_origin, get_distance
from logging import getLogger
from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSignal

LOGGER = getLogger(__name__)


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
    )

    # Signals emitted when starting/ending a draw operation
    drawStart = pyqtSignal(object)
    drawEnd = pyqtSignal(object)

    # Cursors for pan and draw modes
    pan_cursor = QtCore.Qt.PointingHandCursor
    draw_cursor = QtCore.Qt.CrossCursor

    def __init__(self, canvas):
        super(Seismap, self).__init__()
        self.canvas = canvas
        self.map_figure = canvas.fig
        self.map_axes = self.map_figure.add_axes([0.01, 0.01, .98, .98])

        # Trackers for the markers
        self.event_markers = EventMarkers()
        self.station_markers = StationMarkers()

        # Basic map features
        self.init_basemap()

        self.init_drawing()

    def init_basemap(self):
        # NOTE:  http://matplotlib.org/basemap/api/basemap_api.html
        # NOTE:  https://gist.github.com/dannguyen/eb1c4e70565d8cb82d63
        self.map_axes.clear()

        basemap_kwargs = {}
        basemap_kwargs.update(self.DEFAULT_BASEMAP_KWARGS)
        basemap_kwargs.update(
            ax=self.map_axes
        )
        self.basemap = Basemap(**basemap_kwargs)

        self.basemap.bluemarble(scale=0.1, alpha=0.42)
        self.basemap.drawcoastlines(color='#555566', linewidth=1)
        self.basemap.drawmeridians(np.arange(0, 360, 30))
        self.basemap.drawparallels(np.arange(-90, 90, 30))

        self.canvas.draw_idle()

    def get_latlon(self, x, y):
        """
        Translate a canvas x/y coordinate to lat/lon
        """
        (lon, lat) = self.basemap(x, y, inverse=True)
        return (lat, lon)

    def add_markers(self, markers, points):
        """
        Display marker locations

        @param markers: either self.event_markers or self.station_markers
        @param points: a list of (lat, lon) values
        """

        self.clear_markers(markers, redraw=False)
        self.clear_highlights(markers, redraw=False)

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

    def add_highlights(self, markers, points):
        """
        Highlight selected items

        @param markers: either self.event_markers or self.station_markers
        @param points: a list of (lat, lon) values
        """

        self.clear_highlights(markers, redraw=False)

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

    def add_marker_box(self, markers, n, e, s, w):
        """
        Display a bounding box
        """

        self.clear_bounding_markers(markers, redraw=False)

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

    def add_marker_toroid(self, markers, lat, lon, minradius, maxradius):
        """
        Display a toroidal bounding area
        """

        self.clear_bounding_markers(markers, redraw=False)

        for r in (minradius, maxradius):
            if r > 0:
                paths = self.wrap_path(get_bounding_circle(lat, lon, r))
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

    def clear_markers(self, markers, redraw=True):
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

    def clear_highlights(self, markers, redraw=True):
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

    def clear_bounding_markers(self, markers, redraw=True):
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

    def add_events(self, catalog):
        """
        Display event locations
        """
        points = [
            (o.latitude, o.longitude)
            for o in
            [get_preferred_origin(e) for e in catalog]
            if o
        ]
        self.add_markers(self.event_markers, points)

    def add_events_highlighting(self, points):
        """
        Highlights selected events
        """
        self.add_highlights(self.event_markers, points)

    def add_events_box(self, n, e, s, w):
        """
        Display event box
        """
        self.add_marker_box(self.event_markers, n, e, s, w)

    def add_events_toroid(self, lat, lon, minradius, maxradius):
        """
        Display event locations
        """
        self.add_marker_toroid(self.event_markers, lat, lon, minradius, maxradius)

    def clear_events_bounds(self):
        """
        Clear event bounding markers
        """
        self.clear_bounding_markers(self.event_markers)

    def add_stations(self, inventory):
        """
        Display station locations
        """
        points = [
            (s.latitude, s.longitude)
            for n in inventory.networks
            for s in n.stations
        ]
        self.add_markers(self.station_markers, points)

    def add_stations_highlighting(self, points):
        """
        Highlight selected stations
        """
        self.add_highlights(self.station_markers, points)

    def add_stations_box(self, n, e, s, w):
        """
        Display station box outline
        """
        self.add_marker_box(self.station_markers, n, e, s, w)

    def add_stations_toroid(self, lat, lon, minradius, maxradius):
        """
        Display station locations
        """
        self.add_marker_toroid(self.station_markers, lat, lon, minradius, maxradius)

    def clear_stations_bounds(self):
        """
        Clear station bounding markers
        """
        self.clear_bounding_markers(self.station_markers)

    def wrap_path(self, path):
        """
        Split a path of (lat, lon) values into a list of paths none of which crosses the map boundary

        This is a workaround for https://github.com/matplotlib/basemap/issues/214
        """
        last_point = None
        current_subpath = []
        subpaths = [current_subpath]
        for point in path:
            # Detect the path wrapping around the map boundary
            midpoints = self.wrap_point(last_point, point)
            if midpoints:
                # The first midpoint goes at the end of the previous subpath
                current_subpath.append(midpoints[0])
                current_subpath = []
                subpaths.append(current_subpath)
                # The second midpoint goes at the start of the new subpath
                current_subpath.append(midpoints[1])
            current_subpath.append(point)
            last_point = point
        # If the path crosses the map boundary, we will (usually?) have 3 subpaths, and the
        # first and last subpaths are actually contiguous so join them together
        if len(subpaths) > 2:
            subpaths[-1].extend(subpaths[0])
            subpaths = subpaths[1:]
        return subpaths

    def wrap_point(self, p1, p2):
        """
        Given two lat/lon pairs representing a line segment to be plotted, if the segment crosses
        the map boundary this returns two points (one at each edge of the map) where the segment
        crosses the boundary, or None if the segment doesn't cross the boundary.

        For example:
        wrap_point([20, 170], [10, -170])
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

    def zoom_in(self):
        """
        Zoom into the map
        """
        # Zoom in by 2, by trimming 1/4 from each edge
        xlim = self.map_axes.get_xlim()
        xdelta = (xlim[1] - xlim[0]) / 4
        ylim = self.map_axes.get_ylim()
        ydelta = (ylim[1] - ylim[0]) / 4

        self.map_axes.set_xlim(xlim[0] + xdelta, xlim[1] - xdelta)
        self.map_axes.set_ylim(ylim[0] + ydelta, ylim[1] - ydelta)
        self.canvas.draw_idle()

    def zoom_out(self):
        """
        Zoom out on the map
        """
        # Zoom out by 2, by adding 1/2 to each edge
        xlim = self.map_axes.get_xlim()
        xdelta = (xlim[1] - xlim[0]) / 2
        ylim = self.map_axes.get_ylim()
        ydelta = (ylim[1] - ylim[0]) / 2

        self.map_axes.set_xlim(xlim[0] - xdelta, xlim[1] + xdelta)
        self.map_axes.set_ylim(ylim[0] - ydelta, ylim[1] + ydelta)
        self.canvas.draw_idle()

    def zoom_reset(self):
        """
        Zoom all the way out of the map
        """
        self.map_axes.set_xlim(-180, 180)
        self.map_axes.set_ylim(-90, 90)
        self.canvas.draw_idle()

    def init_drawing(self):
        # Map drawing mode
        self.draw_mode = None
        # Indicates that we are actually drawing (ie. mouse button is down)
        self.drawing = False
        # If drawing, the start and end points
        self.draw_points = []
        # Handler functions for mouse down/move/up, these are created when drawing is activated
        # See http://matplotlib.org/users/event_handling.html
        self.draw_handlers = {
            'click': self.canvas.mpl_connect('button_press_event', self.on_mouse_down)
        }
        self.update_cursor()

    def set_draw_mode(self, mode):
        """
        Initialize the given drawing mode
        """
        LOGGER.info("Drawing mode set to %s", mode)
        self.drawing = False
        self.draw_mode = mode
        self.drawStart.emit(DrawEvent(mode))
        self.update_cursor()

    def clear_draw_mode(self):
        """
        Clear any active drawing mode
        """
        if self.draw_mode:
            points = None
            if self.drawing:
                # If we finished drawing bounds, pass back the parameters indicated
                if self.draw_points:
                    if 'box' in self.draw_mode:
                        points = self.draw_points_to_box()
                    elif 'toroid' in self.draw_mode:
                        points = self.draw_points_to_toroid()
            self.drawEnd.emit(DrawEvent(self.draw_mode, points))
        self.drawing = False
        self.draw_mode = None
        self.update_cursor()

    def toggle_draw_mode(self, mode, toggle):
        """
        Event handler when a draw mode button is clicked
        """
        if toggle:
            self.set_draw_mode(mode)
        else:
            self.clear_draw_mode()

    def update_cursor(self):
        """
        Set the cursor on the canvas according to the current mode
        """
        if self.draw_mode:
            self.canvas.setCursor(self.draw_cursor)
        else:
            self.canvas.setCursor(self.pan_cursor)

    def draw_points_to_box(self):
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

    def draw_points_to_toroid(self):
        """
        Convert self.draw_points to a tuple of (lat, lon, radius)
        """
        (lat1, lon1) = self.draw_points[0]
        (lat2, lon2) = self.draw_points[1]
        radius = get_distance(lat1, lon1, lat2, lon2)
        return (lat1, lon1, radius)

    def on_mouse_down(self, event):
        """
        Handle a mouse click on the map
        """
        if self.draw_mode:
            # Start a drawing operation
            (lat, lon) = self.get_latlon(event.xdata, event.ydata)
            if lat is not None and lon is not None:
                self.drawing = True
                self.draw_points = [[lat, lon], [lat, lon]]
        else:
            # If there's no draw operation, pan the map
            if event.inaxes == self.map_axes:
                LOGGER.debug("Starting pan")
                self.drawing = True
                self.map_axes.start_pan(event.x, event.y, event.button)
        # If we've started a drawing operation, connect listeners for activity
        if self.drawing:
            self.draw_handlers['release'] = self.canvas.mpl_connect('button_release_event', self.on_mouse_up)
            self.draw_handlers['move'] = self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

    def on_mouse_up(self, event):
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
            self.map_axes.end_pan()

        # Exit drawing mode
        self.clear_draw_mode()

    def on_mouse_move(self, event):
        """
        Handle a mouse move event, this should only be called while the user is drawing on the map
        """
        if self.drawing:
            if self.draw_mode:
                (lat, lon) = self.get_latlon(event.xdata, event.ydata)
                if lat is not None and lon is not None:
                    self.draw_points[1] = [lat, lon]
                    LOGGER.debug("Draw points: %s" % self.draw_points)
                    self.update_draw_bounds()
            else:
                # If we aren't drawing anything, pan the map
                self.map_axes.drag_pan(event.button, event.key, event.x, event.y)
                self.canvas.draw_idle()

    def update_draw_bounds(self):
        """
        Update the displayed bounding box/toroid as the user is drawing it
        """
        # Build options values based on box or toroid
        if 'box' in self.draw_mode:
            (n, e, s, w) = self.draw_points_to_box()
            if 'events' in self.draw_mode:
                self.add_events_box(n, e, s, w)
            elif 'stations' in self.draw_mode:
                self.add_stations_box(n, e, s, w)
        elif 'toroid' in self.draw_mode:
            (lat, lon, maxradius) = self.draw_points_to_toroid()
            if 'events' in self.draw_mode:
                self.add_events_toroid(lat, lon, 0, maxradius)
            elif 'stations' in self.draw_mode:
                self.add_stations_toroid(lat, lon, 0, maxradius)
