#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main PyWEED application

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

# Basic packages
import os
import logging

# For debugging, raise an exception on attempted chained assignment
# See http://pandas.pydata.org/pandas-docs/version/0.19.1/indexing.html#returning-a-view-versus-a-copy
# import pandas as pd
# pd.set_option('mode.chained_assignment', 'raise')

# Pyweed UI components
from pyweed.preferences import Preferences, user_config_path
from pyweed.pyweed_utils import manageCache, iter_channels, get_sncl
from obspy.clients.fdsn import Client
from pyweed.event_options import EventOptions
from pyweed.station_options import StationOptions

LOGGER = logging.getLogger(__name__)


class NoConsoleLoggingFilter(logging.Filter):
    """
    Logging filter that excludes the (very noisy) output from the attached Python console
    """
    exclude = ('ipykernel', 'traitlets',)

    def filter(self, record):
        for exclude in self.exclude:
            if record.name.startswith(exclude):
                return False
        return True


class PyWeedCore(object):
    """
    This is intended to be the core PyWEED functionality, without any reference to the GUI layer.
    The original intent was to allow this to run independently, eg. from a script or interactive shell.
    """

    event_client = None
    event_data_center = None
    station_client = None
    station_data_center = None
    preferences = None
    event_options = None
    events = None
    selected_event_ids = None
    station_options = None
    stations = None
    selected_station_ids = None

    def __init__(self):
        super(PyWeedCore, self).__init__()
        self.configure_logging()
        self.event_options = EventOptions()
        self.station_options = StationOptions()
        self.load_preferences()
        self.manage_cache()

    def set_event_data_center(self, data_center):
        if data_center != self.event_data_center or not self.event_client:
            # Use the station client if they're the same, otherwise create a client
            if data_center == self.station_data_center and self.station_client:
                client = self.station_client
            else:
                LOGGER.info("Creating ObsPy client for %s", data_center)
                client = Client(data_center)
            # Verify that this client supports events
            if 'event' not in client.services:
                LOGGER.error("The %s data center does not provide an event service" % data_center)
                return
            # Update settings
            self.event_data_center = data_center
            self.event_client = client

    def set_station_data_center(self, data_center):
        if data_center != self.station_data_center or not self.station_client:
            # Use the station client if they're the same, otherwise create a client
            if data_center == self.event_data_center and self.event_client:
                client = self.event_client
            else:
                LOGGER.info("Creating ObsPy client for %s", data_center)
                client = Client(data_center)
            # Verify that this client supports station and dataselect
            for service in ('station', 'dataselect',):
                if service not in client.services:
                    LOGGER.error("The %s data center does not provide a %s service" % (data_center, service))
                    return
            # Update settings
            self.station_data_center = data_center
            self.station_client = client

    def load_preferences(self):
        """
        Load configurable preferences from ~/.pyweed/config.ini
        """
        LOGGER.info("Loading preferences")
        self.preferences = Preferences()
        try:
            self.preferences.load()
        except Exception as e:
            LOGGER.error("Unable to load configuration preferences -- using defaults.\n%s", e)
        self.set_event_options(self.preferences.EventOptions)
        self.set_event_data_center(self.preferences.Data.eventDataCenter)
        self.set_station_options(self.preferences.StationOptions)
        self.set_station_data_center(self.preferences.Data.stationDataCenter)

    def save_preferences(self):
        """
        Save preferences to ~/.pyweed/config.ini
        """
        LOGGER.info("Saving preferences")
        try:
            self.preferences.EventOptions.update(self.event_options.get_options(stringify=True))
            self.preferences.StationOptions.update(self.station_options.get_options(stringify=True))
            self.preferences.save()
        except Exception as e:
            LOGGER.error("Unable to save configuration preferences: %s", e)

    def configure_logging(self):
        """
        Configure the root logger
        """
        logger = logging.getLogger()
        try:
            log_level = getattr(logging, self.preferences.Logging.level)
            logger.setLevel(log_level)
        except Exception:
            logger.setLevel(logging.DEBUG)
        # Log to the terminal if available, otherwise log to a file
        if False:
            # Log to stderr
            handler = logging.StreamHandler()
        else:
            log_file = os.path.join(user_config_path(), 'pyweed.log')
            handler = logging.FileHandler(log_file, mode='w')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        handler.addFilter(NoConsoleLoggingFilter())
        logger.addHandler(handler)
        LOGGER.info("Logging configured")

    def manage_cache(self, init=True):
        """
        Make sure the waveform download directory exists and isn't full
        """
        download_path = self.preferences.Waveforms.downloadDir
        cache_size = int(self.preferences.Waveforms.cacheSize)
        LOGGER.info('Checking on download directory...')
        if os.path.exists(download_path):
            manageCache(download_path, cache_size)
        elif init:
            try:
                os.makedirs(download_path, 0o700)
            except Exception as e:
                LOGGER.error("Creation of download directory failed with" + " error: \"%s\'""" % e)
                raise

    def set_event_options(self, options):
        """
        Update the event options
        """
        LOGGER.debug("Set event options: %s", repr(options))
        self.event_options.set_options(options)

    def get_event_obspy_options(self):
        """
        Get the options for making an event request from Obspy
        """
        return self.event_options.get_obspy_options()

    def fetch_events(self, options=None):
        """
        NOT THREAD SAFE: The GUI subclass should override this
        """
        if not options:
            options = self.get_event_obspy_options()
        self.set_events(self.event_client.get_events(**options))

    def set_events(self, events):
        """
        Set the current event list

        @param events: a Catalog
        """
        LOGGER.info("Set events")
        self.events = events

    def set_selected_event_ids(self, event_ids):
        self.selected_event_ids = event_ids

    def iter_selected_events(self):
        """
        Iterate over the selected events
        """
        for event in self.events:
            event_id = event.resource_id.id
            if event_id in self.selected_event_ids:
                yield event

    def set_station_options(self, options):
        LOGGER.debug("Set station options: %s", repr(options))
        self.station_options.set_options(options)

    def get_station_obspy_options(self):
        """
        Get the options for making an event request from Obspy
        """
        return self.station_options.get_obspy_options()

    def fetch_stations(self, options=None):
        """
        NOT THREAD SAFE: The GUI subclass should override this
        """
        if not options:
            options = self.get_station_obspy_options()
        self.set_stations(self.station_client.get_stations(**options))

    def set_stations(self, stations):
        """
        Set the current station list

        @param stations: an Inventory
        """
        LOGGER.info("Set stations")
        self.stations = stations

    def set_selected_station_ids(self, station_ids):
        self.selected_station_ids = station_ids

    def iter_selected_stations(self):
        """
        Iterate over the selected stations (channels)
        Yields (network, station, channel) for each selected channel
        """
        for (network, station, channel) in iter_channels(self.stations):
            sncl = get_sncl(network, station, channel)
            if sncl in self.selected_station_ids:
                yield (network, station, channel)

    def close(self):
        self.manage_cache(init=False)
        self.save_preferences()


if __name__ == "__main__":
    pyweed = PyWeedCore()
    # Do something?
