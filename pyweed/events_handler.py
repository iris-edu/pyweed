"""
Container for events.

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

import re
import pandas as pd
from signals import SignalingThread, SignalingObject
import logging
from PyQt4 import QtCore

LOGGER = logging.getLogger(__name__)


class EventsLoader(SignalingThread):
    """
    Thread to handle event requests
    """

    def __init__(self, client, parameters):
        """
        Initialization.
        """
        self.client = client
        self.parameters = parameters
        super(EventsLoader, self).__init__()

    def run(self):
        """
        Make a webservice request for events using the passed in options.
        """
        # Sanity check
        try:
            if not self.parameters.has_key('starttime') or not self.parameters.has_key('endtime'):
                raise ValueError('starttime or endtime is missing')
            LOGGER.info('Loading events...')
            event_catalog = self.client.get_events(**self.parameters)
            self.done.emit(event_catalog)
        except Exception as e:
            # TODO:  What type of exception should we trap?
            self.done.emit(e)
            raise


class EventsDataFrameLoader(SignalingThread):
    """
    Thread to handle event requests
    """

    def __init__(self, event_catalog, column_names):
        """
        Initialization.
        """
        self.event_catalog = event_catalog
        self.column_names = column_names
        super(EventsDataFrameLoader, self).__init__()

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
        Obtain events data as an ObsPy Catalog.
        Then convert this into a pandas dataframe.

        A pandas dataframe is returned.
        """

        # TODO:  Optimize interaction with IRIS by restoring the previous version with
        # TODO:  requests for format="text" and simple pandas import.

        # NOTE:  The parameters dictionary is created by EventsQueryDialog.getOptions()
        # NOTE:  and will be passed as **kwargs to client.get_events:
        # NOTE:
        # NOTE:    https://docs.obspy.org/packages/autogen/obspy.clients.fdsn.client.Client.get_events.html

        # NOTE:  Some datacenters complain about seemingly reasonable requests. Here is a response from SCEDC
        # NOTE:  when we try to get_events(**parameters):

        #Detailed response of server:
        #Error 400: handlerProgram exit code: 3 handlerProgram message: Unrecognized mag format or value, 10.0. Valid format or range is [-1.0 to 9.0]
        #Unrecognized depth format or value, 6731.0. Valid format or range is [0.0 to 700.0]
        #Invalid min lat value -90.0. Valid value range is [30.0 to 39.0]
        #Invalid max lat value 90.0. Value value range is [30.0 to 39.0]
        #Invalid min lon value -180.0. Valid value range is [-124.0.0 to -111.0]
        #Invalid max lon value 180.0. Valid value range is [-124.0 to -111.0]

        # TODO:  Events parameters need to be validated on a per dataCenter basis

        # TODO:  Values extracted from an event_catalog need to be processed on a per dataCenter basis

        # TODO:  Each of these is a big trial-and-error task

        LOGGER.info("Creating events dataframe")

        # Set up empty dataframe
        df = pd.DataFrame(columns=self.column_names)

        for event in self.event_catalog:
            origin = event.preferred_origin() or (len(event.origins) and event.origins[0])
            if not origin:
                LOGGER.error("No preferred origin found for event %s", event)
                continue
            magnitude = event.preferred_magnitude() or (len(event.magnitudes) and event.magnitudes[0])
            if not magnitude:
                LOGGER.error("No preferred magnitude found for event %s", event)
                continue

            # Uniformly handled elements
            time = origin.time.strftime("%Y-%m-%d %H:%M:%S") # use strftime to remove milliseconds
            mag = magnitude.mag
            longitude = origin.longitude
            latitude = origin.latitude
            depth = origin.depth / 1000 # we wish to report in km # TODO:  is this correct?
            magnitude_type = magnitude.magnitude_type
            event_description = "no description"
            if len(event.event_descriptions) > 0:
                event_description = event.event_descriptions[0].text
            author = None           # TODO:  Figure out how to get event author
            catalog = None          # TODO:  Figure out how to get event catalog
            contributor = None      # TODO:  Figure out how to get event contributor
            contributor_id = None   # TODO:  Figure out how to get event contributor_id
            magnitude_author = None # TODO:  Figure out how to get event magnitude_author

            # Need to handle some information differently depending on which dataCenter it comes from
            # NOTE:  List of FDSN datacenters:   http://www.fdsn.org/webservices/datacenters/
            # NOTE:  ObsPy list of datacenters:  https://docs.obspy.org/packages/obspy.clients.fdsn.html
            event_id = event.resource_id.id
            if 'eventid=' in event_id:
                event_id = re.sub('.*eventid=', '', event_id)
            if '/Event/NC/' in event_id:
                # 'quakeml:nc.anss.org/Event/NC/72734605'
                event_id = re.sub('.*/Event/NC/', '', event_id)

            # Append a row to the dataframe
            df.loc[len(df)] = [time,
                               mag,
                               longitude,
                               latitude,
                               depth,
                               magnitude_type,
                               event_description,
                               author,
                               catalog,
                               contributor,
                               contributor_id,
                               magnitude_author,
                               event_id]

        return(df)


class EventsHandler(SignalingObject):
    """
    Container for events.
    """

    catalog_loaded = QtCore.pyqtSignal(object)

    column_names = [
        'Time', 'Magnitude', 'Longitude', 'Latitude', 'Depth/km', 'MagType', 'EventLocationName',
        'Author', 'Catalog', 'Contributor', 'ContributorID', 'MagAuthor', 'EventID'
    ]

    def __init__(self, pyweed):
        """
        Initialization.
        """
        super(EventsHandler, self).__init__()

        self.pyweed = pyweed

        # Current state
        self.event_catalog = None
        self.currentDF = None
        self.selectedIDs = []

        self.catalog_loader = None
        self.data_frame_loader = None

    def load_catalog(self, parameters=None):
        if not parameters:
            parameters = self.pyweed.event_options.get_obspy_options()
        self.catalog_loader = EventsLoader(self.pyweed.client, parameters)
        self.catalog_loader.done.connect(self.on_catalog_loaded)
        self.catalog_loader.start()

    def on_catalog_loaded(self, event_catalog):
        if not isinstance(event_catalog, Exception):
            self.event_catalog = event_catalog
            self.load_data_frame()
        self.catalog_loaded.emit(event_catalog)

    def load_data_frame(self):
        column_names = self.get_column_names()
        self.data_frame_loader = EventsDataFrameLoader(self.event_catalog, column_names)
        self.data_frame_loader.done.connect(self.on_data_frame_loaded)
        self.data_frame_loader.start()

    def on_data_frame_loaded(self, df):
        if not isinstance(df, Exception):
            self.currentDF = df
        self.done.emit(df)

    def get_selected_ids(self):
        return(self.selectedIDs)

    def set_selected_ids(self, IDs):
        self.selectedIDs = IDs

    def get_selected_dataframe(self):
        df = self.currentDF.loc[self.currentDF['EventID'].isin(self.selectedIDs)]
        return(df)

    def get_column_names(self):
        return(self.column_names)


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
