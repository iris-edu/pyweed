"""
Subprocess class for downloading waveforms.

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

# Basic packages
import os

# Vectors and dataframes
import numpy as np
import pandas as pd

# Multi-processing
import multiprocessing

# ObsPy
from obspy import UTCDateTime
from obspy.taup import TauPyModel
from obspy.clients import fdsn
from obspy.geodetics import locations2degrees

# https://pymotw.com/2/multiprocessing/basics.html

class WaveformDownloadProcess(multiprocessing.Process):
    """
    Subprocess class for downloading waveforms.
    """
    def __init__(self, parameters):
        super(WaveformDownloadProcess, self).__init__()
        
        self.parameters = parameters
    
        # NOTE:  We cannot use the logging module here as we get the following complaint:
        # NOTE:
        # NOTE:  THE_PROCESS_HAS_FORKED_AND_YOU_CANNOT_USE_THIS_COREFOUNDATION_FUNCTIONALITY___YOU_MUST_EXEC
        
        # Set up logging
        filename = parameters['SNCL'] + '_' + parameters['time'] + '.log'
        logPath = os.path.join(self.parameters['downloadDir'], filename)
        self.log = open(logPath, 'w')
        
        
    def run(self):
        """
        Make a webservice request for waveforms using the passed in options
        """
        self.log.write('Process %s started\n' % self.pid)
        
        # NOTE:  This function is intended to be run as a separate process and cannot use logging
        # NOTE:  or raise errors. It must create it's own separate transcript file if necessary.
        
        # NOTE:  Multi-process example:  https://pymotw.com/2/multiprocessing/basics.html
        # NOTE:  Multi-process example:  http://www.blog.pythonlibrary.org/2016/08/02/python-201-a-multiprocessing-tutorial/
                        
        # TOOD:  Sanity check parameters
        
        # TODO:  Should parameters be called "event_sncls" and passed in as a dataframe? 
        
        downloadDir = self.parameters['downloadDir']
        source_time = self.parameters['time']
        source_depth = self.parameters['source_depth']
        source_lon = self.parameters['source_lon']
        source_lat = self.parameters['source_lat']
        SNCL = self.parameters['SNCL']
        receiver_lon = self.parameters['receiver_lon']
        receiver_lat = self.parameters['receiver_lat']
        plot_width = self.parameters['plot_width']
        plot_height = self.parameters['plot_height']
        
        try:
            model = TauPyModel(model='iasp91') # TODO:  should TauP model be an optional parameter?
            tt = model.get_travel_times_geo(source_depth, source_lat, source_lon, receiver_lat, receiver_lon)
        except Exception as e:
            # TODO:  What type of exception to trap?
            self.log.write('%s\n' % e)
            ###raise
            pass
    
        # TODO:  Are traveltimes always sorted by time?
        # TODO:  Do we need to check the phase?
        earliest_arrival_time = UTCDateTime(source_time) + tt[0].time
        
        # TODO:  get user chosen window parameters from WaveformOptionsDialog
        secs_before = 60
        secs_after = 600
        starttime = earliest_arrival_time - secs_before
        endtime = earliest_arrival_time + secs_after
        
        # Get the waveform
        dataCenter = "IRIS"
        client = fdsn.Client(dataCenter)
        (network, station, location, channel) = SNCL.split('.')
        ###self.logger.info('Process %s -- loading %s from %s', self.pid, SNCL, dataCenter)
        try:
            st = client.get_waveforms(network, station, location, channel, starttime, endtime)
        except Exception as e:
            self.log.write('%s\n' % e)
            pass
        
        # Create the png image
        filename = downloadDir + '/' + SNCL + '_' + str(source_time) + ".png"
        imagePath = filename
        ###self.logger.debug('Saving %s', filename)
        try:
            st.plot(outfile=filename,
                    size=(plot_width,plot_height))
        except Exception as e:
            s##elf.log.write('%s\n' % e)
            pass
        
        # Save the miniseed file
        filename = downloadDir + '/' + SNCL + '_' + str(source_time) + ".MSEED"
        ###self.logger.debug('Saving %s', filename)
        try:
            st.write(filename, format="MSEED") 
        except Exception as e:
            self.log.write('%s\n' % e)
            pass
            
        #self.logger.debug('Process %s completed', self.pid)
        self.log.write('Process %s completed\n' % self.pid)
        self.log.close()

        
        
# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
    