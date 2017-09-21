# -*- coding: utf-8 -*-
"""
Container for stations.

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

import logging
from pyweed.signals import SignalingThread, SignalingObject
from obspy.core.inventory.inventory import Inventory
from pyweed.pyweed_utils import get_service_url, CancelledException
from PyQt4 import QtCore
import concurrent.futures

LOGGER = logging.getLogger(__name__)


def load_stations(client, parameters):
    """
    Execute one query for station metadata. This is a standalone function so we can
    run it in a separate thread.
    """
    try:
        LOGGER.info('Loading stations: %s', get_service_url(client, 'station', parameters))
        return client.get_stations(**parameters)
    except Exception as e:
        # If no results found, the client will raise an exception, we need to trap this
        # TODO: this should be much cleaner with a fix to https://github.com/obspy/obspy/issues/1656
        if str(e).startswith("No data"):
            LOGGER.warning("No stations found! Your query may be too narrow.")
            return Inventory([], 'INTERNAL')
        else:
            raise


class StationsLoader(SignalingThread):
    """
    Thread to handle station requests
    """
    progress = QtCore.pyqtSignal()

    def __init__(self, client, options):
        """
        Initialization.
        """
        # Keep a reference to globally shared components
        self.client = client
        self.station_options = station_options
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
        LOGGER.info("Making %d station requests" % len(self.request_params))
        with concurrent.futures.ThreadPoolExecutor(5) as executor:
            for options in self.station_options.get_station_obspy_options():
                # Dictionary to look up the waveform id by Future
                self.futures[executor.submit(load_stations, self.client, options)] = 1
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

    def load_inventory(self, station_options):
        try:
            self.inventory_loader = StationsLoader(self.pyweed.station_client, station_options)
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

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
