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

#    def query(self,
#              starttime=None, endtime=None,
#              minmag=0, maxmag=None, magtype=None,
#              mindepth=None, maxdepth=None):
    def query(self, optionsDict=None):
        """
        """
        # Sanity check
        if not optionsDict.has_key('starttime') or not optionsDict.has_key('endtime'):
            raise('starttime or endtime is missing')
        
        # Guarantee that all parameters are properly formatted strings        
        # Required parameters
        
        parameters = {'starttime':UTCDateTime(optionsDict['starttime']).format_iris_web_service(),
                      'endtime':UTCDateTime(optionsDict['endtime']).format_iris_web_service(),
                      'minmag':'%.1f' % float(optionsDict['minmag']),
                      'format':'text'}        
        # Optional parameters
        if optionsDict.has_key('maxmag'):
            parameters['maxmag'] = '%.1f' % float(optionsDict['maxmag'])
        if optionsDict.has_key('magtype'):
            parameters['magtype'] = str(optionsDict['magtype'])
        if optionsDict.has_key('mindepth'):
            parameters['mindepth'] = '%.4f' % float(optionsDict['mindepth'])
        if optionsDict.has_key('maxdepth'):
            parameters['maxdepth'] = '%.4f' % float(optionsDict['maxdepth'])
            
        # Create events webservice URL
        url = build_url(parameters=parameters)
        
        # Check if we have already gotten this url
        if url in self.url_history:
            index = self.url_history.index(url)
            df = self.df_history[index]
            
        else:  
            try:
                df = pd.read_csv(url, sep='|')       
                # Push items onto the stack (so the most recent is always in position 0)
                self.parameters_history.insert(0,parameters)
                self.url_history.insert(0,url)
                self.df_history.insert(0,df)
            except:
                # TODO:  What type of exception should we trap? We should probably log it.
                raise
        
        
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

    # Add parameters
    url = "?".join((url, urllib.parse.urlencode(parameters)))
    return url


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
