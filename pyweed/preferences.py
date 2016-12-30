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
import ConfigParser

__appName__ = "PyWEED"
__version__ = "0.1.1"


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

        self.App = Section.create("App")
        self.App.name = __appName__
        self.App.version = __version__

        self.Data = Section.create("Data")
        self.Data.dataCenter = "IRIS"

        self.Waveforms = Section.create("Waveforms")
        self.Waveforms.downloadDir = os.path.join(os.path.expanduser("~"), ".pyweed_downloads")
        self.Waveforms.cacheSize = "50" # megabytes

        self.Logging = Section.create("Logging")
        self.Logging.level = "DEBUG"

        self.Map = Section.create("Map")
        self.Map.projection = "robin"

        self.EventOptions = Section.create("EventOptions")
        self.EventOptions.minmag = "5.0"
        self.EventOptions.maxmag = "10.0"
        self.EventOptions.mindepth = "0.0"
        self.EventOptions.maxdepth = "6731.0"
        self.EventOptions.minlongitude = "-180.0"
        self.EventOptions.maxlongitude = "180.0"
        self.EventOptions.minlatitude = "-90.0"
        self.EventOptions.maxlatitude = "90.0"
        self.EventOptions.minradius = "0"
        self.EventOptions.maxradius = "30"
        self.EventOptions.longitude = "0"
        self.EventOptions.latitude = "0"
        self.EventOptions.time_choice = 'timeBetweenRadioButton' # or 'timeDuringStationsRadioButton'
        self.EventOptions.location_choice = 'locationRangeRadioButton' # or 'locationDistanceFromPointRadioButton' or 'locationDistanceFromStationsRadioButton'

        self.StationOptions = Section.create("StationOptions")
        self.StationOptions.network = "_GSN"
        self.StationOptions.station = "*"
        self.StationOptions.location = "*"
        self.StationOptions.channel = "?HZ"
        self.StationOptions.locationRangeWest = "-180"
        self.StationOptions.locationRangeEast = "180"
        self.StationOptions.locationRangeSouth = "-90"
        self.StationOptions.locationRangeNorth = "90"
        self.StationOptions.distanceFromPointMinRadius = "0"
        self.StationOptions.distanceFromPointMaxRadius = "30"
        self.StationOptions.distanceFromPointEast = "0"
        self.StationOptions.distanceFromPointNorth = "0"
        self.StationOptions.selectedTimeButton = 'timeBetweenRadioButton' # or 'timeDuringEventsRadioButton'
        self.StationOptions.selectedLocationButton = 'locationRangeRadioButton' # or 'locationDistanceFromPointRadioButton' or 'locationDistanceFromEventsRadioButton'

    def save(self):
        """
        Saves the user's preferences to ~/.pyweed/config.ini
        """
        config = ConfigParser.SafeConfigParser()

        sections = [
            self.Waveforms,
            self.Logging,
            self.Map,
            self.EventOptions,
            self.StationOptions,
        ]
        for section in sections:
            section.write_to_config(config)

        if not os.path.exists(user_config_path()):
            try:
                os.makedirs(user_config_path(), 0700)
            except Exception as e:
                print("Creation of user configuration directory failed with" + " error: \"%s\'""" % e)
                return
        f = open(os.path.join(user_config_path(), "config.ini"), "w")
        config.write(f)


    def load(self):
        """
        Loads the user's preferences from ~/.pyweed/config.ini
        '"""
        path = os.path.join(user_config_path(), "config.ini")

        if not os.path.exists(path):
            # Save the default configuration info
            try:
                self.save()
            except Exception as e:
                raise

        else:
            # Override defaults with anything found in config.ini
            f = open(path, "r")
            config = ConfigParser.SafeConfigParser()
            config.readfp(f)

            sections = [
                self.Waveforms,
                self.Logging,
                self.Map,
                self.EventOptions,
                self.StationOptions,
            ]
            for section in sections:
                section.read_from_config(config)


# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------


def user_config_path():
    """
    Option to support different paths for different operatiing systems.

    Adapted from:  https://github.com/claysmith/oldArcD/blob/master/tools/arctographer/arcmap/datafiles.py

    @rtype: str
    @return: the directory for storing user configuration files
    """
    if platform.system() == "Darwin":
        path = os.path.join(os.path.expanduser("~"), ".pyweed")
        return(path)
    #elif platform.system() == "Linux":
        #path = os.path.join(os.path.expanduser("~"), ".config", "pyweed")
        #return path
    #elif platform.system() == "Windows":
        #path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "pyweed")
        #return path
    else:
        raise Exception("Unsupported operating system")


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
