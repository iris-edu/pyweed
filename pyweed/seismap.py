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
        
        # Lists of plotted elements that can be removed
        self.events = []
        self.events_box = []
        self.events_toroid = []
        self.events_highlighting = []
        self.stations = []
        self.stations_box = []
        self.stations_toroid = []
        self.stations_highlighting = []
        
        # Consistent use of colors
        self.event_color = '#FFFF00'              # bright yellow
        self.event_highlight_color = '#00FF00'    # bright green
        self.event_marker = 'o'                   # circle
        self.event_markersize = 6
        self.station_color = '#FF0000'            # bright red
        self.station_highlight_color = '#0000FF'  # bright blue
        self.station_marker = 'v'                 # inverted triangle
        self.station_markersize = 6
        
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
        
        
    def add_events(self, dataframe):
        """
        Display event locations

        See http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
        """
        
        # Remove existing 'lines' elements
        # See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        try:
            while self.events:
                self.events.pop(0).remove()
            self.events = []
        except IndexError:
            pass

        # Get locations to plot
        lons = dataframe.Longitude.tolist()
        lats = dataframe.Latitude.tolist()
        
        # Plot in projection coordinates
        x, y = self(lons, lats)
        self.events.extend( self.plot(x, y, linestyle='None', marker=self.event_marker, markersize=self.event_markersize, color=self.event_color, markeredgecolor=self.event_color) )
        
        # NOTE:  Cannot use self.plots(lons, lats, latlon=True, ...) because we run into this error:
        # NOTE:    http://stackoverflow.com/questions/31839047/valueerror-in-python-basemap
        # NOTE:    https://github.com/matplotlib/basemap/issues/214
        ###lons = self.shiftdata(lons)        
        ###self.events = self.plot(lons, lats, latlon=True, linestyle='None', marker=self.event_marker, markersize=self.event_markersize, color=self.event_color, markeredgecolor=self.event_color)
                
        self.ax.figure.canvas.draw()
        
        
    def add_events_highlighting(self, lons, lats):
        """
        Highlights selected events
        """
        
        # Remove existing 'lines' elements
        try:
            while self.events_highlighting:
                self.events_highlighting.pop(0).remove()
            self.events_highlighting = []
        except IndexError:
            pass

        # Plot in projection coordinates
        x, y = self(lons, lats)
        self.events_highlighting.extend( self.plot(x, y, linestyle='None', marker=self.event_marker, markersize=self.event_markersize*1.5,
                                                   color=self.event_color, markeredgecolor=self.event_highlight_color, alpha=1.0) )
                        
        self.ax.figure.canvas.draw()
        
        
    def add_events_box(self, n, e, s, w):
        """
        Display event box

        See http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
        """

        # Remove existing 'lines' elements
        # See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        try:
            while self.events_box:
                self.events_box.pop(0).remove()
            self.events_box = []
            while self.events_toroid:
                self.events_toroid.pop(0).remove()
            self.events_toroid = []
        except IndexError:
            pass

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
        self.events_box.extend( self.plot(x, y, lineStyle='solid', color=self.event_color, alpha=0.7, linewidth=2) )
        
        self.ax.figure.canvas.draw()
        
        
    def add_events_toroid(self, n, e, minradius, maxradius):
        """
        Display event locations

        See http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
        """

        # Remove existing 'lines' elements
        # See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        try:
            while self.events_box:
                self.events_box.pop(0).remove()
            self.events_box = []
            while self.events_toroid:
                self.events_toroid.pop(0).remove()
            self.events_toroid = []
        except IndexError:
            pass
        
        # Get locations to plot
        lons1,lats1 = self._geocircle(e, n, minradius)
        lons2,lats2 = self._geocircle(e, n, maxradius)
        
        # Plot in projection coordinates
        x1, y1 = self(lons1, lats1)
        self.events_toroid.extend( self.plot(x1, y1, lineStyle='solid', color=self.event_color, alpha=0.7, linewidth=2) )
        x2, y2 = self(lons2, lats2)
        self.events_toroid.extend( self.plot(x2, y2, lineStyle='solid', color=self.event_color, alpha=0.7, linewidth=2) )

        self.ax.figure.canvas.draw()


    def add_stations(self, dataframe):
        """
        Display station locations

        See http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
        """
        
        lons = dataframe.Longitude.tolist()
        lats = dataframe.Latitude.tolist()
                
        x, y = self(lons, lats)
        
        # Remove existing 'lines' elements
        # See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        try:
            while self.stations:
                self.stations.pop(0).remove()
            self.stations = []
        except IndexError:
            pass

        self.stations.extend( self.plot(x, y, linestyle='None', marker=self.station_marker, markersize=self.station_markersize, color=self.station_color, markeredgecolor=self.station_color) )

        self.ax.figure.canvas.draw()


    def add_stations_highlighting(self, lons, lats):
        """
        Highlight selected stations
        """
        
        # Remove existing 'lines' elements
        try:
            while self.stations_highlighting:
                self.stations_highlighting.pop(0).remove()
            self.stations_highlighting = []
        except IndexError:
            pass

        # Plot in projection coordinates
        x, y = self(lons, lats)
        self.stations_highlighting.extend( self.plot(x, y, linestyle='None', marker=self.station_marker, markersize=self.station_markersize*1.5,
                                                   color=self.station_color, markeredgecolor=self.station_highlight_color, alpha=1.0) )
                        
        self.ax.figure.canvas.draw()
        
        
    def add_stations_box(self, n, e, s, w):
        """
        Display station box outline
        """
        
        # Remove existing 'lines' elements
        # See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        try:
            while self.stations_box:
                self.stations_box.pop(0).remove()
            self.stations_box = []
            while self.stations_toroid:
                self.stations_toroid.pop(0).remove()
            self.stations_toroid = []
        except IndexError:
            pass

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
        self.stations_box.extend( self.plot(x, y, lineStyle='solid', color=self.station_color, alpha=0.7, linewidth=2) )
        
        self.ax.figure.canvas.draw()
        
        
    def add_stations_toroid(self, n, e, minradius, maxradius):
        """
        Display station locations

        See http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
        """
        
        # Remove existing 'lines' element
        # See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        try:
            while self.stations_box:
                self.stations_box.pop(0).remove()
            self.stations_box = []
            while self.stations_toroid:
                self.stations_toroid.pop(0).remove()
            self.stations_toroid = []
        except IndexError:
            pass

        # Get locations to plot
        lons1,lats1 = self._geocircle(e, n, minradius)
        lons2,lats2 = self._geocircle(e, n, maxradius)
        
        # Plot in projection coordinates
        x1, y1 = self(lons1, lats1)
        self.stations_toroid.extend( self.plot(x1, y1, lineStyle='solid', color=self.station_color, alpha=0.7, linewidth=2) )
        x2, y2 = self(lons2, lats2)
        self.stations_toroid.extend( self.plot(x2, y2, lineStyle='solid', color=self.station_color, alpha=0.7, linewidth=2) )

        self.ax.figure.canvas.draw()


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




