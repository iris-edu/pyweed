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
    
    def load_data(self, parameters=None):
        """
        Make a webservice request for waveforms using the passed in options
        """
        # TOOD:  Sanity check parameters
        
        # TODO:  Should parameters be called "event_sncls" and passed in as a dataframe?
        
        # TODO: loop over event-sncl combinations
        i = 0
        source_time = parameters['times'][i]
        source_depth = parameters['source_depths'][i]
        source_lon = parameters['source_lons'][i]
        source_lat = parameters['source_lats'][i]
        stationID = parameters['stationIDs'][i]
        receiver_lon = parameters['receiver_lons'][i]
        receiver_lat = parameters['receiver_lats'][i]
        
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
        
        # TODO:  get user chosen window parameters
        secs_before = 60
        secs_after = 600
        starttime = earliest_arrival_time - secs_before
        endtime = earliest_arrival_time + secs_after
        
        # Get the waveform
        dataCenter = "IRIS"
        client = fdsn.Client(dataCenter)
        (network, station, location, channel) = stationID.split('.')
        self.logger.info('Loading %s from %s', stationID, dataCenter)
        st = client.get_waveforms(network, station, location, channel, starttime, endtime)
        
        # TODO:  Plot it?
        ###st.plot()
        
        # TODO:  return success or failure?
        debug_point = True
        
        return(True)
    
        
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
