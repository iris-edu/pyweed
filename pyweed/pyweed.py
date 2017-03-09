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
from preferences import Preferences
from pyweed_utils import manageCache, iter_channels, get_sncl
from obspy.clients.fdsn import Client
from event_options import EventOptions
from station_options import StationOptions


__app_name__ = "PyWEED"
__app_version__ = "0.1.1"


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


class PyWeed(object):

    app_name = __app_name__
    app_version = __app_version__

    client = None
    data_center = None
    preferences = None
    event_options = None
    events = None
    selected_event_ids = None
    station_options = None
    stations = None
    selected_station_ids = None

    def __init__(self):
        super(PyWeed, self).__init__()
        self.configure_logging()
        self.event_options = EventOptions()
        self.station_options = StationOptions()
        self.load_preferences()
        self.manage_cache()

    def set_data_center(self, data_center):
        # Instantiate a client
        self.data_center = data_center
        LOGGER.info("Creating ObsPy client for %s", self.data_center)
        self.client = Client(self.data_center)

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
        self.set_station_options(self.preferences.StationOptions)
        self.set_data_center(self.preferences.Data.dataCenter)

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
        handler = logging.StreamHandler()
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
        cache_size = float(self.preferences.Waveforms.cacheSize)
        LOGGER.info('Checking on download directory...')
        if os.path.exists(download_path):
            manageCache(download_path, cache_size)
        elif init:
            try:
                os.makedirs(download_path, 0700)
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
        return self.event_options.get_obspy_options(self.station_options)

    def fetch_events(self, options=None):
        """
        NOT THREAD SAFE: The GUI subclass should override this
        """
        if not options:
            options = self.get_event_obspy_options()
        self.set_events(self.client.get_events(**options))

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
        return self.station_options.get_obspy_options(self.event_options)

    def fetch_stations(self, options=None):
        """
        NOT THREAD SAFE: The GUI subclass should override this
        """
        if not options:
            options = self.get_station_obspy_options()
        self.set_stations(self.client.get_stations(**options))

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
    pyweed = PyWeed()
    # Do something?
