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
from geographiclib.geodesic import Geodesic
from obspy.taup.tau import TauPyModel
from obspy.core.util.attribdict import AttribDict
from future.moves.urllib.parse import urlencode

LOGGER = logging.getLogger(__name__)
GEOD = Geodesic.WGS84
TAUP = TauPyModel()


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


def manageCache(downloadDir, cacheSize):
    """
    Maintain a cache directory at a certain size (MB) by removing the oldest files.
    """

    try:
        # Compile statistics on all files in the output directory and subdirectories
        stats = []
        totalSize = 0
        for root, dirs, files in os.walk(downloadDir):
            for file in files:
                path = os.path.join(root, file)
                statList = os.stat(path)
                # path, size, atime
                newStatList = [path, statList.st_size, statList.st_atime]
                totalSize = totalSize + statList.st_size
                # don't want hidden files like .htaccess so don't add stuff that starts with .
                if not file.startswith('.'):
                    stats.append(newStatList)

        # Sort file stats by last access time
        stats = sorted(stats, key=lambda file: file[2])

        # Delete old files until we get under cacheSize (configured in megabytes)
        deletionCount = 0
        while totalSize > cacheSize * 1000000:
            # front of stats list is the file with the smallest (=oldest) access time
            lastAccessedFile = stats[0]
            # index 1 is where size is
            totalSize = totalSize - lastAccessedFile[1]
            # index 0 is where path is
            os.remove(lastAccessedFile[0])
            # remove the file from the stats list
            stats.pop(0)
            deletionCount = deletionCount + 1

        LOGGER.debug('Removed %d files to keep %s below %.0f megabytes' % (deletionCount, downloadDir, cacheSize))

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
    dist = GEOD.Inverse(lat1, lon1, lat2, lon2, Geodesic.DISTANCE)
    return dist['a12']


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
    return [
        (g['lat2'], g['lon2'])
        for g in [
            GEOD.ArcDirect(lat, lon, (i * 360) / num_points, radius)
            for i in range(0, num_points + 1)
        ]
    ]


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

