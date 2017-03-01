from options import Options, DateOption, FloatOption, Option


class EventOptions(Options):

    time_choice = Option(hidden=True)
    TIME_RANGE = 'timeBetween'
    TIME_STATIONS = 'timeFromStations'

    starttime = DateOption(default=-30)
    endtime = DateOption(default=0)

    minmagnitude = FloatOption(default=5.0)
    maxmagnitude = FloatOption(default=10.0)
    magtype = Option()

    mindepth = FloatOption(default=0)
    maxdepth = FloatOption(default=6800)

    location_choice = Option(hidden=True)
    LOCATION_GLOBAL = 'locationGlobal'
    LOCATION_BOX = 'locationRange'
    LOCATION_POINT = 'locationDistanceFromPoint'
    LOCATION_STATIONS = 'locationFromStations'

    minlatitude = FloatOption(default=-90)
    maxlatitude = FloatOption(default=90)
    minlongitude = FloatOption(default=-180)
    maxlongitude = FloatOption(default=180)

    latitude = FloatOption()
    longitude = FloatOption()
    minradius = FloatOption()
    maxradius = FloatOption(default=30)

    def get_time_options(self, station_options=None):
        if self.time_choice == self.TIME_RANGE:
            return self.get_options(['starttime', 'endtime'])
        elif self.time_choice == self.TIME_STATIONS and station_options:
            return station_options.get_time_options()
        else:
            return {}

    def get_location_options(self, station_options=None):
        if self.location_choice == self.LOCATION_BOX:
            return self.get_options(['minlatitude', 'maxlatitude', 'minlongitude', 'maxlongitude'])
        elif self.location_choice == self.LOCATION_POINT:
            return self.get_options(['latitude', 'longitude', 'minradius', 'maxradius'])
        elif self.location_choice == self.LOCATION_STATIONS and station_options:
            return station_options.get_location_options()
        else:
            return {}

    def get_obspy_options(self, station_options=None):
        base_keys = ['minmagnitude', 'maxmagnitude', 'magtype', 'mindepth', 'maxdepth']
        options = self.get_options(keys=base_keys)
        options.update(self.get_time_options(station_options))
        options.update(self.get_location_options(station_options))
        return options
