"""
Subprocess class for downloading waveforms.

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)

This process is started up when the WaveformsDialog "Download / Refresh" button
is pressed and continues until it is finished downloading.

# TODO:  It can be interrupted with a (?signal) from the WaveformsDialog.
        
After each waveform is downloaded and written to disk, a message is placed on
the waveformResponseQueue.  This thread and multi-process safe queue is watched
in a waveformsWatcher thread started when the WaveformsDialog initializes.

Waveforms downloading is both IO- and CPU-intensive so running it in an entirely
separate process seems best. 
"""

from __future__ import (absolute_import, division, print_function)

# Basic packages
import os
import logging

# Multi-processing
import multiprocessing

# ObsPy
from obspy import UTCDateTime
from obspy.taup import TauPyModel
from obspy.clients import fdsn

# NOTE:  Good documentation and examples of python multiprocessing:
# NOTE:
# NOTE:    https://pymotw.com/2/multiprocessing/
# NOTE:    http://www.blog.pythonlibrary.org/tag/concurrency/
# NOTE:    http://oz123.github.io/writings/2015-02-25-Simple-Multiprocessing-Task-Queue-in-Python/

class WaveformsDownloader(multiprocessing.Process):
    """
    Subprocess class for downloading waveforms.

    :param parametersList: list of parameter dictionaries containing information
        needed to download waveforms
    :param waveformResponseQueue: python Queue ready to receive messages with the
        success or failure status of each attempted waveform download
    """
    def __init__(self, parametersList, waveformReqeustQueue, waveformResponseQueue):
        super(WaveformsDownloader, self).__init__()
        
        # Set up multiprocessor logging
        multiprocessing.log_to_stderr()
        self.logger = multiprocessing.get_logger()
        self.logger.setLevel(logging.DEBUG)    
        
        # Configured properties
        self.secs_before = 60 # TODO:  get configurable plot properties from WaveformOptionsDialog
        self.secs_after = 600 # TODO:  get configurable plot properties from WaveformOptionsDialog

        # Save arguments as class propteries
        self.parametersList = parametersList
        self.waveformResponseQueue = waveformResponseQueue        
    
        return
        
        
    def run(self):
        """
        Work through the parametersList, downloading each associated waveform in turn.
        
        After making a webservice request for data, place a message on the waveformResponseQueue
        with information about the success or failure of the request.
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
            self.waveformResponseQueue.put( {"status":"OK", "waveformID":waveformID, "mseedFile":"", "message":message} )

            try:
                model = TauPyModel(model='iasp91') # TODO:  should TauP model be an optional parameter?
                tt = model.get_travel_times_geo(source_depth, source_lat, source_lon, receiver_lat, receiver_lon)
            except Exception as e:
                self.waveformResponseQueue.put( {"status":"ERROR", "waveformID":waveformID, "mseedFile":"", "message":str(e)} )                
                self.logger.error('%s', e)
                continue
        
            # TODO:  Are traveltimes always sorted by time?
            # TODO:  Do we need to check the phase?
            earliest_arrival_time = UTCDateTime(source_time) + tt[0].time
            
            starttime = earliest_arrival_time - self.secs_before
            endtime = earliest_arrival_time + self.secs_after
            
            self.logger.debug("%s client.get_waveforms", SNCL)

            # Get the waveform
            dataCenter = "IRIS" # TODO:  dataCenter should be configurable
            client = fdsn.Client(dataCenter)
            (network, station, location, channel) = SNCL.split('.')
            try:
                st = client.get_waveforms(network, station, location, channel, starttime, endtime)
            except Exception as e:
                self.waveformResponseQueue.put( {"status":"ERROR", "waveformID":waveformID, "mseedFile":"", "message":str(e)} )                
                self.logger.error('%s', e)
                continue
            
            # Save the miniseed file
            filename = downloadDir + '/' + SNCL + '_' + str(source_time) + ".MSEED"
            self.logger.debug("%s st.write filename=%s", SNCL, filename)
            try:
                st.write(filename, format="MSEED")
            except Exception as e:
                self.waveformResponseQueue.put( {"status":"ERROR", "waveformID":waveformID, "mseedFile":"", "message":str(e)} )                
                self.logger.error('%s', e)
                continue
                
            # TODO:  Is this the place to save another version of the data in the configurable directory in the configurable format?
            
            # NOTE:  Getting the following when I try to plot while using multiprocessing
            # NOTE:
            # NOTE:  The process has forked and you cannot use this CoreFoundation functionality safely. You MUST exec().
            # NOTE:  Break on __THE_PROCESS_HAS_FORKED_AND_YOU_CANNOT_USE_THIS_COREFOUNDATION_FUNCTIONALITY___YOU_MUST_EXEC__() to debug.
            # NOTE:
            # NOTE:  So, instead of generating plots in this separate process, we will only save files.
            # NOTE:  A separate waveformsDialog.waveformsWatcherThread is in charge of watching for results
            # NOTE:  appearing on waveformsDialog.waveformResponseQueue and signals the main thread.
            # NOTE:
            # NOTE:  All plotting and GUI updating should be handled by the GUI main thread.

            # Announce that this file is ready for plotting
            # TODO:  Maybe change the status and message to reflect "MSEED_READY". It's not up the the downloader to decide what happens next.
            message = "Plotting %s" % basename
            self.waveformResponseQueue.put( {"status":"READY", "waveformID":waveformID, "mseedFile":filename, "message":message})
            
            
        # Send a message saying we are finished
        # TODO:  Maybe change status to "FINISHED"
        message = "Finished downloading %d waveforms" % len(self.parametersList)
        self.waveformResponseQueue.put( {"status":"OK", "waveformID":"", "mseedFile":"", "message":message} )  
        
        