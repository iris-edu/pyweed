# -*- coding: utf-8 -*-
"""
Station Options

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from PyQt4 import QtGui, QtCore
from pyweed.gui.uic import StationOptionsWidget
import logging
from pyweed.station_options import StationOptions
from distutils.util import strtobool
from pyweed.gui.OptionsWidget import BaseOptionsWidget

LOGGER = logging.getLogger(__name__)


class StationOptionsWidget(BaseOptionsWidget, StationOptionsWidget.Ui_StationOptionsWidget):
    """
    Dialog window for event options used in creating a webservice query.
    """

    def mapInputs(self):
        return {
            'network': self.networkLineEdit,
            'station': self.stationLineEdit,
            'location': self.locationLineEdit,
            'channel': self.channelLineEdit,
            'starttime': self.starttimeDateTimeEdit,
            'endtime': self.endtimeDateTimeEdit,
            'minlongitude': self.locationRangeWestDoubleSpinBox,
            'maxlongitude': self.locationRangeEastDoubleSpinBox,
            'minlatitude': self.locationRangeSouthDoubleSpinBox,
            'maxlatitude': self.locationRangeNorthDoubleSpinBox,
            'minradius': self.distanceFromPointMinRadiusDoubleSpinBox,
            'maxradius': self.distanceFromPointMaxRadiusDoubleSpinBox,
            'longitude': self.distanceFromPointEastDoubleSpinBox,
            'latitude': self.distanceFromPointNorthDoubleSpinBox,
            '_locationGlobal': self.locationGlobalRadioButton,
            '_locationRange': self.locationRangeRadioButton,
            '_locationDistanceFromPoint': self.locationDistanceFromPointRadioButton,
        }

    def optionsToInputs(self, values):
        # Turn the option choice value into a set of radio values
        location_choice = values.get('location_choice')
        values['_locationGlobal'] = (location_choice == StationOptions.LOCATION_GLOBAL)
        values['_locationRange'] = (location_choice == StationOptions.LOCATION_BOX)
        values['_locationDistanceFromPoint'] = (location_choice == StationOptions.LOCATION_POINT)
        return values

    def inputsToOptions(self, values):
        # Turn the radio values into an option choice value
        if strtobool(values.get('_locationGlobal', 'F')):
            values['location_choice'] = StationOptions.LOCATION_GLOBAL
        elif strtobool(values.get('_locationRange', 'F')):
            values['location_choice'] = StationOptions.LOCATION_BOX
        elif strtobool(values.get('_locationDistanceFromPoint', 'F')):
            values['location_choice'] = StationOptions.LOCATION_POINT
        return values

    def get_timeFromOtherButton(self):
        return self.timeFromEventsToolButton

    def get_locationFromOtherButton(self):
        return self.locationFromEventsToolButton

