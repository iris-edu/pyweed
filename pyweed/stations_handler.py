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
import logging
from signals import SignalingThread, SignalingObject

LOGGER = logging.getLogger(__name__)


class StationsLoader(SignalingThread):
    """
    Thread to handle station requests
    """

    def __init__(self, client, column_names, parameters):
        """
        Initialization.
        """
        # Keep a reference to globally shared components
        self.client = client
        self.column_names = column_names
        self.parameters = parameters
        super(StationsLoader, self).__init__()

    def run(self):
        """
        Make a webservice request for events using the passed in options.
        """
        # Add level='channel'
        self.parameters['level'] = 'channel'

        # Sanity check
        try:
            if not self.parameters.has_key('starttime') or not self.parameters.has_key('endtime'):
                raise ValueError('starttime or endtime is missing')

            # Create dataframe of station metadata
            LOGGER.info('Loading stations...')
            inventory = self.client.get_stations(**self.parameters)
            df = self.build_dataframe(inventory)
            self.done.emit(df)

        except Exception as e:
            # TODO:  What type of exception should we trap?
            self.done.emit(e)
            raise

    def build_dataframe(self, inventory):
        """
        Obtain station data as an ObsPy Inventory.
        Then convert this into a pandas dataframe.

        A pandas dataframe is returned.
        """

        # Set up empty dataframe
        df = pd.DataFrame(columns=self.column_names)

        # Walk through the Inventory object
        for n in inventory.networks:
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


class StationsHandler(SignalingObject):
    """
    Container for events.
    """

    def __init__(self, client):
        """
        Initialization.
        """
        super(StationsHandler, self).__init__()

        self.client = client

        # Current state
        self.currentDF = None
        self.selectedIDs = []

        self.loader = None

    def load_data(self, parameters=None):
        self.loader = StationsLoader(self.client, self.get_column_names(), parameters)
        self.loader.done.connect(self.on_loader_done)
        self.loader.start()

    def on_loader_done(self, df):
        if not isinstance(df, Exception):
            self.currentDF = df
        self.done.emit(df)

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


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
