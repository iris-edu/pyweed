"""
Container for events.

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

class EventsHandler(object):
    """
    Container for events.
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
        df = self.currentDF.loc[self.currentDF['EventID'].isin(self.selectedIDs)]
        return(df)

    def get_column_names(self):
        columnNames = ['Time', 'Magnitude', 'Longitude', 'Latitude', 'Depth/km', 'MagType', 'EventLocationName', 'Author', 'Catalog', 'Contributor', 'ContributorID', 'MagAuthor', 'EventID']
        return(columnNames)
    

    def load_data(self, parameters=None):
        """
        Make a webservice request for events using the passed in options.
        
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
        Obtain events data as an ObsPy Catalog.
        Then convert this into a pandas dataframe.
        
        A pandas dataframe is returned.
        """
        
        # NOTE:  The parameters dictionary is created by EventsQueryDialog.getOptions()
        # NOTE:  and will be passed as **kwargs to client.get_events:
        # NOTE:
        # NOTE:    https://docs.obspy.org/packages/autogen/obspy.clients.fdsn.client.Client.get_events.html
    
        try:
            event_catalog = self.client.get_events(**parameters)
            
        except Exception as e:
            raise   
        
        # Set up empty dataframe
        df = pd.DataFrame(columns=self.get_column_names())

        for event in event_catalog:
            origin = event.preferred_origin()
            magnitude = event.preferred_magnitude()
            # Append a row to the dataframe
            df.loc[len(df)] = [origin.time.strftime("%Y-%m-%d %H:%M:%S"), # use strftime to remove milliseconds
                               magnitude.mag,
                               origin.longitude,
                               origin.latitude,
                               origin.depth/1000, # IRIS event webservice returns depth in km # TODO:  check this
                               magnitude.magnitude_type,
                               event.event_descriptions[0].text,
                               None,     # TODO:  Figure out how to get instrument 'Author'
                               None,     # TODO:  Figure out how to get instrument 'Catalog'
                               None,     # TODO:  Figure out how to get instrument 'Contributor'
                               None,     # TODO:  Figure out how to get instrument 'ContributorID'
                               None, # magnitude.creation_info.author, # not always present
                               re.sub('.*eventid=','',event.resource_id.id)]
                    
        return(df)
        
        
# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
