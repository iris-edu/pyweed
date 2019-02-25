# -*- coding: utf-8 -*-
"""
Container for waveforms.

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

import os
from obspy import UTCDateTime
from pyweed.signals import SignalingThread, SignalingObject
import collections
from PyQt5 import QtCore, QtGui
import obspy
from logging import getLogger
import matplotlib
import weakref
from pyweed.pyweed_utils import get_sncl, get_event_id, TimeWindow,\
    get_preferred_origin, get_preferred_magnitude, OUTPUT_FORMAT_EXTENSIONS,\
    get_event_description, get_arrivals, format_time_str, get_distance, get_service_url, CancelledException
from obspy.core.util.attribdict import AttribDict
from obspy.io.sac.sactrace import SACTrace
from obspy.core.stream import Stream
import concurrent.futures

LOGGER = getLogger(__name__)

THREAD_POOL_SIZE = 10


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
        # Distance from event to station
        distance=None,
        # Phase arrivals
        arrivals=None,
        # Timing information
        event_time=None,
        start_time=None,
        end_time=None,
        start_string=None,
        end_string=None,
        # Reflects user checkbox in the table
        keep=True,
        # Tracking IDs
        waveform_id=None,
        # Other table display values
        sncl=None,
        event_time_str=None,
        event_description=None,
        event_mag=None,
        event_mag_value=None,
        event_depth=None,
        # Base directory to download files to (from WaveformsHandler)
        download_dir=None,
        # Time window settings (from WaveformHandler)
        time_window=None,
        # Base filename for mseed, image, etc.
        base_filename=None,
        # Full paths
        mseed_path=None,
        mseed_exists=False,
        image_path=None,
        image_exists=False,
        # Loading indicator
        loading=False,
        # Error message if unable to load
        error=None,
    )

    def __init__(self, event, network, station, channel, *args, **kwargs):
        super(WaveformEntry, self).__init__(*args, **kwargs)

        self.event_ref = weakref.ref(event)
        self.network_ref = weakref.ref(network)
        self.station_ref = weakref.ref(station)
        self.channel_ref = weakref.ref(channel)

        self.sncl = get_sncl(network, station, channel)

        self.event_description = get_event_description(event)
        origin = get_preferred_origin(event)
        self.event_time = origin.time
        self.event_time_str = format_time_str(origin.time)
        self.event_depth = origin.depth / 1000
        mag = get_preferred_magnitude(event)
        self.event_mag = "%s%s" % (mag.mag, mag.magnitude_type)
        self.event_mag_value = mag.mag
        self.waveform_id = '%s_%s' % (self.sncl, get_event_id(event))

        self.distance = get_distance(
            origin.latitude, origin.longitude,
            station.latitude, station.longitude)

    def update_handler_values(self, waveform_handler):
        """
        Update any values that come from the WaveformHander
        """
        self.download_dir = waveform_handler.downloadDir
        self.time_window = waveform_handler.time_window

    def prepare(self):
        """
        Calculate (or recalculate) values in preparation for doing work
        """
        if not self.arrivals:
            self.arrivals = get_arrivals(self.distance, self.event_depth)

        (self.start_time, self.end_time) = self.time_window.calculate_window(
            self.event_time, self.arrivals)
        self.start_string = UTCDateTime(self.start_time).format_iris_web_service().replace(':', '_')
        self.end_string = UTCDateTime(self.end_time).format_iris_web_service().replace(':', '_')

        self.base_filename = "%s_%s_%s" % (self.sncl, self.start_string, self.end_string)
        self.mseed_path = os.path.join(self.download_dir, "%s.mseed" % self.base_filename)
        self.image_path = os.path.join(self.download_dir, "%s.png" % self.base_filename)

        self.check_files()

    def check_files(self):
        """
        After calculating the paths for downloaded files, check to see if they're already there
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


def load_waveform(client, waveform):
    """
    Download the given waveform data and generate an image. This is a standalone function so we can
    run it in a separate thread. This modifies the waveform entry and returns a dummy value, or
    raises an exception on any error.
    """
    plot_width = 600
    plot_height = 120

    waveform_id = waveform.waveform_id
    LOGGER.debug("Loading waveform: %s (%s)", waveform_id, QtCore.QThread.currentThreadId())
