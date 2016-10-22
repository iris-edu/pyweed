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
import logging

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

# NOTE:  Good documentation and examples of python threading:
# NOTE:    https://pymotw.com/2/multiprocessing/
# NOTE:    http://www.blog.pythonlibrary.org/tag/concurrency/
# NOTE:    http://oz123.github.io/writings/2015-02-25-Simple-Multiprocessing-Task-Queue-in-Python/
# NOTE:
# NOTE:  PyQt Qt threading example
# NOTE:    http://stackoverflow.com/questions/9957195/updating-gui-elements-in-multithreaded-pyqt

class WaveformsDownloader(multiprocessing.Process):
    """
    Subprocess class for downloading waveforms.
    """
    def __init__(self, parametersList, waveformsMessageQueue):
        super(WaveformsDownloader, self).__init__()
        
        # Set up multiprocessor logging
        multiprocessing.log_to_stderr()
        self.logger = multiprocessing.get_logger()
        self.logger.setLevel(logging.DEBUG)    
        
        # Save internal variables
        self.parametersList = parametersList
        self.waveformsMessageQueue = waveformsMessageQueue
    
        return
        
        
    def run(self):
        """
        Make a webservice request for waveforms using the passed in options
        """
                        
        for parameters in self.parametersList:
            
            downloadDir = parameters['downloadDir']
            source_time = parameters['time']
            source_depth = parameters['source_depth']
            source_lon = parameters['source_lon']
            source_lat = parameters['source_lat']
            SNCL = parameters['SNCL']
            receiver_lon = parameters['receiver_lon']
            receiver_lat = parameters['receiver_lat']
            plot_width = parameters['plot_width']
            plot_height = parameters['plot_height']
            waveformID = parameters['waveformID']
            
            self.logger.debug("%s TauPyModel", SNCL)

            basename = SNCL + '_' + str(source_time)

            message = "Downloading %s" % basename
            self.waveformsMessageQueue.put( {"status":"OK", "waveformID":waveformID, "mseedFile":"", "message":message} )

            try:
                model = TauPyModel(model='iasp91') # TODO:  should TauP model be an optional parameter?
                tt = model.get_travel_times_geo(source_depth, source_lat, source_lon, receiver_lat, receiver_lon)
            except Exception as e:
                self.waveformsMessageQueue.put( {"status":"ERROR", "waveformID":waveformID, "mseedFile":"", "message":str(e)} )                
                self.logger.error('%s', e)
                next
        
            # TODO:  Are traveltimes always sorted by time?
            # TODO:  Do we need to check the phase?
            earliest_arrival_time = UTCDateTime(source_time) + tt[0].time
            
            # TODO:  get user chosen window parameters from WaveformOptionsDialog
            secs_before = 60
            secs_after = 600
            starttime = earliest_arrival_time - secs_before
            endtime = earliest_arrival_time + secs_after
            
            self.logger.debug("%s client.get_waveforms", SNCL)

            # Get the waveform
            dataCenter = "IRIS"
            client = fdsn.Client(dataCenter)
            (network, station, location, channel) = SNCL.split('.')
            try:
                st = client.get_waveforms(network, station, location, channel, starttime, endtime)
            except Exception as e:
                self.waveformsMessageQueue.put( {"status":"ERROR", "waveformID":waveformID, "mseedFile":"", "message":str(e)} )                
                self.logger.error('%s', e)
                next
            
            # Save the miniseed file
            filename = downloadDir + '/' + SNCL + '_' + str(source_time) + ".MSEED"
            self.logger.debug("%s st.write filename=%s", SNCL, filename)
            try:
                st.write(filename, format="MSEED") 
            except Exception as e:
                self.waveformsMessageQueue.put( {"status":"ERROR", "waveformID":waveformID, "mseedFile":"", "message":str(e)} )                
                self.logger.error('%s', e)
                next
                

            # NOTE:  Getting the following when I try to plot while using multiprocessing
            # NOTE:
            # NOTE:  The process has forked and you cannot use this CoreFoundation functionality safely. You MUST exec().
            # NOTE:  Break on __THE_PROCESS_HAS_FORKED_AND_YOU_CANNOT_USE_THIS_COREFOUNDATION_FUNCTIONALITY___YOU_MUST_EXEC__() to debug.
            # NOTE:
            # NOTE:  Instead, we plot in a separate *thread* that runs pyweed_gui.WaveformDialog.waveformWatcher().
            
            # Announce that this file is ready for plotting
            message = "Plotting %s" % basename
            self.waveformsMessageQueue.put( {"status":"READY", "waveformID":waveformID, "mseedFile":filename, "message":message})
            
            
            
            ####################################################################
            # TODO:  Solve issue with image creation
            ####################################################################            
            
            ## Create the png image
            #filename = downloadDir + '/' + SNCL + '_' + str(source_time) + ".png"
            #imagePath = filename
            #print("%s st.plot filename=%s" % (SNCL,filename))
            ####self.logger.debug('Saving %s', filename)
            #try:
                ## NOTE:  Getting the following when I try to plot while using multiprocessing
                ## NOTE:
                ## NOTE:  The process has forked and you cannot use this CoreFoundation functionality safely. You MUST exec().
                ## NOTE:  Break on __THE_PROCESS_HAS_FORKED_AND_YOU_CANNOT_USE_THIS_COREFOUNDATION_FUNCTIONALITY___YOU_MUST_EXEC__() to debug.                
                #st.plot(outfile=filename,
                        #size=(plot_width,plot_height))
            #except Exception as e:
                ###self.log.write('%s\n' % e)
                #print("%s" % e)
                #pass

        
        message = "Finished downloading %d waveforms" % len(self.parametersList)
        self.waveformsMessageQueue.put( {"status":"OK", "waveformID":"", "mseedFile":"", "message":message} )  
        
        
## ------------------------------------------------------------------------------
## Helper functions
## ------------------------------------------------------------------------------



## ------------------------------------------------------------------------------
## Main
## ------------------------------------------------------------------------------

#if __name__ == '__main__':
    #import doctest
    #doctest.testmod(exclude_empty=True)
    