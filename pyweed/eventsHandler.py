"""
Container for events.

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

import urllib

import numpy as np
import pandas as pd

class EventsHandler(object):
    """
    Container for events.
    """
    def __init__(self):
        """
        Initialization.
        """
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
        Make a webservice request for events using the passed in options
        """
        # Sanity check
        if not parameters.has_key('starttime') or not parameters.has_key('endtime'):
            raise('starttime or endtime is missing')
                    
        # Create events webservice URL
        url = build_url(parameters=parameters, output_format="text")
                    
        try:
            # Get events dataframe and clean up column names
            df = pd.read_csv(url, sep='|')
            df.columns = df.columns.str.strip()
            df.columns = df.columns.str.lstrip('#') # remove '#' from '#EventID'
            # Rearrange columns
            df = df[self.get_column_names()]
            # Convert EventID to character
            df['EventID'] = df['EventID'].astype(str)
            # Push items onto the stack (so the most recent is always in position 0)
            self.url_history.insert(0, url)
        except:
            # TODO:  What type of exception should we trap? We should probably log it.
            raise
            
        self.currentDF = df
        
        return(df)

    def get_column_names(self):
        columnNames = ['Time', 'Magnitude', 'Longitude', 'Latitude', 'Depth/km', 'MagType', 'EventLocationName', 'Author', 'Catalog', 'Contributor', 'ContributorID', 'MagAuthor', 'EventID']
        return(columnNames)
    
    def get_selected_ids(self):
        return(self.selectedIDs)
    
    def set_selected_ids(self, IDs):
        self.selectedIDs = IDs
        
    def get_selected_dataframe(self):
        df = self.currentDF.loc[self.currentDF['EventID'].isin(self.selectedIDs)]
        return(df)
        
        
# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------

# Similar to obspy.clients.fdsn.client.py
def build_url(base_url="http://service.iris.edu",
              service="event",
              major_version=1,
              resource_type="query",
              parameters={},
              output_format="xml"):
    """
    Build a FDSN webservice url to request events.

    >>> print(build_url("http://service.iris.edu", "event", 1, \
                        "query", {'starttime':'2015-01-01','endtime':'2015-01-03','minmag':'4.00'}, "text"))
    http://service.iris.edu/fdsnws/event/1/query?endtime=2015-01-03&starttime=2015-01-01&minmag=4.00&format=text
    """

    # Construct base_url from FDSN provider, service, verstion.
    url = "/".join((base_url, "fdsnws", service,
                    str(major_version), resource_type))
    
    # Aded a parameter for the output format -- either 'xml' (used to generate an ObsPy catalog) or 'text' (used to generate a pandas dataframe)
    parameters['format'] = output_format

    # Add parameters
    url = "?".join((url, urllib.urlencode(parameters)))
    
    return url


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
