"""
Container for waveforms.

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

import os
from obspy import UTCDateTime
from signals import SignalingThread, SignalingObject
import collections
from PyQt4 import QtCore
import obspy
from logging import getLogger
import matplotlib
import weakref
from pyweed_utils import get_sncl, get_event_id, calculate_distances, get_event_name
from obspy.core.util.attribdict import AttribDict

LOGGER = getLogger(__name__)


class WaveformEntry(AttribDict):
    """
    Class representing an event/channel combination and the relevant waveform request
    """
    defaults = dict(
        # Weak refs to ObsPy event/channel
        event_ref=None,
        network_ref=None,
        station_ref=None,
        channel_ref=None,
        # Lazy value of calculated_distances
        distances=None,
        # Value from create_config()
        config=None,
        # Reflects user checkbox in the table
        keep=True,
        # Tracking IDs
        waveform_id=None,
        # Other labels
        sncl=None,
        event_name=None,
        # Base filename for mseed, image, etc.
        base_filename=None,
        # Full paths
        mseed_path=None,
        mseed_exists=False,
        image_path=None,
        image_exists=False,
        # Error message if unable to load
        error=None,
    )

    @classmethod
    def create_config(cls, waveform_handler):
        """
        Generate a WaveformEntry.config value from WaveformHandler
        """
        return dict(
            phase='P',
            download_dir=waveform_handler.downloadDir,
            offsets=[waveform_handler.seconds_before, waveform_handler.seconds_after]
        )

    def __init__(self, event, network, station, channel, *args, **kwargs):
        super(WaveformEntry, self).__init__(*args, **kwargs)
        self.event_ref = weakref.ref(event)
        self.network_ref = weakref.ref(network)
        self.station_ref = weakref.ref(station)
        self.channel_ref = weakref.ref(channel)

        if not self.config:
            raise Exception("No config!")

        if not self.distances:
            self.distances = calculate_distances(event, station, self.config.phase)

        self.sncl = get_sncl(network, station, channel)
        self.event_name = get_event_name(event)
        self.waveform_id = '%s_%s' % (self.sncl, get_event_id(event))

        self.update_config()

    def update_config(self, config=None):
        """
        Called with something about the config (usually the time window offsets) changes.
        Recalculates various dependent values (eg. mseed and image filenames)
        """
        if config:
            self.config = config

        self.error = None

        self.start_time = self.distances.arrival + self.config.offsets[0]
        self.end_time = self.distances.arrival + self.config.offsets[1]

        self.start_string = UTCDateTime(self.start_time).format_iris_web_service().replace(':', '_')
        self.end_string = UTCDateTime(self.end_time).format_iris_web_service().replace(':', '_')

        self.base_filename = "%s_%s_%s" % (self.sncl, self.start_string, self.end_string)
        self.mseed_path = os.path.join(self.config.download_dir, "%s.mseed" % self.base_filename)
        self.image_path = os.path.join(self.config.download_dir, "%s.png" % self.base_filename)

        self.check_files()

    def check_files(self):
        """
        See whether the backing files for this waveform exist
        """
        self.mseed_exists = os.path.exists(self.mseed_path)
        self.image_exists = os.path.exists(self.image_path)


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
    Thread to download waveform data and generate an image
    """

    def __init__(self, client, waveform, preferences):
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
        super(WaveformLoader, self).__init__()

    def run(self):
        """
        Make a webservice request for events using the passed in options.
        """
        waveform_id = self.waveform.waveform_id
        try:

            LOGGER.debug("Loading waveform: %s", waveform_id)

            mseedFile = self.waveform.mseed_path
            LOGGER.debug("%s save as MiniSEED", waveform_id)

            # Load data from disk or network as appropriate
            if os.path.exists(mseedFile):
                LOGGER.info("Loading waveform data for %s from %s", waveform_id, mseedFile)
                st = obspy.read(mseedFile)
            else:
                LOGGER.info("Retrieving waveform data for %s", waveform_id)
                (network, station, location, channel) = self.waveform.sncl.split('.')
                st = self.client.get_waveforms(
                    network, station, location, channel, self.waveform.start_string, self.waveform.end_string)
                # Write to file
                st.write(mseedFile, format="MSEED")

            # Generate image if necessary
            imageFile = self.waveform.image_path
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
            LOGGER.error("Error downloading %s: %s", waveform_id, e)
            self.done.emit(WaveformResult(waveform_id, e))


class WaveformsHandler(SignalingObject):
    """
    Manage the waveforms retrieval.

    The contents of self.waveforms is determined by the user selections
    in the main GUI events and SNCL tables. There will be a separate
    entry in self.waveforms for each event-SNCL combination regardless
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

        # Current list of waveform entries
        self.waveforms = None
        # Waveforms indexed by id
        self.waveforms_by_id = None

    def create_waveforms(self, pyweed):
        """
        Create a list of waveform entries based on the current event/station selections
        """
        self.waveforms = []
        self.waveforms_by_id = {}
        # Get the events as a list
        events = list(pyweed.iter_selected_events())

        # Need to calculate distances, we can do this per-station to save some time
        distances = {}
        # Common config for each waveform
        config = WaveformEntry.create_config(self)

        # Iterate through the stations
        for (network, station, channel) in pyweed.iter_selected_stations():
            for event in events:
                # Lazy calculate distances based on station
                event_station_id = '.'.join((network.code, station.code, get_event_id(event)))
                if event_station_id not in distances:
                    distances[event_station_id] = calculate_distances(event, station, ['ttp'])
                waveform = WaveformEntry(
                    event, network, station, channel,
                    distances=distances[event_station_id], config=config
                )
                self.waveforms.append(waveform)
                self.waveforms_by_id[waveform.waveform_id] = waveform

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
        LOGGER.debug("Priority IDs: %s" % (priority_ids,))
        LOGGER.debug("Other IDs: %s" % (other_ids,))

        self.seconds_before = seconds_before
        self.seconds_after = seconds_after
        config = WaveformEntry.create_config(self)
        for waveform in self.waveforms:
            waveform.update_config(config)
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
        if not waveform:
            raise Exception("No such waveform %s" % waveform_id)
        if waveform.image_exists:
            # No download needed, but we still want to emit the result event
            self.progress.emit(WaveformResult(waveform_id, waveform.image_path))
            raise Exception("Waveform %s already has an image" % waveform_id)
        LOGGER.debug("Spawning download thread for waveform %s", waveform_id)
        thread = WaveformLoader(self.client, waveform, self.preferences)
        thread.done.connect(self.on_downloaded)
        self.threads[waveform_id] = thread
        thread.start()

    def on_downloaded(self, result):
        LOGGER.debug("Downloaded waveform %s", result.waveform_id)
        if result.waveform_id in self.threads:
            del self.threads[result.waveform_id]
        self.progress.emit(result)
        self.download_next_waveform()

    def get_waveform(self, waveform_id):
        """
        Retrieve the Series for the given waveform
        """
        return self.waveforms_by_id.get(waveform_id)

    def getWaveformImagePath(self, waveformID):
        waveform = self.get_waveform(waveformID)
        if waveform and waveform.image_exists:
            return waveform.image_path
        else:
            return None

    def setWaveformImagePath(self, waveformID, imagePath):
        waveform = self.get_waveform(waveformID)
        if waveform:
            waveform.image_path = imagePath
            waveform.image_exists = True

    def getWaveformKeep(self, waveformID):
        waveform = self.get_waveform(waveformID)
        return (waveform and waveform.keep)

    def setWaveformKeep(self, waveformID, keep):
        waveform = self.get_waveform(waveformID)
        if waveform:
            waveform.keep = keep


# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
