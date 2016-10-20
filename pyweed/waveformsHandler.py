"""
Container for waveforms.

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

# Basic packages
#import urllib
import os

# Vectors and dataframes
import numpy as np
import pandas as pd

## Multi-threading
#from Queue import Queue
#from threading import Thread
# Multi-processing
import multiprocessing

# ObsPy
from obspy import UTCDateTime
from obspy.taup import TauPyModel
from obspy.clients import fdsn
from obspy.geodetics import locations2degrees

from waveformsDownloader import WaveformsDownloader

class WaveformsHandler(object):
    """
    Container for waveforms.
    """
    def __init__(self, logger, preferences):
        """
        Initialization.
        """
        # Always keep a reference to global logger and preferences
        self.logger = logger
        self.preferences = preferences
        
        # Important preferences
        self.downloadDir = self.preferences.Waveforms.downloadDir
        
        # TODO:  Include these in preferences
        self.plot_width = 600
        self.plot_height = 200
        
        # Current state
        self.currentDF = None
                
        
    def create_waveformsDF(self, eventsDF, stationsDF):
        """
        Create a dataframe of event-SNCL combinations
        """
        
        self.logger.debug('Generating event-station combined dataframe...')
        
        #eventsDF.columns
        #Index([u'Time', u'Magnitude', u'Longitude', u'Latitude', u'Depth/km',
               #u'MagType', u'EventLocationName', u'Author', u'Catalog', u'Contributor',
               #u'ContributorID', u'MagAuthor', u'EventID'],
              #dtype='object')  
        #stationsDF.columns
        #Index([u'Network', u'Station', u'Location', u'Channel', u'Longitude',
               #u'Latitude', u'Elevation', u'Depth', u'Azimuth', u'Dip',
               #u'SensorDescription', u'Scale', u'ScaleFreq', u'ScaleUnits',
               #u'SampleRate', u'StartTime', u'EndTime', u'SNCL'],
              #dtype='object')
              
        # Subset eventsDF for pertinent information
        eventsDF = eventsDF[['Time','Magnitude','Depth/km','Longitude','Latitude','EventID']]
        eventsDF.columns = ['Time','Magnitude','Depth','Event_Lon','Event_Lat','EventID']
        
        #  Subset stationsDF for pertinent information
        stationsDF = stationsDF[['SNCL','Network','Station','Longitude','Latitude']]
        stationsDF.columns = ['SNCL','Network','Station','Station_Lon','Station_Lat']
        
        # For each unique SNCL, add columns of SNCL info to eventsDF
        waveformDFs = []
        for i in range(stationsDF.shape[0]):
            df = eventsDF.copy()
            df['SNCL'] = stationsDF.SNCL.iloc[i]
            df['Network'] = stationsDF.Network.iloc[i]
            df['Station'] = stationsDF.Station.iloc[i]
            df['Station_Lon'] = stationsDF.Station_Lon.iloc[i]
            df['Station_Lat'] = stationsDF.Station_Lat.iloc[i]
            waveformDFs.append(df)
            
        # Now combine all SNCL-specific eventsDFs
        waveformsDF = pd.concat(waveformDFs)
        
        # Add waveformID, and WaveformStationID
        waveformsDF['WaveformID'] = waveformsDF.SNCL + '_' + waveformsDF.EventID
        waveformsDF['WaveformStationID'] = waveformsDF.Network + '.' + waveformsDF.Station + '_' + waveformsDF.EventID
        
        # BEGIN event-station distance -----------------------------------------
        
        self.logger.debug('Calculating %d event-station distances...', len(waveformsDF.WaveformStationID.unique()))
        
        # NOTE:  Save time by only calculating on distance per station rather than per channel
        waveformsDF['Distance'] = np.nan
        i = 0
        old_waveformStationID = waveformsDF.WaveformStationID.iloc[i]
        distance = round(locations2degrees(waveformsDF.Event_Lat.iloc[i], waveformsDF.Event_Lon.iloc[i],
                                           waveformsDF.Station_Lat.iloc[i], waveformsDF.Station_Lon.iloc[i]),
                         ndigits=2)
        
        waveformsDF.Distance.iloc[i] = distance
        
        # Now loop through all waveforms, calculating new distances only when necessary
        for i in range(waveformsDF.shape[0]):
            waveformStationID = waveformsDF.WaveformStationID.iloc[i]
            if (waveformStationID != old_waveformStationID):
                old_waveformStationID = waveformStationID
                distance = round(locations2degrees(waveformsDF.Event_Lat.iloc[i], waveformsDF.Event_Lon.iloc[i],
                                                   waveformsDF.Station_Lat.iloc[i], waveformsDF.Station_Lon.iloc[i]),
                                 ndigits=2)            
            waveformsDF.Distance.iloc[i] = distance
        
        self.logger.debug('Finished claculating distances')
        
        # END event-station distance -------------------------------------------
        
        # Add columns to track downloads and display waveforms
        waveformsDF['Waveform'] = ""
        waveformsDF['Downloaded'] = False
        
        # Look to see if any have already been downloaded
        for i in range(waveformsDF.shape[0]):
            filename = waveformsDF.SNCL.iloc[i] + '_' + waveformsDF.Time.iloc[i] + ".png"
            imagePath = os.path.join(self.downloadDir, filename)
            waveformsDF.Waveform.iloc[i] = imagePath
            waveformsDF.Downloaded.iloc[i] = os.path.exists(imagePath)
        
        # Reorganize columns
        waveformsDF = waveformsDF[self.get_column_names()]
        
        # Save a copy internally
        self.currentDF = waveformsDF
    
        return(waveformsDF)
    
    
    def load_data(self, parameters=None):
        """
        Load a waveform image from cache or download/plot first.
        """
        
        # TOOD:  Sanity check parameters
        
        # TODO:  Should parameters be called "event_sncls" and passed in as a dataframe?
        
        source_time = parameters['time']
        source_depth = parameters['source_depth']
        source_lon = parameters['source_lon']
        source_lat = parameters['source_lat']
        SNCL = parameters['SNCL']
        receiver_lon = parameters['receiver_lon']
        receiver_lat = parameters['receiver_lat']
        
        self.logger.info('Loading data for %s-%s...', source_time, SNCL)

        # Find the matching row in self.currentDF
        # NOTE:  The table may show a resorted subset of the full currentDF so we need
        # NOTE:  to use the parameters to find the matching row of currentDF
        
        # TODO:  Is this the best way to find the matching row?
        SNCL_mask = self.currentDF.SNCL.isin([SNCL])
        event_mask = self.currentDF.Time.isin([source_time])  # TODO:  Use 'EventID' instead of 'Time' to identify events?
        matching_row_mask = SNCL_mask & event_mask
        row_index = matching_row_mask.tolist().index(True)
        
        if self.currentDF.Downloaded.iloc[row_index]:
            imagePath = self.currentDF.Waveform.iloc[row_index]
        
        else:
            imagePath = self.download_data_OLD(parameters)
            self.currentDF.Downloaded.iloc[row_index] = True
        
        return(imagePath)


    def download_data(self, parametersList=None, waveformsQueue=None):
        """
        Start a new process to download a set of waveforms.
        """
        
        # NOTE:  https://pymotw.com/2/multiprocessing/basics.html
        
        waveformsDownloader = WaveformsDownloader(parametersList, waveformsQueue)
        waveformsDownloader.daemon = True
        waveformsDownloader.start()
        # Don't block, don't listen, just let it go. 
    
        self.logger.debug('Started WaveformsDownloader process with pid %s', waveformsDownloader.pid)

        return


    def get_column_names(self):
        columnNames = ['SNCL', 'Distance', 'Magnitude', 'Depth', 'Time', 'Waveform', 'Event_Lon', 'Event_Lat', 'EventID', 'Network', 'Station', 'Station_Lon', 'Station_Lat', 'WaveformID', 'WaveformStationID', 'Downloaded']
        return(columnNames)
    
    def get_column_hidden(self):
        is_hidden =    [False,  False,      False,       False,   False,  False,      True,        True,        True,      True,      True,      True,          True,          True,         True,                True]
        return(is_hidden)
    
    def get_column_numeric(self):
        is_numeric =   [False,  True,       True,        True,    False,  False,      True,        True,        False,     False,     False,     True,          True,          False,        False,               False]
        return(is_numeric)
    
    
    
        
# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
