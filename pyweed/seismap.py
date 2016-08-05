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
                 projection='moll', resolution='c',
                 area_thresh=1000.0, rsphere=6370997.0,
                 ellps=None, lat_ts=None,
                 lat_1=None, lat_2=None,
                 lat_0=None, lon_0=180,
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
        self.events_lines = []
        self.stations_lines = []
        
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
        ###self.etopo(scale=0.1)
        self.drawcoastlines()
        self.drawcountries()
        self.drawmeridians(np.arange(0, 360, 30))
        self.drawparallels(np.arange(-90, 90, 30))
        
        
    def add_events(self, dataframe):
        """
        Displays event locations

        See http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
        """
        
        lats = dataframe.Latitude.tolist()
        lons = dataframe.Longitude.tolist()
        
        x, y = self(lons, lats)
        
        # See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        # Clean out existing events
        try:
            self.events_lines.pop(0).remove()
            self.events_lines = []
        except IndexError:
            pass

        self.events_lines = self.plot(x, y, linestyle='None', marker='o', markersize=6, color='y', markeredgecolor='y')
        

    def add_stations(self, dataframe):
        """
        Displays station locations

        See http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
        """
        
        lats = dataframe.Latitude.tolist()
        lons = dataframe.Longitude.tolist()
                
        x, y = self(lons, lats)
        
        # See http://stackoverflow.com/questions/4981815/how-to-remove-lines-in-a-matplotlib-plot
        # Clean out existing stations
        try:
            self.stations_lines.pop(0).remove()
            self.stations_lines = []
        except IndexError:
            pass

        self.stations_lines = self.plot(x, y, linestyle='None', marker='v', markersize=6, color='r', markeredgecolor='r')


        
                        



