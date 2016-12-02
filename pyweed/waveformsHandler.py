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
#import multiprocessing

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
        self.dataCenter = "IRIS" # TODO:  dataCenter should be configurable
        
        # Instantiate a client
        self.client = fdsn.Client(self.dataCenter)
        
        # Current state
        self.currentDF = None        
                
        
    def createWaveformsDF(self, eventsDF, stationsDF):
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
        waveformsDF['Keep'] = True
        
        # Reorganize columns
        waveformsDF = waveformsDF[self.getColumnNames()]
        
        # Save a copy internally
        self.currentDF = waveformsDF
    
        return(self.currentDF)
    
    
    def handleWaveformRequest(self, request, secondsBefore, secondsAfter):
        """
        This funciton is invoked whenever the waveformRequestWatcherThread emits
        a waveformRequestSignal. This means that a new waveform request has been
        assembled and placed on the waveformRequestQueue. The GUI
        WaveformDialog.handleWaveformRequest() function calls this function and
        handles the return values.
        """

        # Pull elements from the request dictionary
        task = request['task']
        downloadDir = request['downloadDir']
        source_time = request['time']
        source_depth = request['source_depth']
        source_lon = request['source_lon']
        source_lat = request['source_lat']
        SNCL = request['SNCL']
        receiver_lon = request['receiver_lon']
        receiver_lat = request['receiver_lat']
        plot_width = request['plot_width']
        plot_height = request['plot_height']
        waveformID = request['waveformID']

        self.logger.debug("waveformRequestSignal: %s -- %s", task, waveformID)

        # Calculate arrival times
        self.logger.debug("%s calculate travel time", SNCL)
        try:
            model = TauPyModel(model='iasp91') # TODO:  should TauP model be an optional parameter?
            tt = model.get_travel_times_geo(source_depth, source_lat, source_lon, receiver_lat, receiver_lon)
        except Exception as e:
            self.logger.error('%s', e)
            return("ERROR", waveformID, "", str(e))

        # TODO:  Are traveltimes always sorted by time?
        # TODO:  Do we need to check the phase?
        earliest_arrival_time = UTCDateTime(source_time) + tt[0].time

        starttime = earliest_arrival_time - secondsBefore
        endtime = earliest_arrival_time + secondsAfter

        # Download the waveform
        self.logger.debug("%s download waveform", SNCL)    
        (network, station, location, channel) = SNCL.split('.')
        try:
            st = self.client.get_waveforms(network, station, location, channel, starttime, endtime)
        except Exception as e:
            self.logger.error('%s', e)
            return("ERROR", waveformID, "", str(e))

        # Save the miniseed file
        startstring = starttime.format_iris_web_service()
        endstring = endtime.format_iris_web_service()
        mseedFile = downloadDir + '/' + SNCL + '_' + startstring + '_' + endstring + ".MSEED"
        self.logger.debug("%s save as MiniSEED", SNCL)
        try:
            st.write(mseedFile, format="MSEED")
        except Exception as e:
            self.logger.error('%s', e)
            return("ERROR", waveformID, "", str(e))
        
        # Successful completion
        return("MSEED_READY", waveformID, mseedFile, "")
    
    
    def getWaveformImagePath(self, waveformID):
        waveformIDs = self.currentDF.WaveformID.tolist()
        index = waveformIDs.index(waveformID)
        imagePath = self.currentDF.WaveformImagePath.iloc[index]
        return(imagePath)
    
    def setWaveformImagePath(self, waveformID, imagePath):
        waveformIDs = self.currentDF.WaveformID.tolist()
        index = waveformIDs.index(waveformID)
        self.currentDF.WaveformImagePath.iloc[index] = imagePath
        return
    
    def getWaveformKeep(self, waveformID):
        waveformIDs = self.currentDF.WaveformID.tolist()
        index = waveformIDs.index(waveformID)
        keep = self.currentDF.Keep.iloc[index]
        return(keep)
    
    def setWaveformKeep(self, waveformID, keep):
        waveformIDs = self.currentDF.WaveformID.tolist()
        index = waveformIDs.index(waveformID)
        self.currentDF.Keep.iloc[index] = keep
        return
    
    def getColumnNames(self):
        columnNames = ['Keep', 'SNCL', 'Distance', 'Magnitude', 'Depth', 'Time', 'Waveform', 'Event_Lon', 'Event_Lat', 'EventID', 'Network', 'Station', 'Station_Lon', 'Station_Lat', 'WaveformID', 'WaveformStationID', 'WaveformImagePath']
        return(columnNames)
    
    def getColumnHidden(self):
        is_hidden =    [False,  False,  False,      False,       False,   False,  False,      True,        True,        True,      True,      True,      True,          True,          True,         True,                True]
        return(is_hidden)
    
    def getColumnNumeric(self):
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
