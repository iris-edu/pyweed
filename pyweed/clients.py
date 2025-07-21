from enum import Enum
from typing import Dict
from obspy.clients.fdsn import Client
import logging

LOGGER = logging.getLogger(__name__)


class FDSNService(Enum):
    EVENT = "event"
    STATION = "station"
    DATASELECT = "dataselect"


class ClientInitializationError(Exception):
    """
    Error thrown if we can't initialize an ObsPy client
    """

    pass


class ClientManager(object):
    """
    Manages a set of ObsPy clients for different services and data centers.
    """

    clients: Dict[FDSNService, Client] = None
    data_centers: Dict[FDSNService, str] = None

    def initialize(
        self,
        event_data_center: str,
        station_data_center: str,
        dataselect_data_center: str,
    ):
        LOGGER.info("Initializing ObsPy client(s)")
        self.data_centers = {}
        self.clients = {}
        self.set_data_center(FDSNService.EVENT, event_data_center)
        self.set_data_center(FDSNService.STATION, station_data_center)
        self.set_data_center(FDSNService.DATASELECT, dataselect_data_center)

    def set_data_center(self, service: FDSNService, data_center: str):
        """
        Set the data center used for the given service
        """
        if data_center == self.data_centers.get(service) and self.clients.get(service):
            # Already set, no action needed
            return

        # See if we can reuse one of the other clients
        client = self.find_existing_client(service, data_center)
        if not client:
            LOGGER.info("Creating ObsPy %s client for %s", service.value, data_center)
            try:
                client = self.create_client(service, data_center)
            except Exception as e:
                raise ClientInitializationError("Couldn't create ObsPy client") from e
        # Verify that this client supports the service we need
        if service.value not in client.services:
            raise ClientInitializationError(
                "The %s data center does not provide a %s service"
                % (data_center, service)
            )
        # Update settings
        self.data_centers[service] = data_center
        self.clients[service] = client

    def find_existing_client(self, service: FDSNService, data_center: str):
        """
        Search for an existing client (associated with a different service) that can also work for
        the given service. This is to handle the common case where all the clients are targeting the
        same data center.
        """
        for other_service in (
            FDSNService.EVENT,
            FDSNService.STATION,
            FDSNService.DATASELECT,
        ):
            other_client = (
                other_service != service
                and data_center == self.data_centers.get(other_service)
                and self.clients.get(other_service)
            )
            if other_client:
                return other_client
        return None

    def create_client(self, service: FDSNService, url_or_label: str):
        """
        Create an ObsPy Client

        @param service: service type (eg. 'event' or 'station')
        @param url_or_label: either an ObsPy label or a URL for that service

        NOTE: url_or_label here is different from the Client's base_url -- the base_url is just the
        base domain, so it can only do standard FDSN service paths (eg. starting with /fdsnws)
        To allow totally custom URLs, we take the URL for the service itself
        (eg. https://service.iris.edu/fdsnwsbeta/station/1/) and explicitly map it.
        """
        kwargs = {}
        if url_or_label.startswith("http"):
            service_mappings = {}
            service_mappings[service.value] = url_or_label
            return Client(url_or_label, service_mappings=service_mappings, **kwargs)
        else:
            return Client(url_or_label, **kwargs)

    @property
    def event_data_center(self):
        return self.data_centers.get(FDSNService.EVENT)

    @property
    def station_data_center(self):
        return self.data_centers.get(FDSNService.STATION)

    @property
    def dataselect_data_center(self):
        return self.data_centers.get(FDSNService.DATASELECT)

    @property
    def event_client(self):
        return self.clients.get(FDSNService.EVENT)

    @property
    def station_client(self):
        return self.clients.get(FDSNService.STATION)

    @property
    def dataselect_client(self):
        return self.clients.get(FDSNService.DATASELECT)
