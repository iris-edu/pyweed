# -*- coding: utf-8 -*-
"""
Application preferences

Adapted from: https://github.com/claysmith/oldArcD/blob/master/tools/arctographer/arcmap/preferences.py

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

import os
import platform
from future.moves.configparser import SafeConfigParser


def safe_bool(s, default=False):
    try:
        return s.startswith('y')
    except:
        return default


def bool_to_str(b):
    if b:
        return "y"
    else:
        return "n"


def safe_int(s, default=0):
    try:
        return int(s)
    except:
        return default


class Section(object):
    def __init__(self, **initial):
        self.__dict__.update(initial)

    def read_from_config(self, config):
        name = self.__name__
        if config.has_section(name):
            fix_case = dict((k.lower(), k) for k in self.__dict__.keys())
            for k, v in config.items(name):
                if k in fix_case:
                    k = fix_case[k]
                self.__dict__[k] = v

    def write_to_config(self, config):
        name = self.__name__
        config.add_section(name)
        for key, value in self.items():
            config.set(name, key, str(value))

    @property
    def __name__(self):
        return self.__class__.__name__

    def items(self):
        return self.__dict__.items()

    def update(self, values):
        self.__dict__.update(values)

    def __repr__(self):
        return self.__dict__.__repr__()

    @classmethod
    def create(cls, section_name, **initial):
        return type(section_name, (cls,), {})(**initial)


class Preferences(object):
    """
    Container for application preferences.
    """

    def __init__(self):
        """
        Initialization with default settings.
        """

#         for (section, prefs) in DEFAULTS.items():
#             setattr(self, section, Section.create(section, **prefs))

        self.Data = Section.create("Data")
        self.Data.eventDataCenter = "IRIS"
        self.Data.stationDataCenter = "IRIS"

        self.Waveforms = Section.create("Waveforms")
        self.Waveforms.downloadDir = user_download_path()
        self.Waveforms.cacheSize = "50"  # megabytes
        self.Waveforms.saveDir = user_save_path()
        self.Waveforms.timeWindowBefore = "60"  # seconds
        self.Waveforms.timeWindowBeforePhase = "P"  # P|S|Event
        self.Waveforms.timeWindowAfter = "600"  # seconds
        self.Waveforms.timeWindowAfterPhase = "P"  # P|S|Event
        self.Waveforms.saveFormat = "MSEED"

        self.Logging = Section.create("Logging")
        self.Logging.level = "DEBUG"

        self.Map = Section.create("Map")

        self.MainWindow = Section.create("MainWindow")
        self.MainWindow.width = "1000"
        self.MainWindow.height = "800"
        self.MainWindow.eventOptionsFloat = "n"
        self.MainWindow.stationOptionsFloat = "n"

        self.EventOptions = Section.create("EventOptions")

        self.StationOptions = Section.create("StationOptions")

    def save(self):
        """
        Saves the user's preferences to config file
        """
        config = SafeConfigParser()

        sections = [
            self.Data,
            self.Waveforms,
            self.Logging,
            self.Map,
            self.MainWindow,
            self.EventOptions,
            self.StationOptions,
        ]
        for section in sections:
            section.write_to_config(config)

        if not os.path.exists(user_config_path()):
            try:
                os.makedirs(user_config_path(), 0o700)
            except Exception as e:
                print("Creation of user configuration directory failed with" + " error: \"%s\'""" % e)
                return
        f = open(os.path.join(user_config_path(), "pyweed.ini"), "w")
        config.write(f)

    def load(self):
        """
        Loads the user's preferences from saved config file
        '"""
        path = os.path.join(user_config_path(), "pyweed.ini")

        if not os.path.exists(path):
            # Save the default configuration info
            self.save()

        else:
            # Override defaults with anything found in config.ini
            f = open(path, "r")
            config = SafeConfigParser()
            config.readfp(f)

            sections = [
                self.Data,
                self.Waveforms,
                self.Logging,
                self.Map,
                self.MainWindow,
                self.EventOptions,
                self.StationOptions,
            ]
            for section in sections:
                section.read_from_config(config)


# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------

def user_config_path(safe=True):
    """
    @param safe: If set, auto-create the path if it doesn't exist
    @rtype: str
    @return: the directory for storing user configuration files
    """
    p = os.path.join(os.path.expanduser("~"), ".pyweed")
    if safe:
        os.makedirs(p, exist_ok=True)
    return p
#     if platform.system() == "Darwin":
#         return os.path.join(os.path.expanduser("~"), "Library", "Preferences")
#     elif platform.system() == "Windows":
#         return os.path.join(os.path.expanduser("~"), "AppData", "Local")
#     else:
#         # Assume a Linux-like system
#         return os.path.join(os.path.expanduser("~"), ".config")


def user_download_path(safe=True):
    """
    @param safe: If set, auto-create the path if it doesn't exist
    @rtype: str
    @return: the default directory for saving downloaded (previewed) waveform data
    """
    p = os.path.join(os.path.expanduser("~"), ".pyweed", "data")
    if safe:
        os.makedirs(p, exist_ok=True)
    return p
#     if platform.system() == "Darwin":
#         return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "pyweed_data")
#     elif platform.system() == "Windows":
#         return os.path.join(os.path.expanduser("~"), "AppData", "Local", "pyweed_data")
#     else:
#         # Assume a Linux-like system
#         return os.path.join(os.path.expanduser("~"), ".config", "pyweed_data")


def user_save_path(safe=False):
    """
    @param safe: If set, auto-create the path if it doesn't exist
    @rtype: str
    @return: the default directory for saving waveform files
    """
    p = os.path.join(os.path.expanduser("~"), "Downloads", "pyweed")
    if safe:
        os.makedirs(p, exist_ok=True)
    return p
#     if platform.system() == "Darwin":
#         return os.path.join(os.path.expanduser("~"), "Downloads", "pyweed")
#     elif platform.system() == "Windows":
#         return os.path.join(os.path.expanduser("~"), "Documents", "pyweed")
#     else:
#         # Assume a Linux-like system
#         return os.path.join(os.path.expanduser("~"), "Downloads", "pyweed")


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
