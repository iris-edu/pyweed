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

class WaveformsHandler(object):
    """
    Container for waveforms metadata.
    
    The contents of self.currentDF is determined by the user selections
    in the main GUI events and SNCL tables. There will be a separate
    entry in self.currentDF for each event-SNCL combination regardless
    of any filtering that is applied in the WaveformsDialog to reduce
    the size of the visible table. 
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
        
        # Current state
        self.currentDF = None
                
        
    def create_waveformsDF(self, eventsDF, stationsDF):
        """
        Create a dataframe of event-SNCL combinations.
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
        waveformsDF['WaveformImagePath'] = ""
        
        # Look to see if any have already been downloaded
        for i in range(waveformsDF.shape[0]):
            filename = waveformsDF.SNCL.iloc[i] + '_' + waveformsDF.Time.iloc[i] + ".png"
            imagePath = os.path.join(self.downloadDir, filename)
            if os.path.exists(imagePath):
                waveformsDF.WaveformImagePath.iloc[i] = imagePath
        
        # Add a Keep column for checkboxes
        waveformsDF['Keep'] = ''
        
        # Reorganize columns
        waveformsDF = waveformsDF[self.get_column_names()]
        
        # Save a copy internally
        self.currentDF = waveformsDF
    
        return(self.currentDF)
    
    def get_WaveformImagePath(self, waveformID):
        waveformIDs = self.currentDF.WaveformID.tolist()
        index = waveformIDs.index(waveformID)
        imagePath = self.currentDF.WaveformImagePath.iloc[index]
        return(imagePath)
    
    def set_WaveformImagePath(self, waveformID, imagePath):
        waveformIDs = self.currentDF.WaveformID.tolist()
        index = waveformIDs.index(waveformID)
        self.currentDF.WaveformImagePath.iloc[index] = imagePath
        return
    
    def get_column_names(self):
        columnNames = ['Keep', 'SNCL', 'Distance', 'Magnitude', 'Depth', 'Time', 'Waveform', 'Event_Lon', 'Event_Lat', 'EventID', 'Network', 'Station', 'Station_Lon', 'Station_Lat', 'WaveformID', 'WaveformStationID', 'WaveformImagePath']
        return(columnNames)
    
    def get_column_hidden(self):
        is_hidden =    [False,  False,  False,      False,       False,   False,  False,      True,        True,        True,      True,      True,      True,          True,          True,         True,                True]
        return(is_hidden)
    
    def get_column_numeric(self):
        is_numeric =   [False,  False,  True,       True,        True,    False,  False,      True,        True,        False,     False,     False,     True,          True,          False,        False,               False]
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
