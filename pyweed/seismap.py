"""
Seismap is a subclass of Basemap, specialized for handling seismic data.

Ideas and code borrowed from:
 * https://github.com/matplotlib/basemap/blob/master/examples/allskymap.py

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

import numpy as np

from mpl_toolkits.basemap import Basemap
from pyweed_utils import get_bounding_circle, get_preferred_origin


class MapMarkers(object):
    """
    Configures and tracks the markers (for items on the map and bounding boxes/toroids) on the map
    This handles a single type, so there is one instance of this class for events and
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


class Seismap(Basemap):
    """
    Seismap is a subclass of Basemap, specialized for handling seismic data.
    """
    def __init__(self, **kwargs):
        super(Seismap, self).__init__(**kwargs)

        # Trackers for the markers
        self.event_markers = EventMarkers()
        self.station_markers = StationMarkers()

        # Basic map features
        self.add_base()

    def add_base(self):
        # NOTE:  http://matplotlib.org/basemap/api/basemap_api.html
        # NOTE:  https://gist.github.com/dannguyen/eb1c4e70565d8cb82d63
        self.bluemarble(scale=0.1, alpha=0.42)
        self.drawcoastlines(color='#555566', linewidth=1)
        self.drawmeridians(np.arange(0, 360, 30))
        self.drawparallels(np.arange(-90, 90, 30))

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
            x, y = self(lons, lats)
            markers.markers.extend(
                self.plot(
                    x, y, linestyle='None', marker=markers.marker_type, markersize=markers.marker_size,
                    color=markers.color, markeredgecolor=markers.color
                )
            )

        self.ax.figure.canvas.draw()

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
            x, y = self(lons, lats)
            markers.highlights.extend(
                self.plot(
                    x, y, linestyle='None', marker=markers.marker_type, markersize=markers.highlight_marker_size,
                    color=markers.highlight_color
                )
            )

        self.ax.figure.canvas.draw()

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
            (x, y) = self(lons, lats)
            markers.box_markers.extend(
                self.plot(
                    x, y,
                    color=markers.color,
                    linewidth=markers.bounds_linewidth,
                    linestyle=markers.bounds_linestyle,
                    alpha=markers.bounds_alpha
                ))

        self.ax.figure.canvas.draw()

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
                    (x, y) = self(lons, lats)
                    markers.toroid_markers.extend(
                        self.plot(
                            x, y,
                            color=markers.color,
                            linewidth=markers.bounds_linewidth,
                            linestyle=markers.bounds_linestyle,
                            alpha=markers.bounds_alpha
                        ))

        self.ax.figure.canvas.draw()

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
            self.ax.figure.canvas.draw()

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
            self.ax.figure.canvas.draw()

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
            self.ax.figure.canvas.draw()

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
