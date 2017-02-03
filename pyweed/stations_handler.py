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
from PyQt4 import QtCore
from obspy.core.inventory.inventory import Inventory

LOGGER = logging.getLogger(__name__)


class StationsLoader(SignalingThread):
    """
    Thread to handle station requests
    """

    def __init__(self, client, parameters):
        """
        Initialization.
        """
        # Keep a reference to globally shared components
        self.client = client
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
            LOGGER.info('Loading stations...')
            inventory = self.client.get_stations(**self.parameters)
            self.done.emit(inventory)
        except Exception as e:
            # If no results found, the client will raise an exception, we need to trap this
            # TODO: this should be much cleaner with a fix to https://github.com/obspy/obspy/issues/1656
            if e.message.startswith("No data"):
                LOGGER.warning("No stations found! Your query may be too narrow.")
                self.done.emit(Inventory([], 'INTERNAL'))
            else:
                self.done.emit(e)
                raise


class StationsDataFrameLoader(SignalingThread):
    """
    Thread to handle event requests
    """

    def __init__(self, inventory, column_names):
        """
        Initialization.
        """
        self.inventory = inventory
        self.column_names = column_names
        super(StationsDataFrameLoader, self).__init__()

    def run(self):
        """
        Make a webservice request for events using the passed in options.
        """
        # Sanity check
        try:
            # Create dataframe of station metadata
            df = self.build_dataframe()
            self.done.emit(df)
        except Exception as e:
            # TODO:  What type of exception should we trap?
            self.done.emit(e)
            raise

    def build_dataframe(self):
        """
        Obtain station data as an ObsPy Inventory.
        Then convert this into a pandas dataframe.

        A pandas dataframe is returned.
        """

        # Set up empty dataframe
        df = pd.DataFrame(columns=self.column_names)

        # Walk through the Inventory object
        for n in self.inventory.networks:
            for s in n.stations:
                for c in s.channels:
                    snclId = n.code + "." + s.code + "." + c.location_code + "." + c.code
                    # Append a row to the dataframe
                    df.loc[len(df)] = [n.code,
                                       s.code,
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

    inventory_loaded = QtCore.pyqtSignal(object)

    column_names = [
        'Network', 'Station', 'Location', 'Channel', 'Longitude', 'Latitude',
        'Elevation', 'Depth', 'Azimuth', 'Dip', 'SensorDescription', 'Scale', 'ScaleFreq',
        'ScaleUnits', 'SampleRate', 'StartTime', 'EndTime', 'SNCL'
    ]

    def __init__(self, pyweed):
        """
        Initialization.
        """
        super(StationsHandler, self).__init__()

        self.pyweed = pyweed

        # Current state
        self.inventory = None
        self.currentDF = None

        self.inventory_loader = None
        self.data_frame_loader = None

    def load_inventory(self, parameters=None):
        if not parameters:
            parameters = self.pyweed.station_options.get_obspy_options()
        self.inventory_loader = StationsLoader(self.pyweed.client, parameters)
        self.inventory_loader.done.connect(self.on_inventory_loaded)
        self.inventory_loader.start()

    def on_inventory_loaded(self, inventory):
        if not isinstance(inventory, Exception):
            self.inventory = inventory
            self.load_data_frame()
        self.inventory_loaded.emit(inventory)

    def load_data_frame(self):
        column_names = self.get_column_names()
        self.data_frame_loader = StationsDataFrameLoader(self.inventory, column_names)
        self.data_frame_loader.done.connect(self.on_data_frame_loaded)
        self.data_frame_loader.start()

    def on_data_frame_loaded(self, df):
        if not isinstance(df, Exception):
            self.currentDF = df
        self.done.emit(df)

    def get_selected_dataframe(self):
        df = self.currentDF.loc[self.currentDF['SNCL'].isin(self.pyweed.selected_station_ids)]
        return(df)

    def get_column_names(self):
        return(self.column_names)


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
