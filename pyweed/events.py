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

class Events(object):
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
        self.eventsDF = None
        self.selectedRows = []
        
    def get_url(self, index=0):
        return(self.url_history[index])
    
    def get_dataframe(self, parameters=None):
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
            # Push items onto the stack (so the most recent is always in position 0)
            self.url_history.insert(0, url)
        except:
            # TODO:  What type of exception should we trap? We should probably log it.
            raise
            
        self.current_eventsDF = df
        
        return(df)

    def get_selectedRows(self):
        return(self.selectedRows)
    
    def set_selectedRows(self, selectedRows):
        self.selectedRows = selectedRows
        
        
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
