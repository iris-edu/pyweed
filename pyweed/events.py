"""
Container for events.

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

import numpy as np
import pandas as pd


class Events(object):
    """
    Container for events.
    """
    def __init__(self, logger=None):
        """
        Initializes the Events container.
        """
        # TODO:  Better strucutre/objects for storing history?
        parameters_history = []
        url_history = []
        df_history = []
        
    def get_parameters(self, index=0):
        return(self.parameters_history[index])
    
    def get_url(self, index=0):
        return(self.url_history[index])
    
    def get_df(self, index=0):
        return(self.df_history[index])
    
    def build_url(self, parameters):
        # TODO:  Much more attention to detail when building the url. Probably loop over parameters and only add when "is not None"
        # TODO:  We should support requests from other FDSN service providers as well. Do they all support "format=text"?
        params = (parameters['starttime'], parameters['endtime'], parameters['minmag'])
        url = 'http://service.iris.edu/fdsnws/event/1/query?starttime=%s&endtime=%s&minmag=%f&format=text' % params
        return(url)

    def query_events(self,
                     starttime=None, endtime=None,
                     minmag=0, maxmag=None, magtype=None,
                     mindepth=None, maxdepth=None):
        """
        """
        # TODO:  Better structure/objects for adding things to the history?
        # TODO:  How many of the options defined for this web service should we support? All?
        parameters = {'starttime':starttime,
                      'endtime':endtime,
                      'minmag':minmag}
        
        url = build_url(parameters)
        
        # Check if we have already gotten this url
        if url in self.url_history:
            index = self.url_history.index(url)
            df = df_history[index]
            
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
        

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