#     LOGGER.debug("Adding slowness")
#     QtCore.QThread.currentThread().sleep(2)

    try:
        waveform.prepare()

        if waveform.image_exists:
            # No download needed
            LOGGER.info("Waveform %s already has an image" % waveform_id)
            return True

        mseedFile = waveform.mseed_path
        LOGGER.debug("%s save as MiniSEED", waveform_id)

        # Load data from disk or network as appropriate
        if os.path.exists(mseedFile):
            LOGGER.info("Loading waveform data for %s from %s", waveform_id, mseedFile)
            st = obspy.read(mseedFile)
        else:
            (network, station, location, channel) = waveform.sncl.split('.')
            service_url = get_service_url(client, 'dataselect', {
                "network": network, "station": station, "location": location, "channel": channel,
                "starttime": waveform.start_time, "endtime": waveform.end_time,
            })
            LOGGER.info("Retrieving waveform data for %s from %s", waveform_id, service_url)
            st = client.get_waveforms(
                network, station, location, channel, waveform.start_string, waveform.end_string)
            # Write to file
            st.write(mseedFile, format="MSEED")

        # Generate image if necessary
        imageFile = waveform.image_path
        if not os.path.exists(imageFile):
            LOGGER.debug('Plotting waveform image to %s', imageFile)
            # In order to really customize the plotting, we need to return the figure and modify it
            h = st.plot(size=(plot_width, plot_height), handle=True)
            # Resize the subplot to a hard size, because otherwise it will do it inconsistently
            h.subplots_adjust(bottom=.2, left=.1, right=.95, top=.95)
            # Remove the title
            for c in h.get_children():
                if isinstance(c, matplotlib.text.Text):
                    c.remove()
            # Save with transparency
            h.savefig(imageFile)
            matplotlib.pyplot.close(h)

        waveform.check_files()

    except Exception as e:
        # Most common error is "no data" TODO: see https://github.com/obspy/obspy/issues/1656
        if str(e).startswith("No data"):
            waveform.error = "No data available"
        else:
            waveform.error = str(e)
        # Reraise the exception to signal an error to the caller
        raise

    finally:
        # Mark as finished loading
        waveform.loading = False

    return True


