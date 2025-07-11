# -*- coding: utf-8 -*-
"""
Container for stations.

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import absolute_import, division, print_function

import logging
from pyweed.signals import SignalingThread, SignalingObject
from obspy.core.inventory import Inventory, Station
from obspy.clients.fdsn import Client
from pyweed.pyweed_utils import (
    get_service_url,
    CancelledException,
    DataRequest,
    get_distance,
)
from PyQt5 import QtCore
import concurrent.futures
from pyweed.dist_from_events import get_combined_locations, CrossBorderException

LOGGER = logging.getLogger(__name__)


def load_stations(client: Client, parameters):
    """
    Execute one query for station metadata. This is a standalone function so we can
    run it in a separate thread.
    """
    try:
        LOGGER.info(
            "Loading stations: %s", get_service_url(client, "station", parameters)
        )
        return client.get_stations(**parameters)
    except Exception as e:
        # If no results found, the client will raise an exception, we need to trap this
        # TODO: this should be much cleaner with a fix to https://github.com/obspy/obspy/issues/1656
        if str(e).startswith("No data"):
            LOGGER.warning("No stations found! Your query may be too narrow.")
            return Inventory([], "INTERNAL")
        else:
            raise


class StationsLoader(SignalingThread):
    """
    Thread to handle station requests
    """

    progress = QtCore.pyqtSignal()

    def __init__(self, request: "StationsDataRequest"):
        """
        Initialization.
        """
        # Keep a reference to globally shared components
        self.request = request
        self.futures = {}
        super(StationsLoader, self).__init__()

    def run(self):
        """
        Make a webservice request for events using the passed in options.
        """
        self.setPriority(QtCore.QThread.LowestPriority)
        self.clearFutures()
        self.futures = {}

        inventory = None
        LOGGER.info("Making %d station requests" % len(self.request.sub_requests))
        with concurrent.futures.ThreadPoolExecutor(5) as executor:
            for sub_request in self.request.sub_requests:
                # Dictionary lets us look up argument by result later
                self.futures[
                    executor.submit(load_stations, self.request.client, sub_request)
                ] = sub_request
            # Iterate through Futures as they complete
            for result in concurrent.futures.as_completed(self.futures):
                LOGGER.debug("Stations loaded")
                try:
                    if not inventory:
                        inventory = result.result()
                    else:
                        inventory += result.result()
                    self.progress.emit()
                except Exception:
                    self.progress.emit()
        self.futures = {}
        # If no inventory object (ie. no sub-requests were run) create a dummy one
        if not inventory:
            inventory = Inventory([], "INTERNAL")
        inventory = self.request.process_result(inventory)
        self.done.emit(inventory)

    def clearFutures(self):
        """
        Cancel any outstanding tasks
        """
        if self.futures:
            for future in self.futures:
                if not future.done():
                    LOGGER.debug("Cancelling unexecuted future")
                    future.cancel()

    def cancel(self):
        """
        User-requested cancel
        """
        self.done.disconnect()
        self.progress.disconnect()
        self.clearFutures()


class StationsDataRequest(DataRequest):
    event_locations = None
    distance_range = None

    def __init__(self, client: Client, base_options, distance_range, event_locations):
        """
        :param client: an ObsPy FDSN client
        :param base_options: the basic query options (ie. from StationOptions)
        :param distance_range: a tuple of (min, max) if querying by distance from events
        :param event_locations: a list of selected event locations if querying by distance from events
        """
        super(StationsDataRequest, self).__init__(client)
        if distance_range and event_locations:
            # Get a list of just the (lat, lon) for each event
            self.event_locations = list((loc[1] for loc in event_locations))
            self.distance_range = distance_range
            try:
                combined_locations = get_combined_locations(
                    self.event_locations, self.distance_range["maxdistance"]
                )
                self.sub_requests = [
                    dict(
                        base_options,
                        minlatitude=box.lat1,
                        maxlatitude=box.lat2,
                        minlongitude=box.lon1,
                        maxlongitude=box.lon2,
                    )
                    for box in combined_locations
                ]
            except CrossBorderException:
                # Can't break into subqueries, return the base (global, we assume) query
                LOGGER.warning(
                    "Couldn't calculate a bounding box for events, using global"
                )
                self.sub_requests = [base_options]
        else:
            self.sub_requests = [base_options]

    def filter_one_station(self, station: Station):
        """
        Filter one station from the results
        """
        for lat, lon in self.event_locations:
            dist = get_distance(lat, lon, station.latitude, station.longitude)
            if (
                self.distance_range["mindistance"]
                <= dist
                <= self.distance_range["maxdistance"]
            ):
                return True
        return False

    def process_result(self, result):
        """
        If the request is based on distance from a set of events, we need to perform
        a filter after the request, since the low-level request probably overselected.
        """
        result = super(StationsDataRequest, self).process_result(result)
        if (
            isinstance(result, Inventory)
            and self.event_locations
            and self.distance_range
        ):
            filtered_networks = []
            for network in result:
                filtered_stations = [
                    station for station in network if self.filter_one_station(station)
                ]
                if filtered_stations:
                    network.stations = filtered_stations
                    filtered_networks.append(network)
            result.networks = filtered_networks
        return result


class StationsHandler(SignalingObject):
    """
    Container for stations.
    """

    def __init__(self, pyweed):
        """
        Initialization.
        """
        super(StationsHandler, self).__init__()

        self.pyweed = pyweed
        self.inventory_loader = None

    def load_inventory(self, request: StationsDataRequest):
        try:
            self.inventory_loader = StationsLoader(request)
            self.inventory_loader.done.connect(self.on_inventory_loaded)
            self.inventory_loader.start()
        except Exception as e:
            self.done.emit(e)

    def on_inventory_loaded(self, inventory):
        self.done.emit(inventory)

    def cancel(self):
        if self.inventory_loader:
            self.inventory_loader.done.disconnect()
        self.done.emit(CancelledException())


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import doctest

    doctest.testmod(exclude_empty=True)
