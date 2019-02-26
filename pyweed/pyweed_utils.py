# -*- coding: utf-8 -*-
"""
Pyweed utility functions.

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
import re
from pyproj import Geod
from obspy.taup.tau import TauPyModel
from urllib.parse import urlencode

LOGGER = logging.getLogger(__name__)
GEOD = Geod(ellps='WGS84')
TAUP = TauPyModel()

# Rough meters/degree calculation
M_PER_DEG = (GEOD.inv(0, 0, 0, 1)[2] + GEOD.inv(0, 0, 1, 0)[2]) / 2



class OutputFormat(object):
    """
    Simple output format definition.
    """
    def __init__(self, value, label=None, extension=None):
        #: This is the name used by ObsPy, which we treat as the "real" value
        self.value = value
        #: This is the label used in the UI, it defaults to value
        self.label = label or value
        #: This is the file extension, it defaults to lowercased value
        self.extension = extension or value.lower()

# List of the output formats we support
OUTPUT_FORMATS = [
    OutputFormat('MSEED', 'MiniSEED'),
    OutputFormat('SAC'),
    OutputFormat('SACXY', 'SAC ASCII', 'sac.txt'),
    OutputFormat('SLIST', 'ASCII (1 column)', 'ascii1.txt'),
    OutputFormat('TSPAIR', 'ASCII (2 column)', 'ascii2.txt'),
]
# Map of a format to the file extension to use
OUTPUT_FORMAT_EXTENSIONS = dict(((f.value, f.extension) for f in OUTPUT_FORMATS))


class Phase(object):
    """
    Simple phase definition
    """
    def __init__(self, name, label):
        self.name = name
        self.label = label

# List of phases we can use for time windows
EVENT_TIME_PHASE = 'Event'
PHASES = [
    Phase('P', 'P wave arrival'),
    Phase('S', 'S wave arrival'),
    Phase(EVENT_TIME_PHASE, 'Event time')
]
# Actual phase values retrieved from TauP, this should give us a good P and S value for any input (I hope!)
TAUP_PHASES = ['P', 'PKIKP', 'Pdiff', 'S', 'SKIKS', 'SKS', 'p', 's']


def manage_cache(download_dir, cache_size):
    """
    Maintain a cache directory at a certain size (MB) by removing the oldest files.
    """

    try:
        # Compile statistics on all files in the output directory and subdirectories
        stats = []
        total_size = 0
        for root, dirs, files in os.walk(download_dir):
            for file in files:
                path = os.path.join(root, file)
                stat_list = os.stat(path)
                # path, size, atime
                new_stat_list = [path, stat_list.st_size, stat_list.st_atime]
                total_size = total_size + stat_list.st_size
                # don't want hidden files like .htaccess so don't add stuff that starts with .
                if not file.startswith('.'):
                    stats.append(new_stat_list)

        # Sort file stats by last access time
        stats = sorted(stats, key=lambda file: file[2])

        # Delete old files until we get under cache_size (configured in megabytes)
        deletion_count = 0
        while total_size > cache_size * 1000000:
            # front of stats list is the file with the smallest (=oldest) access time
            last_accessed_file = stats[0]
            # index 1 is where size is
            total_size = total_size - last_accessed_file[1]
            # index 0 is where path is
            os.remove(last_accessed_file[0])
            # remove the file from the stats list
            stats.pop(0)
            deletion_count = deletion_count + 1

        LOGGER.debug('Removed %d files to keep %s below %.0f megabytes' % (deletion_count, download_dir, cache_size))

    except Exception as e:
        LOGGER.error(str(e))


def iter_channels(inventory, dedupe=True):
    """
    Iterate over every channel in an inventory.
    For each channel, yields (network, station, channel)

    If dedupe=True, repeated channels are filtered out -- this can occur if the inventory includes
    multiple epochs for a given channel. Only the first channel will be included in this case.
    """
    last_sncl = None
    if inventory:
        for network in inventory.networks:
            for station in network.stations:
                for channel in station.channels:
                    if dedupe:
                        sncl = get_sncl(network, station, channel)
                        if sncl == last_sncl:
                            continue
                        last_sncl = sncl
                    yield (network, station, channel)


def get_sncl(network, station, channel):
    """
    Generate the SNCL for the given network/station/channel
    """
    return '.'.join((network.code, station.code, channel.location_code, channel.code))


def get_event_id(event):
    """
    Get a unique ID for a given event

    Event IDs are given differently by different data centers.

    Examples compiled by crotwell@seis.sc.edu:

    IRIS
    <event publicID="smi:service.iris.edu/fdsnws/event/1/query?eventid=3337497">

    NCEDC
    <event publicID="quakeml:nc.anss.org/Event/NC/71377596"
    catalog:datasource="nc" catalog:dataid="nc71377596"
    catalog:eventsource="nc" catalog:eventid="71377596">

    SCEDC
    <event publicID="quakeml:service.scedc.caltech.edu/fdsnws/event/1/query?eventid=37300872"
    catalog:datasource="ci" catalog:dataid="ci37300872"
    catalog:eventsource="ci" catalog:eventid="37300872">

    USGS
    <event catalog:datasource="us" catalog:eventsource="us"
    catalog:eventid="c000lvb5"
    publicID="quakeml:earthquake.usgs.gov/fdsnws/event/1/query?eventid=usc000lvb5&format=quakeml">

    ETHZ
    <event publicID="smi:ch.ethz.sed/sc3a/2017eemfch">

    INGV
    <event publicID="smi:webservices.ingv.it/fdsnws/event/1/query?eventId=863301">

    ISC
    <event publicID="smi:ISC/evid=600516598">
    """
    # Look for "eventid=" as a URL query parameter
    m = re.search(r'eventid=([^\&]+)', event.resource_id.id, re.IGNORECASE)
    if m:
        return m.group(1)
    # Otherwise, return the trailing segment of alphanumerics
    return re.sub(r'^.*?(\w+)\W*$', r'\1', event.resource_id.id)


def get_event_name(event):
    time_str = get_event_time_str(event)
    mag_str = get_event_mag_str(event)
    description = get_event_description(event)
    return "%s | %s | %s" % (time_str, mag_str, description)


def format_time_str(time):
    return time.isoformat(sep=' ').split('.')[0]


def get_event_time_str(event):
    origin = get_preferred_origin(event)
    return format_time_str(origin.time)


def get_event_mag_str(event):
    mag = get_preferred_magnitude(event)
    return "%s%s" % (mag.mag, mag.magnitude_type)


def get_event_description(event):
    return str(event.event_descriptions[0].text).title()


def get_preferred_origin(event):
    """
    Get the preferred origin for the event, or None if not defined
    """
    origin = event.preferred_origin()
    if not origin:
        LOGGER.error("No preferred origin found for event %s", event.resource_id)
        if len(event.origins):
            origin = event.origins[0]
    return origin


def get_preferred_magnitude(event):
    """
    Get the preferred magnitude for the event, or None if not defined
    """
    magnitude = event.preferred_magnitude()
    if not magnitude:
        LOGGER.error("No preferred magnitude found for event %s", event.resource_id)
        if len(event.magnitudes):
            magnitude = event.magnitudes[0]
    return magnitude


class TimeWindow(object):
    """
    Represents a time window for data based on phase arrivals at a particular location
    """
    start_offset = 0
    end_offset = 0
    start_phase = None
    end_phase = None

    def __init__(self, start_offset=0, end_offset=0, start_phase=PHASES[0].name, end_phase=PHASES[0].name):
        self.update(start_offset, end_offset, start_phase, end_phase)

    def update(self, start_offset, end_offset, start_phase, end_phase):
        """
        Set all values. Phases can be specified by name or label.
        """
        self.start_offset = start_offset
        self.end_offset = end_offset
        self.start_phase = start_phase
        self.end_phase = end_phase

    def calculate_window(self, event_time, arrivals):
        """
        Given an event time and a dictionary of arrival times (see Distances below)
        calculate the full time window
        """
        return (
            # Start time
            event_time + arrivals.get(self.start_phase, 0) - self.start_offset,
            # End time
            event_time + arrivals.get(self.end_phase, 0) + self.end_offset,
        )

    def __eq__(self, other):
        """
        Compare two TimeWindows
        """
        if not isinstance(other, TimeWindow):
            return False
        return (other.start_offset == self.start_offset and
                other.end_offset == self.end_offset and
                other.start_phase == self.start_phase and
                other.end_phase == self.end_phase)


def get_distance(lat1, lon1, lat2, lon2):
    """
    Get the distance between two points in degrees
    """
    # NOTE that GEOD takes longitude first!
    _az, _baz, meters = GEOD.inv(lon1, lat1, lon2, lat2)
    return meters / M_PER_DEG


def get_arrivals(distance, event_depth):
    """
    Calculate phase arrival times

    :param distance: distance in degrees
    :param event_depth: event depth in km
    """
    arrivals = TAUP.get_travel_times(
        event_depth,
        distance,
        TAUP_PHASES
    )

    # From the travel time and origin, calculate the actual first arrival time for each basic phase type
    first_arrivals = {}
    for arrival in arrivals:
        # The basic phase name is the uppercase first letter of the full phase name
        # We assume this matches a Phase.name defined in PHASES
        phase_name = arrival.name[0].upper()
        if phase_name not in first_arrivals:
            first_arrivals[phase_name] = arrival.time

    return first_arrivals


def get_bounding_circle(lat, lon, radius, num_points=36):
    """
    Returns groups of lat/lon pairs representing a circle on the map
    """
    radius_meters = radius * M_PER_DEG
    # NOTE that GEOD takes longitude first!
    trans = GEOD.fwd(
        [lon] * num_points,
        [lat] * num_points,
        list(((i * 360) / num_points) for i in range(num_points)),
        [radius_meters] * num_points
    )
    points = list(zip(trans[1], trans[0]))
    # We need to complete the circle by adding the first point again as the last point
    points.append(points[0])
    return points


def get_service_url(client, service, parameters):
    """
    Figure out the URL for the given service call. This isn't publicly available from the ObsPy client,
    we need to use internal APIs, so those messy details are encapsulated here.
    """
    try:
        return client._create_url_from_parameters(service, {}, parameters)
    except:
        return "%s %s %s" % (
            client.base_url, service, urlencode(parameters)
        )


class CancelledException(Exception):
    """
    An exception to return in an event notification indicating that an operation was cancelled.
    See `StationsHandler` for an example.
    """
    def __str__(self, *args, **kwargs):
        s = super(CancelledException, self).__str__(*args, **kwargs)
        if s == '':
            return 'Cancelled'
        else:
            return s


class DataRequest(object):
    """
    Wrapper object for a data request, which may or may not be more than a single web service query.
    """
    # The client to use
    client = None
    # List of option dictionaries, one for each sub-request required
    sub_requests = None

    def __init__(self, client, *requests):
        self.client = client
        self.sub_requests = requests

    def process_result(self, result):
        """
        Subclasses can define behavior here to do post-processing on the resulting data
        """
        return result
