"""
Container for waveforms.

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

#import urllib
import os

import numpy as np
import pandas as pd

from obspy import UTCDateTime
from obspy.taup import TauPyModel
from obspy.clients import fdsn
from obspy.geodetics import locations2degrees



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
            if os.path.exists(imagePath):
                waveformsDF['Downloaded'] = False
            else:
                waveformsDF['Downloaded'] = True
        
        # Reorganize columns

        self.currentDF = waveformsDF
    
        return(waveformsDF)
    
    
    def download_data(self, parameters=None):
        """
        Make a webservice request for waveforms using the passed in options
        """
        # TOOD:  Sanity check parameters
        
        # TODO:  Should parameters be called "event_sncls" and passed in as a dataframe?
        
        source_time = parameters['time']
        source_depth = parameters['source_depth']
        source_lon = parameters['source_lon']
        source_lat = parameters['source_lat']
        stationID = parameters['stationID']
        receiver_lon = parameters['receiver_lon']
        receiver_lat = parameters['receiver_lat']
        
        self.logger.info('Loading data for %s-%s...', source_time, stationID)
        
        try:
            self.logger.debug('Calculating travel times...')
            model = TauPyModel(model='iasp91') # TODO:  should TauP model be an optional parameter?
            tt = model.get_travel_times_geo(source_depth, source_lat, source_lon, receiver_lat, receiver_lon)
        except Exception as e:
            self.logger.debug('%s', e)
            # TODO:  What type of exception to trap?
            raise
        
        # TODO:  Are traveltimes always sorted by time?
        # TODO:  Do we need to check the phase?
        earliest_arrival_time = UTCDateTime(source_time) + tt[0].time
        
        # TODO:  get user chosen window parameters from WaveformOptionsDialog
        secs_before = 60
        secs_after = 600
        starttime = earliest_arrival_time - secs_before
        endtime = earliest_arrival_time + secs_after
        
        # Get the waveform
        dataCenter = "IRIS"
        client = fdsn.Client(dataCenter)
        (network, station, location, channel) = stationID.split('.')
        self.logger.info('Loading %s from %s', stationID, dataCenter)
        try:
            st = client.get_waveforms(network, station, location, channel, starttime, endtime)
        except Exception as e:
            self.logger.error('%s', e)
        
        # Create the png image
        filename = self.downloadDir + '/' + stationID + '_' + str(source_time) + ".png"
        imagePath = filename
        self.logger.debug('Saving %s', filename)
        try:
            st.plot(outfile=filename) # TODO:  Add plot customizations
        except Exception as e:
            self.logger.error('%s', e)
        
        # Save the miniseed file
        filename = self.downloadDir + '/' + stationID + '_' + str(source_time) + ".MSEED"
        self.logger.debug('Saving %s', filename)
        try:
            st.write(filename, format="MSEED") 
        except Exception as e:
            self.logger.error('%s', e)
        
        return(imagePath)
    
        
    def load_data(self, parameters=None):
        """
        Make a webservice request for waveforms using the passed in options
        """
        # TOOD:  Sanity check parameters
        
        # TODO:  Should parameters be called "event_sncls" and passed in as a dataframe?
        
        # TODO: loop over event-sncl combinations
        for i in range(len(parameters['times'])):
            source_time = parameters['times'][i]
            source_depth = parameters['source_depths'][i]
            source_lon = parameters['source_lons'][i]
            source_lat = parameters['source_lats'][i]
            stationID = parameters['stationIDs'][i]
            receiver_lon = parameters['receiver_lons'][i]
            receiver_lat = parameters['receiver_lats'][i]
            
            self.logger.info('Loading data for %s-%s...', source_time, stationID)
            
            try:
                self.logger.debug('Calculating travel times...')
                model = TauPyModel(model='iasp91') # TODO:  should TauP model be an optional parameter?
                tt = model.get_travel_times_geo(source_depth, source_lat, source_lon, receiver_lat, receiver_lon)
            except Exception as e:
                self.logger.debug('%s', e)
                # TODO:  What type of exception to trap?
                raise
            
            # TODO:  Are traveltimes always sorted by time?
            # TODO:  Do we need to check the phase?
            earliest_arrival_time = UTCDateTime(source_time) + tt[0].time
            
            # TODO:  get user chosen window parameters from WaveformOptionsDialog
            secs_before = 60
            secs_after = 600
            starttime = earliest_arrival_time - secs_before
            endtime = earliest_arrival_time + secs_after
            
            # Get the waveform
            dataCenter = "IRIS"
            client = fdsn.Client(dataCenter)
            (network, station, location, channel) = stationID.split('.')
            self.logger.info('Loading %s from %s', stationID, dataCenter)
            try:
                st = client.get_waveforms(network, station, location, channel, starttime, endtime)
            except Exception as e:
                self.logger.error('%s', e)
            
            # Create the png image
            filename = self.downloadDir + '/' + stationID + '_' + str(source_time) + ".png"
            imagePath = filename
            self.logger.debug('Saving %s', filename)
            try:
                st.plot(outfile=filename) # TODO:  Add plot customizations
            except Exception as e:
                self.logger.error('%s', e)
            
            # Save the miniseed file
            filename = self.downloadDir + '/' + stationID + '_' + str(source_time) + ".MSEED"
            self.logger.debug('Saving %s', filename)
            try:
                st.write(filename, format="MSEED") 
            except Exception as e:
                self.logger.error('%s', e)
            
            # TODO:  Keep track of successfully downloaded files in waveformsDF.Downloaded
            

        # TODO:  return success or failure?
        debug_point = True
        
        return(imagePath)

    def get_column_names(self):
        columnNames = ['SNCL', 'Distance', 'Time', 'Magnitude', 'Event_Lon', 'Event_Lat', 'Depth/km', 'EventID', 'Network', 'Station', 'Station_Lon', 'Station_Lat', 'WaveformID', 'WaveformStationID', 'Waveform', 'Downloaded']
        return(columnNames)
    
    
        
# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
