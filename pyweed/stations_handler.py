"""
Container for stations.

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

import logging
from pyweed.signals import SignalingThread, SignalingObject
from obspy.core.inventory.inventory import Inventory
from pyweed.pyweed_utils import get_service_url

LOGGER = logging.getLogger(__name__)


class StationsLoader(SignalingThread):
    """
    Thread to handle station requests
    """

    def __init__(self, client, parameters):
        """
        Initialization.
        """
        # Keep a reference to globally shared components
        self.client = client
        self.parameters = parameters
        super(StationsLoader, self).__init__()

    def run(self):
        """
        Make a webservice request for events using the passed in options.
        """
        # Sanity check
        try:
            if 'starttime' not in self.parameters or 'endtime' not in self.parameters:
                raise ValueError('starttime or endtime is missing')
            LOGGER.info('Loading stations: %s', get_service_url(self.client, 'station', self.parameters))
            inventory = self.client.get_stations(**self.parameters)
            self.done.emit(inventory)
        except Exception as e:
            # If no results found, the client will raise an exception, we need to trap this
            # TODO: this should be much cleaner with a fix to https://github.com/obspy/obspy/issues/1656
            if str(e).startswith("No data"):
                LOGGER.warning("No stations found! Your query may be too narrow.")
                self.done.emit(Inventory([], 'INTERNAL'))
            else:
                self.done.emit(e)
                raise


class StationsHandler(SignalingObject):
    """
    Container for events.
    """

    def __init__(self, pyweed):
        """
        Initialization.
        """
        super(StationsHandler, self).__init__()

        self.pyweed = pyweed
        self.inventory_loader = None

    def load_inventory(self, parameters=None):
        if not parameters:
            parameters = self.pyweed.get_station_obspy_options()
        self.inventory_loader = StationsLoader(self.pyweed.client, parameters)
        self.inventory_loader.done.connect(self.on_inventory_loaded)
        self.inventory_loader.start()

    def on_inventory_loaded(self, inventory):
        self.done.emit(inventory)


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
