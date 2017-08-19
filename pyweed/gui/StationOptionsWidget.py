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
from pyweed.gui.utils import OptionsAdapter
from pyweed.station_options import StationOptions
from distutils.util import strtobool

LOGGER = logging.getLogger(__name__)


class StationOptionsAdapter(OptionsAdapter):
    def connect_to_widget(self, widget):
        self.inputs = {
            'network': widget.networkLineEdit,
            'station': widget.stationLineEdit,
            'location': widget.locationLineEdit,
            'channel': widget.channelLineEdit,
            'starttime': widget.starttimeDateTimeEdit,
            'endtime': widget.endtimeDateTimeEdit,
            'minlongitude': widget.locationRangeWestDoubleSpinBox,
            'maxlongitude': widget.locationRangeEastDoubleSpinBox,
            'minlatitude': widget.locationRangeSouthDoubleSpinBox,
            'maxlatitude': widget.locationRangeNorthDoubleSpinBox,
            'minradius': widget.distanceFromPointMinRadiusDoubleSpinBox,
            'maxradius': widget.distanceFromPointMaxRadiusDoubleSpinBox,
            'longitude': widget.distanceFromPointEastDoubleSpinBox,
            'latitude': widget.distanceFromPointNorthDoubleSpinBox,
            '_locationGlobal': widget.locationGlobalRadioButton,
            '_locationRange': widget.locationRangeRadioButton,
            '_locationDistanceFromPoint': widget.locationDistanceFromPointRadioButton,
        }

    def options_to_inputs(self, options):
        inputs = super(StationOptionsAdapter, self).options_to_inputs(options)
        # Set the radio buttons based on the EventOptions settings
        inputs['_locationGlobal'] = str(options.location_choice == StationOptions.LOCATION_GLOBAL)
        inputs['_locationRange'] = str(options.location_choice == StationOptions.LOCATION_BOX)
        inputs['_locationDistanceFromPoint'] = str(options.location_choice == StationOptions.LOCATION_POINT)
        return inputs

    def inputs_to_options(self, inputs):
        options = super(StationOptionsAdapter, self).inputs_to_options(inputs)
        if strtobool(options.get('_locationGlobal')):
            options['location_choice'] = StationOptions.LOCATION_GLOBAL
        elif strtobool(options.get('_locationRange')):
            options['location_choice'] = StationOptions.LOCATION_BOX
        elif strtobool(options.get('_locationDistanceFromPoint')):
            options['location_choice'] = StationOptions.LOCATION_POINT
        return options


class StationOptionsWidget(QtGui.QDialog, StationOptionsWidget.Ui_StationOptionsWidget):
    """
    Dialog window for event options used in creating a webservice query.
    """
    # Signal to indicate that the options have changed
    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(StationOptionsWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.adapter = StationOptionsAdapter(self)
        self.adapter.changed.connect(self.changed.emit)

        # Hook up the shortcut buttons
        self.time30DaysPushButton.clicked.connect(self.setTime30Days)
        self.time1YearPushButton.clicked.connect(self.setTime1Year)

    @QtCore.pyqtSlot(int)
    def onLocationButtonClicked(self, button_id):
        """
        Experimental code to enable/disable sections based on radio button
        """
        def enableItem(item, enabled):
            if isinstance(item, QtGui.QLayout):
                for i in range(item.count()):
                    enableItem(item.itemAt(i), enabled)
            elif hasattr(item, 'setEnabled'):
                item.setEnabled(enabled)
        enableItem(self.locationRangeLayout, button_id == 1)

    def setOptions(self, options):
        self.adapter.write_to_widget(options)

    @QtCore.pyqtSlot()
    def getOptions(self):
        return self.adapter.read_from_widget()

    def setTime30Days(self):
        """
        Set the start/end times to cover the last 30 days
        """
        end = QtCore.QDateTime.currentDateTimeUtc()
        start = end.addDays(-30)
        self.starttimeDateTimeEdit.setDateTime(start)
        self.endtimeDateTimeEdit.setDateTime(end)

    def setTime1Year(self):
        """
        Set the start/end times to cover the last 30 days
        """
        end = QtCore.QDateTime.currentDateTimeUtc()
        start = end.addYears(-1)
        self.starttimeDateTimeEdit.setDateTime(start)
        self.endtimeDateTimeEdit.setDateTime(end)
