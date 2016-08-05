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
        self.events_center_point = []
        self.stations = []
        self.stations_box = []
        self.stations_center_point = []
        
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
        #self.bluemarble(scale=0.1, alpha=0.42)
        self.drawcoastlines(color='#555566', linewidth=1)
        self.drawmeridians(np.arange(0, 360, 30))
        self.drawparallels(np.arange(-90, 90, 30))
        
        
    def add_events(self, dataframe):
        """
        Displays event locations

        See http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
        """
        
        lons = dataframe.Longitude.tolist()
        lats = dataframe.Latitude.tolist()
        
        x, y = self(lons, lats)
        
        # Remove existing 'lines' element
        # See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        try:
            self.events.pop(0).remove()
            self.events = []
        except IndexError:
            pass

        self.events = self.plot(x, y, linestyle='None', marker='o', markersize=6, color='y', markeredgecolor='y')
        # NOTE:  Cannot use self.plots(lons, lats, latlon=True, ...) because we run into this error:
        # NOTE:    http://stackoverflow.com/questions/31839047/valueerror-in-python-basemap
        # NOTE:    https://github.com/matplotlib/basemap/issues/214
        ###lons = self.shiftdata(lons)        
        ###self.events = self.plot(lons, lats, latlon=True, linestyle='None', marker='o', markersize=6, color='y', markeredgecolor='y')
        
        
    def add_events_box(self, n, e, s, w):
        """
        Displays event box

        See http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
        """
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

        x, y = self(lons, lats)
        
        # Remove existing 'lines' element
        # See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        try:
            self.events_box.pop(0).remove()
            self.events_box = []
        except IndexError:
            pass

        self.events_box = self.plot(x, y, lineStyle='solid', color='y', alpha=0.7, linewidth=2)
        
        
    def add_events_center_point(self, n, e):
        """
        Displays event locations

        See http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
        """
        
        lons = [n]
        lats = [e]
        
        x, y = self(lons, lats)
        
        # Remove existing 'lines' element
        # See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        try:
            self.events_center_point.pop(0).remove()
            self.events_center_point = []
        except IndexError:
            pass

        self.events_center_point = self.plot(x, y, linestyle='None', marker='*', markersize=12, color='r', markeredgecolor='b')


    def add_stations(self, dataframe):
        """
        Displays station locations

        See http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
        """
        
        lons = dataframe.Longitude.tolist()
        lats = dataframe.Latitude.tolist()
                
        x, y = self(lons, lats)
        
        # Remove existing 'lines' element
        # See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        try:
            self.stations.pop(0).remove()
            self.stations = []
        except IndexError:
            pass

        self.stations = self.plot(x, y, linestyle='None', marker='v', markersize=6, color='r', markeredgecolor='r')


    def add_stations_box(self, n, e, s, w):
        """
        Displays event box

        See http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
        """
        
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

        x, y = self(lons, lats)
                
        # Remove existing 'lines' element
        # See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        try:
            self.stations_box.pop(0).remove()
            self.stations_box = []
        except IndexError:
            pass

        self.stations_box = self.plot(x, y, lineStyle='solid', color='r', alpha=0.7, linewidth=2)
        
        
    def add_stations_center_point(self, n, e):
        """
        Displays event locations

        See http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
        """
        
        lons = [n]
        lats = [e]
        
        x, y = self(lons, lats)
        
        # Remove existing 'lines' element
        # See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        try:
            self.stations_center_point.pop(0).remove()
            self.stations_center_point = []
        except IndexError:
            pass

        self.stations_center_point = self.plot(x, y, linestyle='None', marker='*', markersize=12, color='r', markeredgecolor='b')


        
                        



