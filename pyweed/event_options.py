# -*- coding: utf-8 -*-
"""
Event Options

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from pyweed.options import Options, DateOption, FloatOption, Option


class EventOptions(Options):

    TIME_RANGE = 'timeBetween'
    TIME_STATIONS = 'timeFromStations'
    time_choice = Option(hidden=True, default=TIME_RANGE)

    starttime = DateOption(default=-30)
    endtime = DateOption(default=0)

    minmagnitude = FloatOption(default=5.0)
    maxmagnitude = FloatOption(default=10.0)
    magnitudetype = Option()

    mindepth = FloatOption(default=0)
    maxdepth = FloatOption(default=6800)

    LOCATION_GLOBAL = 'locationGlobal'
    LOCATION_BOX = 'locationRange'
    LOCATION_POINT = 'locationDistanceFromPoint'
    LOCATION_STATIONS = 'locationFromStations'
    location_choice = Option(hidden=True, default=LOCATION_GLOBAL)

    minlatitude = FloatOption(default=-90)
    maxlatitude = FloatOption(default=90)
    minlongitude = FloatOption(default=-180)
    maxlongitude = FloatOption(default=180)

    latitude = FloatOption()
    longitude = FloatOption()
    minradius = FloatOption()
    maxradius = FloatOption(default=30)

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
        base_keys = ['minmagnitude', 'maxmagnitude', 'magnitudetype', 'mindepth', 'maxdepth']
        options = self.get_options(keys=base_keys)
        # Need special handling for "All Types" value of magnitudetype
        if options.get('magnitudetype', '').lower().startswith('all'):
            del options['magnitudetype']
        options.update(self.get_time_options())
        options.update(self.get_location_options())
        return options
