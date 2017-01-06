from options import Options, DateOption, FloatOption, Option


class EventOptions(Options):

    time_choice = Option(hidden=True)
    TIME_RANGE = 'timeBetween'
    TIME_STATIONS = 'timeDuringStations'

    starttime = DateOption(default=-30)
    endtime = DateOption(default=0)

    minmagnitude = FloatOption(default=5.0)
    maxmagnitude = FloatOption(default=10.0)
    magtype = Option()

    mindepth = FloatOption(default=0)
    maxdepth = FloatOption(default=6800)

    location_choice = Option(hidden=True)
    LOCATION_BOX = 'locationRange'
    LOCATION_POINT = 'locationDistanceFromPoint'
    LOCATION_STATIONS = 'locationDistanceFromStations'

    minlatitude = FloatOption(default=-90)
    maxlatitude = FloatOption(default=90)
    minlongitude = FloatOption(default=-180)
    maxlongitude = FloatOption(default=180)

    latitude = FloatOption()
    longitude = FloatOption()
    minradius = FloatOption()
    maxradius = FloatOption(default=30)

    def get_obspy_options(self):
        exclude = set()
        if self.time_choice != self.TIME_RANGE:
            exclude.update(['starttime', 'endtime'])
        if self.location_choice != self.LOCATION_BOX:
            exclude.update(['minlatitude', 'maxlatitude', 'minlongitude', 'maxlongitude'])
        if self.location_choice != self.LOCATION_POINT:
            exclude.update(['latitude', 'longitude', 'minradius', 'maxradius'])

        keys = [k for k in self.keys(hidden=False) if k not in exclude]
        return self.get_options(keys=keys)
