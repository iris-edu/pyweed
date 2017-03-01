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
from pyweed_utils import get_preferred_origin


class MapMarkers(object):
    """
    Handles the markers (for items on the map and bounding boxes/toroids) of a particular type
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

    def __init__(self, llcrnrlon=None, llcrnrlat=None,
                 urcrnrlon=None, urcrnrlat=None,
                 llcrnrx=None, llcrnry=None,
                 urcrnrx=None, urcrnry=None,
                 width=None, height=None,
                 projection='cyl', resolution='c',
                 area_thresh=1000.0, rsphere=6370997.0,
                 ellps=None, lat_ts=None,
                 lat_1=None, lat_2=None,
                 lat_0=None, lon_0=0,
                 lon_1=None, lon_2=None,
                 o_lon_p=None, o_lat_p=None,
                 k_0=None,
                 no_rot=False,
                 suppress_ticks=True,
                 satellite_height=35786000,
                 boundinglat=None,
                 fix_aspect=True,
                 anchor='C',
                 celestial=False,
                 round=False,
                 epsg=None,
                 ax=None):

        self.event_markers = EventMarkers()
        self.station_markers = StationMarkers()

        # Use Basemap's init, enforcing the values of many parameters that
        # aren't used or whose Basemap defaults would not be altered for all-sky
        # celestial maps.

        Basemap.__init__(self, llcrnrlon=None, llcrnrlat=None,
                         urcrnrlon=None, urcrnrlat=None,
                         llcrnrx=None, llcrnry=None,
                         urcrnrx=None, urcrnry=None,
                         width=None, height=None,
                         projection=projection, resolution=resolution,
                         area_thresh=area_thresh, rsphere=6370997.0,
                         ellps=None, lat_ts=None,
                         lat_1=lat_1, lat_2=lat_2,
                         lat_0=lat_0, lon_0=lon_0,
                         lon_1=lon_1, lon_2=lon_2,
                         o_lon_p=None, o_lat_p=None,
                         k_0=None,
                         no_rot=False,
                         suppress_ticks=True,
                         satellite_height=35786000,
                         boundinglat=None,
                         fix_aspect=True,
                         anchor='C',
                         celestial=False,
                         round=False,
                         epsg=None,
                         ax=ax)

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

        See http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
        """

        self.clear_markers(markers, redraw=False)
        self.clear_highlights(markers, redraw=False)

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
        Highlights selected items
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

        # Get locations to plot
        lon_top = np.linspace(w,e)
        lon_right = np.linspace(e,e)
        lon_bottom = np.linspace(e,w)
        lon_left = np.linspace(w,w)
        lons = np.concatenate((lon_top, lon_right, lon_bottom, lon_left))

        lat_top = np.linspace(n,n)
        lat_right = np.linspace(n,s)
        lat_bottom = np.linspace(s,s)
        lat_left = np.linspace(s,n)
        lats = np.concatenate((lat_top, lat_right, lat_bottom, lat_left))

        # Plot in projection coordinates
        x, y = self(lons, lats)
        markers.box_markers.extend(
            self.plot(x, y, lineStyle='solid', color=markers.color, alpha=0.7, linewidth=2)
        )

        self.ax.figure.canvas.draw()

    def add_marker_toroid(self, markers, n, e, minradius, maxradius):
        """
        Display a toroidal bounding area
        """

        self.clear_bounding_markers(markers, redraw=False)

        # Get locations to plot
        lons1, lats1 = self._geocircle(e, n, minradius)
        lons2, lats2 = self._geocircle(e, n, maxradius)

        # Plot in projection coordinates
        x1, y1 = self(lons1, lats1)
        markers.toroid_markers.extend(
            self.plot(x1, y1, lineStyle='solid', color=markers.color, alpha=0.7, linewidth=2)
        )
        x2, y2 = self(lons2, lats2)
        markers.toroid_markers.extend(
            self.plot(x2, y2, lineStyle='solid', color=markers.color, alpha=0.7, linewidth=2)
        )

        self.ax.figure.canvas.draw()

    def clear_markers(self, markers, redraw=True):
        """
        Remove existing marker elements
        See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        """
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

    def add_events_toroid(self, n, e, minradius, maxradius):
        """
        Display event locations
        """
        self.add_marker_toroid(self.event_markers, n, e, minradius, maxradius)

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

    def add_stations_toroid(self, n, e, minradius, maxradius):
        """
        Display station locations
        """
        self.add_marker_toroid(self.station_markers, n, e, minradius, maxradius)

    def clear_stations_bounds(self):
        """
        Clear station bounding markers
        """
        self.clear_bounding_markers(self.station_markers)

    def _geocircle(self, lon, lat, radius, n=50):
        """Calculate lons and lats associated with a circle."""

        # Calculate circle
        step = 2.0*np.pi / n
        lons = lon + radius*np.cos(np.arange(0,2*np.pi,step))
        lons = lons.tolist()
        lons.append(lon + radius)
        lats = lat + radius*np.sin(np.arange(0,2*np.pi,step))
        lats = lats.tolist()
        lats.append(lat)

        # TODO:  _geocircle: Handle branch cut at boundaries

        coords = (lons,lats)

        return(coords)




