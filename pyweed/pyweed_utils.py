"""
Pyweed utility functions.

:copyright:
    Mazama Science
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
from obspy.core.utcdatetime import UTCDateTime

LOGGER = logging.getLogger(__name__)
GEOD = Geodesic.WGS84
TAUP = TauPyModel()


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
                path = os.path.join(root,file)
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

    except Exception, e:
        LOGGER.error(str(e))


def iter_channels(inventory):
    """
    Iterate over every channel in an inventory.
    For each channel, yields (network, station, channel)
    """
    for network in inventory.networks:
        for station in network.stations:
            for channel in station.channels:
                yield (network, station, channel)


def get_sncl(network, station, channel):
    """
    Generate the SNCL for the given network/station/channel
    """
    return '.'.join((network.code, station.code, channel.location_code, channel.code))


def get_event_id(event):
    """
    Get a unique ID for a given event
    """
    # We use the resource id, which is a URI, and we pull off only the final (alphanumeric) component
    # ex:
    #
    # quakeml:nc.anss.org/Event/NC/72734605 -> 72734605
    return re.sub(r'^.*?(\w+)\W*$', r'\1', event.resource_id.id)


def get_event_name(event):
    origin = get_preferred_origin(event)
    time_str = origin.time.isoformat(sep=' ').split('.')[0]
    mag = get_preferred_magnitude(event)
    mag_str = "%s%s" % (mag.mag, mag.magnitude_type)
    region_str = str(event.event_descriptions[0].text).title()
    return "%s | %s | %s" % (time_str, mag_str, region_str)


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


class Distances(AttribDict):
    defaults = dict(
        distance=0,
        azimuth=0,
        arrival=UTCDateTime(),
    )


def get_distance(lat1, lon1, lat2, lon2):
    """
    Get the distance between two points in degrees
    """
    dist = GEOD.Inverse(lat1, lon1, lat2, lon2, Geodesic.DISTANCE)
    return dist['a12']


def calculate_distances(event, station, phase_list=None):
    """
    Calculate distance, azimuth, arrival time, etc.
    """
    origin = get_preferred_origin(event)
    if not origin:
        raise Exception("No origin")
    distaz = GEOD.Inverse(
        origin.latitude, origin.longitude,
        station.latitude, station.longitude)

    if not phase_list:
        phase_list = ['ttp']

    tt = TAUP.get_travel_times(
        origin.depth / 1000,
        distaz['a12'],
        phase_list
    )
    if tt:
        offset = tt[0].time
    else:
        offset = 0

    return Distances(
        distance=distaz['a12'],
        azimuth=distaz['azi1'],
        arrival=(origin.time + offset),
    )


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
