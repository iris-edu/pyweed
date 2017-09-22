# -*- coding: utf-8 -*-
"""
Station Options

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from pyweed.options import Options, DateOption, FloatOption, Option
import copy
from pyweed.dist_from_events import get_combined_locations, CrossBorderException
from pyweed.pyweed_utils import get_preferred_origin
from logging import getLogger

LOGGER = getLogger(__name__)


class StationOptions(Options):

    TIME_RANGE = 'timeBetween'
    TIME_EVENTS = 'timeFromEvents'
    time_choice = Option(hidden=True, default=TIME_RANGE)

    starttime = DateOption(default=-30)
    endtime = DateOption(default=0)

    network = Option(default="_GSN")
    station = Option(default="*")
    location = Option(default="*")
    channel = Option(default="?HZ")

    LOCATION_GLOBAL = 'locationGlobal'
    LOCATION_BOX = 'locationRange'
    LOCATION_POINT = 'locationDistanceFromPoint'
    LOCATION_EVENTS = 'locationDistanceFromEvents'
    location_choice = Option(hidden=True, default=LOCATION_GLOBAL)

    minlatitude = FloatOption(default=-90)
    maxlatitude = FloatOption(default=90)
    minlongitude = FloatOption(default=-180)
    maxlongitude = FloatOption(default=180)

    latitude = FloatOption()
    longitude = FloatOption()
    minradius = FloatOption()
    maxradius = FloatOption(default=30)

    # Special settings indicating the location is based on distance from selected events
    mindistance = FloatOption(hidden=True)
    maxdistance = FloatOption(hidden=True)

    event_locations = None

    def get_time_options(self):
        if self.time_choice == self.TIME_RANGE:
            return self.get_options(['starttime', 'endtime'])
        else:
            return {}

    def get_location_options(self):
        if self.location_choice == self.LOCATION_BOX:
            return self.get_options(['minlatitude', 'maxlatitude', 'minlongitude', 'maxlongitude'])
        elif self.location_choice == self.LOCATION_POINT:
            return self.get_options(['latitude', 'longitude', 'minradius', 'maxradius'])
        else:
            return {}

    def get_obspy_options(self):
        base_keys = ['network', 'station', 'location', 'channel']
        options = self.get_options(keys=base_keys)
        # Default level is 'station' but we always(?) want 'channel'
        options['level'] = 'channel'
        options.update(self.get_time_options())
        options.update(self.get_location_options())
        return options

    def get_event_distances(self):
        """
        If this is a event-based query, return those settings
        Note that this isn't part of the Obspy query!
        """
        if self.location_choice == self.LOCATION_EVENTS:
            return self.get_options(['mindistance', 'maxdistance'])
        else:
            return {}

    def filter_result(self, inventory):
        """
        After a request, filter the results if necessary
        """
        # Only handle filters based on event locations
        if self.location_choice == self.LOCATION_EVENTS and self.event_locations:
            pass


