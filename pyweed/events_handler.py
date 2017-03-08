"""
Container for events.

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

from signals import SignalingThread, SignalingObject
import logging
from obspy.core.event.catalog import Catalog

LOGGER = logging.getLogger(__name__)


class EventsLoader(SignalingThread):
    """
    Thread to handle event requests
    """

    def __init__(self, client, parameters):
        """
        Initialization.
        """
        self.client = client
        self.parameters = parameters
        super(EventsLoader, self).__init__()

    def run(self):
        """
        Make a webservice request for events using the passed in options.
        """
        # Sanity check
        try:
            if 'starttime' not in self.parameters or 'endtime' not in self.parameters:
                raise ValueError('starttime or endtime is missing')
            LOGGER.info('Loading events...')
            event_catalog = self.client.get_events(**self.parameters)
            self.done.emit(event_catalog)
        except Exception as e:
            # If no results found, the client will raise an exception, we need to trap this
            # TODO: this should be much cleaner with a fix to https://github.com/obspy/obspy/issues/1656
            if e.message.startswith("No data"):
                LOGGER.warning("No events found! Your query may be too narrow.")
                self.done.emit(Catalog())
            else:
                self.done.emit(e)
                raise


class EventsHandler(SignalingObject):
    """
    Container for events.
    """

    def __init__(self, pyweed):
        """
        Initialization.
        """
        super(EventsHandler, self).__init__()
        self.pyweed = pyweed
        self.catalog_loader = None

    def load_catalog(self, parameters=None):
        if not parameters:
            parameters = self.pyweed.get_event_obspy_options()
        self.catalog_loader = EventsLoader(self.pyweed.client, parameters)
        self.catalog_loader.done.connect(self.on_catalog_loaded)
        self.catalog_loader.start()

    def on_catalog_loaded(self, event_catalog):
        self.done.emit(event_catalog)


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
