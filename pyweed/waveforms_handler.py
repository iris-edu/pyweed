"""
Container for waveforms.

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

# Basic packages
#import urllib
import os

# Vectors and dataframes
import numpy as np
import pandas as pd

## Multi-threading
#from Queue import Queue
#from threading import Thread
# Multi-processing
#import multiprocessing

# ObsPy
from obspy import UTCDateTime
from obspy.taup import TauPyModel
from obspy.clients import fdsn
from obspy.geodetics import locations2degrees
from signals import SignalingThread, SignalingObject
from Queue import PriorityQueue
import collections
from PyQt4 import QtCore
import obspy
from logging import getLogger
import matplotlib

LOGGER = getLogger(__name__)


class WaveformResult(object):
    """
    Container for a waveform result to be passed as a signal, includes the waveform ID so that
    the result can be correctly handled.
    """
    def __init__(self, waveform_id, result):
        self.waveform_id = waveform_id
        self.result = result


class WaveformLoader(SignalingThread):
    """
    Thread to handle event requests
    """

    def __init__(self, client, waveform, preferences, secondsBefore, secondsAfter):
        """
        Initialization.
        """
        # Keep a reference to globally shared components
        self.client = client
        self.waveform = waveform
        self.downloadDir = preferences.Waveforms.downloadDir
        # TODO:  plot_width, plot_height should come from preferences
        self.plot_width = 600
        self.plot_height = 120  # This this must be >100!
        self.secondsBefore = secondsBefore
        self.secondsAfter = secondsAfter
        super(WaveformLoader, self).__init__()

    def run(self):
        """
        Make a webservice request for events using the passed in options.
        """
        try:
            waveform_id = self.waveform.WaveformID

            LOGGER.debug("Loading waveform: %s", waveform_id)

            # Calculate arrival times
            LOGGER.debug("%s calculate travel time", self.waveform.SNCL)
            model = TauPyModel(model='iasp91') # TODO:  should TauP model be an optional parameter?
            tt = model.get_travel_times_geo(
                self.waveform.Depth,
                self.waveform.Event_Lat,
                self.waveform.Event_Lon,
                self.waveform.Station_Lat,
                self.waveform.Station_Lon)

            # TODO:  Are traveltimes always sorted by time?
            # TODO:  Do we need to check the phase?
            earliest_arrival_time = UTCDateTime(self.waveform.Time) + tt[0].time

            starttime = earliest_arrival_time - self.secondsBefore
            endtime = earliest_arrival_time + self.secondsAfter

            startstring = starttime.format_iris_web_service()
            endstring = endtime.format_iris_web_service()
            mseedFile = "%s/%s_%s_%s.MSEED" % (self.downloadDir, self.waveform.SNCL, startstring, endstring)
            LOGGER.debug("%s save as MiniSEED", waveform_id)

            # Load data from disk or network as appropriate
            if os.path.exists(mseedFile):
                LOGGER.info("Loading waveform data for %s from %s", waveform_id, mseedFile)
                st = obspy.core.read(mseedFile)
            else:
                LOGGER.info("Retrieving waveform data for %s", waveform_id)
                (network, station, location, channel) = self.waveform.SNCL.split('.')
                st = self.client.get_waveforms(network, station, location, channel, starttime, endtime)
                # Write to file
                st.write(mseedFile, format="MSEED")

            # Generate image if necessary
            imageFile = mseedFile.replace('MSEED','png')
            if not os.path.exists(imageFile):
                LOGGER.info('Plotting waveform image to %s', imageFile)
                # In order to really customize the plotting, we need to return the figure and modify it
                h = st.plot(size=(self.plot_width, self.plot_height), handle=True)
                # Resize the subplot to a hard size, because otherwise it will do it inconsistently
                h.subplots_adjust(bottom=.2, left=.1, right=.95, top=.95)
                # Remove the title
                for c in h.get_children():
                    if isinstance(c, matplotlib.text.Text):
                        c.remove()
                # Save with transparency
                h.savefig(imageFile)

            self.done.emit(WaveformResult(waveform_id, imageFile))

        except Exception as e:
            self.done.emit(WaveformResult(waveform_id, e))


class WaveformsHandler(SignalingObject):
    """
    Container for waveforms metadata.

    The contents of self.currentDF is determined by the user selections
    in the main GUI events and SNCL tables. There will be a separate
    entry in self.currentDF for each event-SNCL combination regardless
    of any filtering that is applied in the WaveformsDialog to reduce
    the size of the visible table.
    """

    progress = QtCore.pyqtSignal(object)

    def __init__(self, logger, preferences, client):
        """
        Initialization.
        """
        super(WaveformsHandler, self).__init__()

        # Keep a reference to globally shared components
        self.preferences = preferences
        self.client = client

        # Important preferences
        self.downloadDir = self.preferences.Waveforms.downloadDir

        # Queue of pending waveforms
        self.queue = collections.deque()
        # Active threads indexed by waveformID
        self.threads = {}
        # Number of threads to track
        self.num_threads = 5

        self.seconds_before = 0
        self.seconds_after = 0

        # Current state
        self.currentDF = None


    def createWaveformsDF(self, eventsDF, stationsDF):
        """
        Create a dataframe of event-SNCL combinations.
        """

        LOGGER.info('Generating event-station combined dataframe...')

        #eventsDF.columns
        #Index([u'Time', u'Magnitude', u'Longitude', u'Latitude', u'Depth/km',
               #u'MagType', u'EventLocationName', u'Author', u'Catalog', u'Contributor',
               #u'ContributorID', u'MagAuthor', u'EventID'],
              #dtype='object')
        #stationsDF.columns
        #Index([u'Network', u'Station', u'Location', u'Channel', u'Longitude',
               #u'Latitude', u'Elevation', u'Depth', u'Azimuth', u'Dip',
               #u'SensorDescription', u'Scale', u'ScaleFreq', u'ScaleUnits',
               #u'SampleRate', u'StartTime', u'EndTime', u'SNCL'],
              #dtype='object')

        # Subset eventsDF for pertinent information
        eventsDF = eventsDF[['Time','Magnitude','MagType','Depth/km','Longitude','Latitude','EventID']]
        eventsDF.columns = ['Time','Magnitude','MagType','Depth','Event_Lon','Event_Lat','EventID']

        #  Subset stationsDF for pertinent information
        stationsDF = stationsDF[['SNCL','Network','Station','Longitude','Latitude']]
        stationsDF.columns = ['SNCL','Network','Station','Station_Lon','Station_Lat']

        # For each unique SNCL, add columns of SNCL info to eventsDF
        waveformDFs = []
        for i in range(stationsDF.shape[0]):
            df = eventsDF.copy()
            df['SNCL'] = stationsDF.SNCL.iloc[i]
            df['Network'] = stationsDF.Network.iloc[i]
            df['Station'] = stationsDF.Station.iloc[i]
            df['Station_Lon'] = stationsDF.Station_Lon.iloc[i]
            df['Station_Lat'] = stationsDF.Station_Lat.iloc[i]
            waveformDFs.append(df)

        # Now combine all SNCL-specific eventsDFs
        waveformsDF = pd.concat(waveformDFs)

        # Generate an event name
        waveformsDF['EventName'] = waveformsDF.MagType + ' ' + waveformsDF.Magnitude.map(str) + ' ' + waveformsDF.Time

        # Add waveformID, and WaveformStationID
        waveformsDF['WaveformID'] = waveformsDF.SNCL + '_' + waveformsDF.EventID
        waveformsDF['WaveformStationID'] = waveformsDF.Network + '.' + waveformsDF.Station + '_' + waveformsDF.EventID

        # Set the index to integers
        waveformsDF.reset_index(drop=True, inplace=True)

        # BEGIN event-station distance -----------------------------------------

        LOGGER.debug('Calculating %d event-station distances...', len(waveformsDF.WaveformStationID.unique()))

        waveformsDF['Distance'] = np.nan
        # Now loop through all waveforms, calculating new distances only when necessary
        # NOTE:  Save time by only calculating on distance per station rather than per channel
        old_waveformStationID = None
        for i in range(waveformsDF.shape[0]):
            waveformStationID = waveformsDF.WaveformStationID.iloc[i]
            if not old_waveformStationID or waveformStationID != old_waveformStationID:
                old_waveformStationID = waveformStationID
                distance = round(locations2degrees(waveformsDF.Event_Lat.iloc[i], waveformsDF.Event_Lon.iloc[i],
                                                   waveformsDF.Station_Lat.iloc[i], waveformsDF.Station_Lon.iloc[i]),
                                 ndigits=2)
            waveformsDF.loc[i, 'Distance'] = distance

        LOGGER.debug('Finished calculating distances')

        # END event-station distance -------------------------------------------

        # Add columns to track downloads and display waveforms
        waveformsDF['Waveform'] = ""
        waveformsDF['WaveformImagePath'] = ""

        # Look to see if any have already been downloaded
        for i in range(waveformsDF.shape[0]):
            filename = "%s_%s.png" % (waveformsDF.SNCL.iloc[i], waveformsDF.Time.iloc[i])
            imagePath = os.path.join(self.downloadDir, filename)
            if os.path.exists(imagePath):
                waveformsDF.WaveformImagePath.iloc[i] = imagePath

        # Add a Keep column for checkboxes
        waveformsDF['Keep'] = True

        # Reorganize columns
        waveformsDF = waveformsDF[self.getColumnNames()]

        # Save a copy internally
        self.currentDF = waveformsDF

        return(self.currentDF)

    def clear_downloads(self):
        """
        Clear the download queue and release any active threads
        """
        LOGGER.info('Clearing existing downloads')
        #for thread in self.threads.values():
        #    thread.quit()
        # self.threads = {}
        self.queue.clear()

    def download_waveforms(self, priority_ids, other_ids, seconds_before, seconds_after):
        """
        Initiate a download of all the given waveforms
        """
        self.clear_downloads()
        LOGGER.info('Downloading waveforms')
        LOGGER.debug("Priority IDs: %s" % (priority_ids.tolist(),))
        LOGGER.debug("Other IDs: %s" % (other_ids.tolist(),))
        # Clear image path from the DF
        self.currentDF.WaveformImagePath = ''
        self.seconds_before = seconds_before
        self.seconds_after = seconds_after
        self.queue.extend(priority_ids)
        self.queue.extend(other_ids)
        for _ in range(self.num_threads):
            self.download_next_waveform()

    def download_next_waveform(self):
        """
        Start downloading the next waveform on the queue
        """
        while True:
            try:
                waveform_id = self.queue.popleft()
            except IndexError:
                LOGGER.debug("Download queue is empty")
                if len(self.threads) == 0:
                    self.done.emit(None)
                return
            try:
                self.download_waveform(waveform_id)
                return
            except Exception as e:
                LOGGER.error(e)

    def download_waveform(self, waveform_id):
        """
        Start download of a particular waveform
        """
        if waveform_id in self.threads:
            raise Exception("Already a thread downloading %s" % waveform_id)
        waveform = self.get_waveform(waveform_id)
        if waveform.empty:
            raise Exception("No such waveform %s" % waveform_id)
        if waveform.WaveformImagePath:
            raise Exception("Waveform %s already has an image" % waveform_id)
        LOGGER.debug("Spawning download thread for waveform %s", waveform_id)
        thread = WaveformLoader(self.client, waveform, self.preferences, self.seconds_before, self.seconds_after)
        thread.done.connect(self.on_downloaded)
        self.threads[waveform.WaveformID] = thread
        thread.start()

    def on_downloaded(self, result):
        LOGGER.debug("Downloaded waveform %s", result.waveform_id)
        if not isinstance(result.result, Exception):
            # Successful download, returned the path to the saved waveform image
            waveform = self.get_waveform(result.waveform_id)
            if not waveform.empty:
                LOGGER.debug("Setting image path for %s", result.waveform_id)
                self.setWaveformImagePath(result.waveform_id, result.result)
        if result.waveform_id in self.threads:
            del self.threads[result.waveform_id]
        self.progress.emit(result)
        self.download_next_waveform()

    def get_waveform(self, waveform_id):
        """
        Retrieve the Series for the given waveform
        """
        try:
            return self.currentDF[self.currentDF.WaveformID == waveform_id].iloc[0]
        except IndexError:
            return pd.Series()

    def getWaveformImagePath(self, waveformID):
        waveform = self.get_waveform(waveformID)
        if not waveform.empty:
            return waveform.WaveformImagePath
        else:
            return None

    def setWaveformImagePath(self, waveformID, imagePath):
        waveformIDs = self.currentDF.WaveformID.tolist()
        index = waveformIDs.index(waveformID)
        self.currentDF.loc[index, 'WaveformImagePath'] = imagePath
        return

    def getWaveformKeep(self, waveformID):
        waveformIDs = self.currentDF.WaveformID.tolist()
        index = waveformIDs.index(waveformID)
        keep = self.currentDF.Keep.iloc[index]
        return(keep)

    def setWaveformKeep(self, waveformID, keep):
        waveformIDs = self.currentDF.WaveformID.tolist()
        index = waveformIDs.index(waveformID)
        self.currentDF.loc[index, 'Keep'] = keep
        return

    def getColumnNames(self):
        return ['Keep', 'EventName', 'SNCL', 'Distance', 'Magnitude', 'MagType', 'Depth', 'Time', 'Waveform', 'Event_Lon', 'Event_Lat', 'EventID', 'Network', 'Station', 'Station_Lon', 'Station_Lat', 'WaveformID', 'WaveformStationID', 'WaveformImagePath']

    def getVisibleColumns(self):
        return ['Keep', 'EventName', 'Distance', 'SNCL', 'Waveform']

    def getNumericColumns(self):
        return ['Distance', 'Magnitude', 'Depth', 'Event_Lon', 'Event_Lat', 'Station_Lon', 'Station_Lat']




# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
