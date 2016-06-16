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

from obspy import UTCDateTime

class Events(object):
    """
    Container for events.
    """
    def __init__(self):
        """
        Initialization.
        """
        # TODO:  Better strucutre/objects for storing history?
        self.parameters_history = []
        self.url_history = []
        self.df_history = []
        
    def get_parameters(self, index=0):
        return(self.parameters_history[index])
    
    def get_url(self, index=0):
        return(self.url_history[index])
    
    def get_df(self, index=0):
        return(self.df_history[index])

    def query(self, parameters=None):
        """
        Make a webservice request for events using the passed in options
        """
        # Sanity check
        if not parameters.has_key('starttime') or not parameters.has_key('endtime'):
            raise('starttime or endtime is missing')
                    
        # Create events webservice URL
        url = build_url(parameters=parameters)
        
        # Check if we have already gotten this url
        if url in self.url_history:
            index = self.url_history.index(url)
            df = self.df_history[index]
            
        else:  
            try:
                # Get events dataframe and clean up column names
                df = pd.read_csv(url, sep='|')
                df.columns = df.columns.str.strip()
                # Push items onto the stack (so the most recent is always in position 0)
                self.parameters_history.insert(0, parameters)
                self.url_history.insert(0, url)
                self.df_history.insert(0, df)
            except:
                # TODO:  What type of exception should we trap? We should probably log it.
                raise
            
        return(df)
        
        
# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------

# Similar to obspy.clients.fdsn.client.py
def build_url(base_url="http://service.iris.edu",
              service="event",
              major_version=1,
              resource_type="query",
              parameters={}):
    """
    Build a FDSN webservice url to request events.

    >>> print(build_url("http://service.iris.edu", "event", 1, \
                        "query", {'starttime':'2015-01-01','endtime':'2015-01-03','minmag':'4.00','format':'text'}))
    http://service.iris.edu/fdsnws/event/1/query?endtime=2015-01-03&starttime=2015-01-01&minmag=4.00&format=text
    """

    # Construct base_url from FDSN provider, service, verstion.
    url = "/".join((base_url, "fdsnws", service,
                    str(major_version), resource_type))
    
    # Aded a parameter for text formatting
    parameters['format'] = 'text'

    # Add parameters
    url = "?".join((url, urllib.parse.urlencode(parameters)))
    
    return url


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
