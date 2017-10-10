# -*- coding: utf-8 -*-
"""
Selecting stations based on selected events.

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)
from logging import getLogger

LOGGER = getLogger(__name__)


class CrossBorderException(Exception):
    pass


class LatLonBox(object):
    lat1 = None
    lat2 = None
    lon1 = None
    lon2 = None

    def __init__(self, distance):
        self.distance = distance

    def add_point(self, lat, lon):
        if self.lat1 is None:
            self.lat1 = lat - self.distance
            self.lat2 = lat + self.distance
            self.lon1 = lon - self.distance
            self.lon2 = lon + self.distance
        else:
            self.lat1 = min(self.lat1, lat - self.distance)
            self.lat2 = max(self.lat2, lat + self.distance)
            self.lon1 = min(self.lon1, lon - self.distance)
            self.lon2 = max(self.lon2, lon + self.distance)

        if self.lat1 < -90 or self.lat2 > 90 or self.lon1 < -180 or self.lon2 > 180:
            raise CrossBorderException()

    def __str__(self):
        return "[%s, %s, %s, %s]" % (self.lat1, self.lon1, self.lat2, self.lon2)


def get_combined_locations(points, distance):
    """
    Given a set of points and a distance, return a reasonable set of
    bounding areas covering everything within that distance of any point.
    """
    # Very simple implementation, try to draw a box around all points
    box = LatLonBox(distance)

    if not points:
        return []

    for lat, lon in points:
        box.add_point(lat, lon)
    LOGGER.info("Combined points into: %s", box)
    return [box]