class WaveformsLoader(SignalingThread):
    """
    Thread to download waveform data and generate an image
    """
    progress = QtCore.pyqtSignal(object)

    def __init__(self, client, waveforms):
        """
        Initialization.
        """
        # Keep a reference to globally shared components
        self.client = client
        self.waveforms = waveforms
        self.futures = {}
        super(WaveformsLoader, self).__init__()

    def run(self):
        """
        Make a webservice request for events using the passed in options.
        """
        self.setPriority(QtCore.QThread.LowestPriority)
        self.clearFutures()
        self.futures = {}
        with concurrent.futures.ThreadPoolExecutor(THREAD_POOL_SIZE) as executor:
            for waveform in self.waveforms:
                # Dictionary to look up the waveform id by Future
                self.futures[executor.submit(load_waveform, self.client, waveform)] = waveform.waveform_id
            # Iterate through Futures as they complete
            for result in concurrent.futures.as_completed(self.futures):
                waveform_id = self.futures.get(result)
                if waveform_id:
                    LOGGER.debug("Loader finished: %s", waveform_id)
                    try:
                        self.progress.emit(WaveformResult(waveform_id, result.result()))
                    except Exception as e:
                        self.progress.emit(WaveformResult(waveform_id, e))
        self.futures = {}
        self.done.emit(None)

    def clearFutures(self):
        """
        Cancel any outstanding tasks
        """
        if self.futures:
            for future in self.futures:
                if not future.done():
                    LOGGER.debug("Cancelling unexecuted future")
                    future.cancel()

    def cancel(self):
        """
        User-requested cancel
        """
        self.done.disconnect()
        self.progress.disconnect()
        self.clearFutures()


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

        # Loader component
        self.waveforms_loader = None
        # Thread to run the loader in
        self.thread = None
        # Asynchronous requests, each is working to download a single waveform
        self.requests = None

        # A TimeWindow object giving offsets and phase arrivals
        self.time_window = TimeWindow()

        # Current list of waveform entries
        self.waveforms = None
        # Waveforms indexed by id
        self.waveforms_by_id = None

    def create_waveforms(self, pyweed):
        """
        Create a list of waveform entries based on the current event/station selections
        """
        self.waveforms = [
            WaveformEntry(
                event, network, station, channel
            )
            for (event, network, station, channel) in pyweed.iter_selected_events_stations()
        ]
        self.waveforms_by_id = dict(
            (waveform.waveform_id, waveform)
            for waveform in self.waveforms
        )

    def cancel_download(self):
        """
        Cancel the loader if it's running
        """
        LOGGER.debug('Cancelling existing downloads')
        if self.waveforms_loader:
            self.waveforms_loader.cancel()
        # Mark all the waveforms that are still marked as loading
        for waveform in self.waveforms:
            if waveform.loading:
                waveform.loading = False
                waveform.error = "Cancelled download"
                LOGGER.debug("Manually marking %s as cancelled", waveform.waveform_id)
                self.progress.emit(WaveformResult(waveform.waveform_id, None))
        self.done.emit(CancelledException())

    def download_waveforms(self, priority_ids, other_ids, time_window):
        """
        Initiate a download of all the given waveforms
        """
        LOGGER.info('Downloading waveforms')
        LOGGER.debug("Priority IDs: %s" % (priority_ids,))
        LOGGER.debug("Other IDs: %s" % (other_ids,))

        # Prepare the waveform entries
        self.time_window = time_window
        for waveform in self.waveforms:
            waveform.update_handler_values(self)
            # Clear error flag and set loading flag
            waveform.error = None
            waveform.loading = True

        # Get the waveforms ordered by priority
        waveform_ids = list(priority_ids) + list(other_ids)
        waveforms = [self.get_waveform(waveform_id) for waveform_id in waveform_ids]

        # Create a worker to load the data in a separate thread
        self.waveforms_loader = WaveformsLoader(self.client, waveforms)
        self.waveforms_loader.progress.connect(self.on_downloaded)
        self.waveforms_loader.done.connect(self.on_all_downloaded)
        self.waveforms_loader.start()

    def on_downloaded(self, result):
        """
        Called for each downloaded waveform.

        :param result: a `WaveformResult`
        """
        # LOGGER.debug("Downloaded waveform %s (%s)", result.waveform_id, QtCore.QThread.currentThreadId())
        self.progress.emit(result)

    def on_all_downloaded(self, result):
        LOGGER.debug("All waveforms downloaded  (%s)", QtCore.QThread.currentThreadId())
        if self.waveforms_loader:
            self.waveforms_loader.quit()
            self.waveforms_loader.wait()
            LOGGER.debug("Download thread exited")
        self.done.emit(result)

    def get_waveform(self, waveform_id):
        """
        Retrieve the Series for the given waveform
        """
        return self.waveforms_by_id.get(waveform_id)

    def save_waveforms_iter(self, base_output_path, output_format, waveforms):
        """
        Save waveforms, returning an iterator of WaveformResult objects whose values are
        True (saved), False (already saved), or Exception (error)
        This is so the GUI layer can handle save progress and errors in its own fashion
        """
        if not os.path.exists(base_output_path):
            try:
                os.makedirs(base_output_path, 0o700)
            except Exception as e:
                raise Exception("Could not create the output path: %s" % str(e))

        # Get the file extension to use
        extension = OUTPUT_FORMAT_EXTENSIONS[output_format]

        for waveform in waveforms:
            waveform_id = waveform.waveform_id
            try:
                output_file = os.path.extsep.join((waveform.base_filename, extension))
                output_path = os.path.join(base_output_path, output_file)
                # Don't repeat any work that has already been done
                if not os.path.exists(output_path):
                    LOGGER.debug('reading %s', waveform.mseed_path)
                    st = obspy.read(waveform.mseed_path)
                    self.save_waveform(st, output_path, output_format, waveform)
                    yield WaveformResult(waveform_id, True)
                else:
                    yield WaveformResult(waveform_id, False)
            except Exception as e:
                yield WaveformResult(waveform_id, e)

    def save_waveform(self, st, output_path, output_format, waveform):
        """
        Save a single waveform. This should handle any special output features (eg. SAC metadata)
        """
        LOGGER.debug('writing %s', output_path)
        if output_format in ('SAC', 'SACXY',):
            # For SAC output, we need to pull header data from the waveform record
            st = self.to_sac_stream(st, waveform)
        st.write(output_path, format=output_format)

    def to_sac_stream(self, st, waveform):
        """
        Return a SACTrace based on the given stream, containing metadata headers from the waveform
        """
        tr = SACTrace.from_obspy_trace(st[0])
        tr.kevnm = waveform.event_description[:16]
        event = waveform.event_ref()
        if not event:
            LOGGER.warn("Lost reference to event %s", waveform.event_description)
        else:
            origin = get_preferred_origin(waveform.event_ref())
            if origin:
                tr.evla = origin.latitude
                tr.evlo = origin.longitude
                tr.evdp = origin.depth / 1000
                tr.o = origin.time - waveform.start_time
            magnitude = get_preferred_magnitude(waveform.event_ref())
            if magnitude:
                tr.mag = magnitude.mag
        channel = waveform.channel_ref()
        if not channel:
            LOGGER.warn("Lost reference to channel %s", waveform.sncl)
        else:
            tr.stla = channel.latitude
            tr.stlo = channel.longitude
            tr.stdp = channel.depth
            tr.stel = channel.elevation
            tr.cmpaz = channel.azimuth
            tr.cmpinc = channel.dip + 90
            tr.kinst = channel.sensor.description[:8]
        return Stream([tr.to_obspy_trace()])


# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
