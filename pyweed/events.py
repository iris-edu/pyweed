"""
Library for events.

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

import re

import numpy as np
import pandas as pd
from activity import ActivityThread, ActivityObject
from PyQt4 import QtCore


# NOTE:  http://stackoverflow.com/questions/9957195/updating-gui-elements-in-multithreaded-pyqt
class EventsLoader(ActivityThread):
    """
    Thread to handle event requests
    """

    def __init__(self, client, column_names, parameters):
        """
        Initialization.
        """
        # Keep a reference to globally shared components
        self.client = client
        self.column_names = column_names
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

            # Create dataframe of station metadata
            self.log.emit('Loading events...')
            event_catalog = self.client.get_events(**self.parameters)
            df = self.build_dataframe(event_catalog)
            self.done.emit(df)

        except Exception as e:
            # TODO:  What type of exception should we trap?
            self.done.emit(e)
            raise

    def build_dataframe(self, event_catalog):
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

        self.log.emit("Creating events dataframe")

        # Set up empty dataframe
        df = pd.DataFrame(columns=self.column_names)

        for event in event_catalog:
            origin = event.preferred_origin()
            magnitude = event.preferred_magnitude()

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
            if self.client.base_url == "http://service.iris.edu":
                event_id = re.sub('.*eventid=','',event.resource_id.id)
            elif self.client.base_url == "http://service.ncedc.org":
                # 'quakeml:nc.anss.org/Event/NC/72734605'
                event_id = re.sub('.*/Event/NC/','',event.resource_id.id)
            # elif OTHER

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


class EventsManager(ActivityObject):
    """
    Container for events.
    """

    def __init__(self, client):
        """
        Initialization.
        """
        super(EventsManager, self).__init__()

        self.client = client

        # Current state
        self.currentDF = None
        self.selectedIDs = []

        self.loader = None

    def load_data(self, parameters=None):
        self.loader = EventsLoader(self.client, self.get_column_names(), parameters)
        self.loader.done.connect(self.on_loader_done)
        self.loader.log.connect(self.on_loader_log)
        self.loader.start()

    def on_loader_done(self, df):
        if not isinstance(df, Exception):
            self.currentDF = df
        self.done.emit(df)

    def on_loader_log(self, msg):
        self.log.emit(msg)

    def get_selected_ids(self):
        return(self.selectedIDs)

    def set_selected_ids(self, IDs):
        self.selectedIDs = IDs

    def get_selected_dataframe(self):
        df = self.currentDF.loc[self.currentDF['EventID'].isin(self.selectedIDs)]
        return(df)

    def get_column_names(self):
        columnNames = ['Time', 'Magnitude', 'Longitude', 'Latitude', 'Depth/km', 'MagType', 'EventLocationName', 'Author', 'Catalog', 'Contributor', 'ContributorID', 'MagAuthor', 'EventID']
        return(columnNames)


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
