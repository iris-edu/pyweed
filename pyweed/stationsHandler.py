"""
Container for stations.

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

import numpy as np
import pandas as pd

class StationsHandler(object):
    """
    Container for stations.
    """
    def __init__(self, logger, preferences, client):
        """
        Initialization.
        """
        # Keep a reference to globally shared components
        self.logger = logger
        self.preferences = preferences
        self.client = client

        # Current state
        self.currentDF = None
        self.selectedIDs = []
        
    def get_selected_ids(self):
        return(self.selectedIDs)
    
    def set_selected_ids(self, IDs):
        self.selectedIDs = IDs
        
    def get_selected_dataframe(self):
        df = self.currentDF.loc[self.currentDF['SNCL'].isin(self.selectedIDs)]
        return(df)    
        
    def get_column_names(self):
        columnNames = ['Network', 'Station', 'Location', 'Channel', 'Longitude', 'Latitude', 'Elevation', 'Depth', 'Azimuth', 'Dip', 'SensorDescription', 'Scale', 'ScaleFreq', 'ScaleUnits', 'SampleRate', 'StartTime', 'EndTime', 'SNCL']
        return(columnNames)


    def load_data(self, parameters=None):
        """
        Make a webservice request for stations using the passed in options.
        
        A pandas dataframe is stored in self.currentDF and is also returned.
        """
        # Sanity check
        if not parameters.has_key('starttime') or not parameters.has_key('endtime'):
            raise('starttime or endtime is missing')                   
        
        try:
            # Create dataframe of station metadata
            self.logger.debug('Loading stations...')
            df = self.build_dataframe(parameters)
            
        except Exception as e:
            # TODO:  What type of exception should we trap?
            self.logger.error('%s', e)
            raise

        self.currentDF = df

        return(df)
        
        
    def build_dataframe(self, parameters):
        """
        Obtain station data as an ObsPy Inventory.
        Then convert this into a pandas dataframe.
        
        A pandas dataframe is returned.
        """
        
        # TODO:  Optimize interaction with IRIS by restoring the previous version with 
        # TODO:  requests for format="text" and simple pandas import.
        
        # NOTE:  The parameters dictionary is created by StationsQueryDialog.getOptions()
        # NOTE:  and will be passed as **kwargs to client.get_stations:
        # NOTE:
        # NOTE:    https://docs.obspy.org/packages/autogen/obspy.clients.fdsn.client.Client.get_stations.html
    
        # Add level='channel'
        parameters['level'] = 'channel'

        try:
            sncl_inventory = self.client.get_stations(**parameters)
    
        except Exception as e:
            raise
    
        # Set up empty dataframe
        df = pd.DataFrame(columns=self.get_column_names())
    
        # Walk through the Inventory object
        for n in sncl_inventory.networks:
            for s in n.stations:
                for c in s.channels:
                    snclId = n.code + "." + s.code + "." + c.location_code + "." + c.code
                    # Append a row to the dataframe
                    df.loc[len(df)] = [n.code, s.code,
                                       c.location_code,
                                       c.code,
                                       c.longitude,
                                       c.latitude,
                                       c.elevation,
                                       c.depth,
                                       c.azimuth,
                                       c.dip,
                                       c.sensor.description,
                                       None,     # TODO:  Figure out how to get instrument 'Scale'
                                       None,     # TODO:  Figure out how to get instrument 'ScaleFreq'
                                       None,     # TODO:  Figure out how to get instrument 'ScaleUnits'
                                       c.sample_rate,
                                       c.start_date,
                                       c.end_date,
                                       snclId]
                                       
        return(df)


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
