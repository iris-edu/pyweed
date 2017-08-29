# -*- coding: utf-8 -*-
"""
Code for saving and loading user-selected events/stations.

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)
import copy
from obspy.core.inventory.inventory import Inventory
from obspy.core.event.catalog import Catalog


def get_filtered_inventory(inventory, stations_iter):
    """
    Given an inventory and an iterator of selected network/station/channel items, return
    an inventory containing only the selected items.
    """
    networks = {}
    stations = {}
    for (network, station, channel) in stations_iter:
        # Create a station record if necessary, and add this channel to it
        full_station_code = "%s.%s" % (network.code, station.code)
        if full_station_code not in stations:
            f_station = copy.copy(station)
            f_station.channels = []
            stations[full_station_code] = f_station
            # Create a network record if necessary, and add this station to it
            if network.code not in networks:
                f_network = copy.copy(network)
                f_network.stations = []
                networks[network.code] = f_network
            networks[network.code].stations.append(f_station)
        stations[full_station_code].channels.append(channel)

    return Inventory(list(networks.values()), inventory.source, inventory.sender)


def get_filtered_catalog(catalog, events_iter):
    """
    Given a catalog and an iterator of selected events, return a catalog containing only the selected events.
    """
    return Catalog(list(events_iter))


