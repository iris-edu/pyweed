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
    def __init__(self, logger):
        """
        Initialization.
        """
        self.logger = logger
        
        # TODO:  Historical stuff should be saved elsewhere so that the Events class 
        # TODO:  will only have current state.
        self.url_history = []
        
        # Current state
        self.currentDF = None
        self.selectedIDs = []
        
    def get_url(self, index=0):
        return(self.url_history[index])
    
    def create_waveformsDF(self, eventsDF, stationsDF):
        """
        Create a dataframe of event-SNCL combinations
        """
        # Create a new dataframe with time, source_lat, source_lon, source_mag, source_depth, SNCL, receiver_lat, receiver_lon -- one for each waveform
        eventsDF = eventsDF[['Time','Magnitude','Depth/km','Longitude','Latitude','EventID']]
        eventsDF.columns = ['Time','Magnitude','Depth','Event_Lon','Event_Lat','EventID']
        
        stationsDF = stationsDF[['SNCL','Network','Station','Longitude','Latitude']]
        stationsDF.columns = ['SNCL','Network','Station','Station_Lon','Station_Lat']
        
        self.logger.debug('Generating event-station combined dataframe...')

        waveformDFs = []

        for i in range(stationsDF.shape[0]):
            df = eventsDF.copy()
            df['SNCL'] = stationsDF.SNCL.iloc[i]
            df['Network'] = stationsDF.Network.iloc[i]
            df['Station'] = stationsDF.Station.iloc[i]
            df['Station_Lon'] = stationsDF.Station_Lon.iloc[i]
            df['Station_Lat'] = stationsDF.Station_Lat.iloc[i]
            waveformDFs.append(df)
            
        waveformsDF = pd.concat(waveformDFs)
        
        # Add waveformID, and WaveformStationID
        waveformsDF['WaveformID'] = waveformsDF.EventID + '_' + waveformsDF.SNCL
        waveformsDF['WaveformStationID'] = waveformsDF.EventID + '_' + waveformsDF.Network + '.' + waveformsDF.Station
        
        # Add event-station distance -------------------------------------------
        
        # NOTE:  Save time by only calculating on distance per station rather than per channel
        self.logger.debug('Calculating %d event-station distances...', len(waveformsDF.WaveformStationID.unique()))
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
        
        # All done -------------------------------------------------------------
        
        # Add Downloaded
        waveformsDF['Downloaded'] = False
        
        self.currentDF = waveformsDF
    
        return(waveformsDF)
    
    
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
            
            # TODO:  Save it to a file
            filename = stationID + '_' + str(source_time) + ".MSEED"
            self.logger.debug('Saving %s', filename)
            try:
                st.write(filename, format="MSEED") 
            except Exception as e:
                self.logger.error('%s', e)
            
            # TODO:  Keep track of successfully downloaded files in waveformsDF.Downloaded
            
            # TODO:  Plot it?
            ###st.plot()

        # TODO:  return success or failure?
        debug_point = True
        
        return(st)
    
        
    def get_selected_ids(self):
        return(self.selectedIDs)
    
    def set_selected_ids(self, IDs):
        self.selectedIDs = IDs
        
    #def get_selected_dataframe(self):
        #df = self.currentDF.loc[self.currentDF['SNCL'].isin(self.selectedIDs)]
        #return(df)
    
        
# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
