#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Testing mapping functionalitiy."""


from __future__ import (absolute_import, division, print_function)

# Basic modules
import os
import sys
import argparse
import datetime

# pyweed modules
from events import Events
from stations import Stations

import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap



__version__ = "0.0.1"

def main():

    # Parse arguments ----------------------------------------------------------
    
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('--starttime', action='store', required=True,
                        help='starttime in ISO 8601 format')
    parser.add_argument('--endtime', action='store', required=False,
                        help='endtime in ISO 8601 format')
    parser.add_argument('-M', '--minmag', required=True,
                        help='minimum magnitue')

    args = parser.parse_args(sys.argv[1:])
    
    
    # Test event query -----------------
    
    parameters = {}        
    parameters['starttime'] = args.starttime
    parameters['endtime'] = args.endtime
    parameters['minmag'] = args.minmag
    parameters['maxmag'] = '10'
        
    eventsHandler = Events()
    eventsDF = eventsHandler.query(parameters=parameters)
    ###print(eventsDF)
    
    # Test station query ---------------
    
    parameters = {}
    parameters['starttime'] = args.starttime
    parameters['endtime'] = args.endtime
    parameters['network'] = 'IU'
    parameters['station'] = '*'
    parameters['location'] = '00'
    parameters['channel'] = '?HZ'
    
    stationsHandler = Stations()
    stationsDF = stationsHandler.query(parameters=parameters)
    ###print(stationsDF)
    
    # Plot map
    fig = plt.figure(figsize=(16,8))
    map = Basemap(projection='robin', resolution = 'l', area_thresh = 1000.0,
                 lat_0=0, lon_0=-130)
    
    # NOTE:  http://matplotlib.org/basemap/api/basemap_api.html
    map.etopo(scale=0.1)
    map.drawcoastlines()
    map.drawcountries()
    map.drawmeridians(np.arange(0, 360, 30))
    map.drawparallels(np.arange(-90, 90, 30))
    
    event_lats = eventsDF.Latitude.tolist()
    event_lons = eventsDF.Longitude.tolist()
    
    station_lats = stationsDF.Latitude.tolist()
    station_lons = stationsDF.Longitude.tolist()
    
    ex,ey = map(event_lons, event_lats)
    sx,sy = map(station_lons, station_lats)
    
    # NOTE:  http://matplotlib.org/api/markers_api.html#module-matplotlib.markers
    map.plot(ex, ey, linestyle='None', marker='o', markersize=6, color='y', markeredgecolor='y')
    map.plot(sx, sy, linestyle='None', marker='v', markersize=6, color='r', markeredgecolor='r')
     
    # A box
    box_lats = [30,50,50,30,30]
    box_lons = [-160,-160,-120,-120,-160]
    bx,by = map(box_lons, box_lats)
    map.plot(bx, by, lineStyle='solid', color='lightblue', alpha=0.5, linewidth=4)
    
    # A circle
    c_lats = -40 + 20*np.sin(np.arange(0,2*np.pi,.1))
    c_lats = c_lats.tolist()
    c_lats.append(-40)
    c_lons = -140 + 20*np.cos(np.arange(0,2*np.pi,.1))
    c_lons = c_lons.tolist()
    c_lons.append(-140+20)
    cx,cy = map(c_lons, c_lats)
    map.plot(cx, cy, lineStyle='solid', color='lightcoral', alpha=0.7, linewidth=4)
    
    
    plt.show()
    
    debug_point = 1
    

    
    
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

# try:
#     from mpl_toolkits.basemap import Basemap
#     have_basemap = True
# except ImportError:
#     have_basemap = False
# 
# 
# def plotmap():
#     # create figure
#     fig = plt.figure(figsize=(8,8))
#     # set up orthographic map projection with
#     # perspective of satellite looking down at 50N, 100W.
#     # use low resolution coastlines.
#     map = Basemap(projection='ortho',lat_0=50,lon_0=-100,resolution='l')
#     # lat/lon coordinates of five cities.
#     lats=[40.02,32.73,38.55,48.25,17.29]
#     lons=[-105.16,-117.16,-77.00,-114.21,-88.10]
#     cities=['Boulder, CO','San Diego, CA',
#             'Washington, DC','Whitefish, MT','Belize City, Belize']
#     # compute the native map projection coordinates for cities.
#     xc,yc = map(lons,lats)
#     # make up some data on a regular lat/lon grid.
#     nlats = 73; nlons = 145; delta = 2.*np.pi/(nlons-1)
#     lats = (0.5*np.pi-delta*np.indices((nlats,nlons))[0,:,:])
#     lons = (delta*np.indices((nlats,nlons))[1,:,:])
#     wave = 0.75*(np.sin(2.*lats)**8*np.cos(4.*lons))
#     mean = 0.5*np.cos(2.*lats)*((np.sin(2.*lats))**2 + 2.)
#     # compute native map projection coordinates of lat/lon grid.
#     # (convert lons and lats to degrees first)
#     x, y = map(lons*180./np.pi, lats*180./np.pi)
#     # draw map boundary
#     map.drawmapboundary(color="0.9")
#     # draw graticule (latitude and longitude grid lines)
#     map.drawmeridians(np.arange(0,360,30),color="0.9")
#     map.drawparallels(np.arange(-90,90,30),color="0.9")
#     # plot filled circles at the locations of the cities.
#     map.plot(xc,yc,'wo')
#     # plot the names of five cities.
#     for name,xpt,ypt in zip(cities,xc,yc):
#         plt.text(xpt+100000,ypt+100000,name,fontsize=9,color='w')
#     # contour data over the map.
#     cs = map.contour(x,y,wave+mean,15,linewidths=1.5)
#     # draw blue marble image in background.
#     # (downsample the image by 50% for speed)
#     map.bluemarble(scale=0.5)
# 
# def plotempty():
#     # create figure
#     fig = plt.figure(figsize=(8,8))
#     fig.text(0.5, 0.5, "Sorry, could not import Basemap",
#                                 horizontalalignment='center')
# 
# if have_basemap:
#     plotmap()
# else:
#     plotempty()
# plt.show()

