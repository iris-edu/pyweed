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
import sys
import logging

# For debugging, raise an exception on attempted chained assignment
# See http://pandas.pydata.org/pandas-docs/version/0.19.1/indexing.html#returning-a-view-versus-a-copy
import pandas as pd
pd.set_option('mode.chained_assignment', 'raise')

# Pyweed UI components
from preferences import Preferences
from pyweed_utils import manageCache
from obspy.clients import fdsn
from events import EventOptions


__appName__ = "PyWEED"
__version__ = "0.1.1"


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

    client = None
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
        self.station_options = {}
        self.load_preferences()
        self.manage_cache()

        # Instantiate a client
        LOGGER.info("Creating ObsPy client for %s", self.preferences.Data.dataCenter)
        self.client = fdsn.Client(self.preferences.Data.dataCenter)

    def load_preferences(self):
        # Load configurable preferences from ~/.pyweed/config.ini
        LOGGER.info("Loading preferences")
        self.preferences = Preferences()
        try:
            self.preferences.load()
            self.event_options.set_options(self.preferences.EventOptions)
        except Exception as e:
            LOGGER.error("Unable to load configuration preferences -- using defaults.\n%s", e)

    def save_preferences(self):
        LOGGER.info("Saving preferences")
        try:
            self.preferences.EventOptions.update(self.event_options.get_options(stringify=True))
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
        except Exception as e:
            logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
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
        self.event_options.set_options(options)

    def fetch_events(self, options=None):
        raise NotImplementedError("PyWEED subclass should implement this")

    def set_events(self, events):
        LOGGER.info("Set events")
        self.events = events

    def set_selected_event_ids(self, event_ids):
        self.selected_event_ids = event_ids

    def set_station_options(self, options):
        self.station_options = options

    def fetch_stations(self, options=None):
        raise NotImplementedError("PyWEED subclass should implement this")

    def set_stations(self, stations):
        LOGGER.info("Set stations")
        self.stations = stations

    def set_selected_station_ids(self, station_ids):
        self.selected_station_ids = station_ids

    def close(self):
        self.manage_cache(init=False)
        self.save_preferences()


if __name__ == "__main__":
    pyweed = PyWeed()
    # Do something?

