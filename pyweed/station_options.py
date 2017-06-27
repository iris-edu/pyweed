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


class StationOptions(Options):

    time_choice = Option(hidden=True)
    TIME_RANGE = 'timeBetween'
    TIME_EVENTS = 'timeFromEvents'

    starttime = DateOption(default=-30)
    endtime = DateOption(default=0)

    network = Option(default="_GSN")
    station = Option(default="*")
    location = Option(default="*")
    channel = Option(default="?HZ")

    location_choice = Option(hidden=True)
    LOCATION_GLOBAL = 'locationGlobal'
    LOCATION_BOX = 'locationRange'
    LOCATION_POINT = 'locationDistanceFromPoint'
    LOCATION_EVENTS = 'locationFromEvents'

    minlatitude = FloatOption(default=-90)
    maxlatitude = FloatOption(default=90)
    minlongitude = FloatOption(default=-180)
    maxlongitude = FloatOption(default=180)

    latitude = FloatOption()
    longitude = FloatOption()
    minradius = FloatOption()
    maxradius = FloatOption(default=30)

    def get_time_options(self, event_options=None):
        if self.time_choice == self.TIME_RANGE:
            return self.get_options(['starttime', 'endtime'])
        elif self.time_choice == self.TIME_EVENTS and event_options:
            return event_options.get_time_options()
        else:
            return {}

    def get_location_options(self, event_options=None):
        if self.location_choice == self.LOCATION_BOX:
            return self.get_options(['minlatitude', 'maxlatitude', 'minlongitude', 'maxlongitude'])
        elif self.location_choice == self.LOCATION_POINT:
            return self.get_options(['latitude', 'longitude', 'minradius', 'maxradius'])
        elif self.location_choice == self.LOCATION_EVENTS and event_options:
            return event_options.get_location_options()
        else:
            return {}

    def get_obspy_options(self, event_options=None):
        base_keys = ['network', 'station', 'location', 'channel']
        options = self.get_options(keys=base_keys)
        options.update(self.get_time_options(event_options))
        options.update(self.get_location_options(event_options))
        # Default level is 'station' but we always(?) want 'channel'
        options['level'] = 'channel'
        return options
