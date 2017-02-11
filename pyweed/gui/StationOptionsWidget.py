from PyQt4 import QtGui, QtCore
from gui.uic import StationOptionsWidget
import logging
from gui.utils import OptionsAdapter
from station_options import StationOptions
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
            '_timeBetween': widget.timeBetweenRadioButton,
            '_timeFromEvents': widget.timeFromEventsRadioButton,
            '_locationGlobal': widget.locationGlobalRadioButton,
            '_locationRange': widget.locationRangeRadioButton,
            '_locationDistanceFromPoint': widget.locationDistanceFromPointRadioButton,
            '_locationFromEvents': widget.locationFromEventsRadioButton,
        }

    def options_to_inputs(self, options):
        inputs = super(StationOptionsAdapter, self).options_to_inputs(options)
        # Set the radio buttons based on the EventOptions settings
        inputs['_timeBetween'] = str(options.time_choice == StationOptions.TIME_RANGE)
        inputs['_timeFromEvents'] = str(options.time_choice == StationOptions.TIME_EVENTS)
        inputs['_locationGlobal'] = str(options.location_choice == StationOptions.LOCATION_GLOBAL)
        inputs['_locationRange'] = str(options.location_choice == StationOptions.LOCATION_BOX)
        inputs['_locationDistanceFromPoint'] = str(options.location_choice == StationOptions.LOCATION_POINT)
        inputs['_locationFromEvents'] = str(options.location_choice == StationOptions.LOCATION_EVENTS)
        return inputs

    def inputs_to_options(self, inputs):
        options = super(StationOptionsAdapter, self).inputs_to_options(inputs)
        if strtobool(options.get('_timeBetween')):
            options['time_choice'] = StationOptions.TIME_RANGE
        elif strtobool(options.get('_timeFromEvents')):
            options['time_choice'] = StationOptions.TIME_EVENTS
        if strtobool(options.get('_locationGlobal')):
            options['location_choice'] = StationOptions.LOCATION_GLOBAL
        elif strtobool(options.get('_locationRange')):
            options['location_choice'] = StationOptions.LOCATION_BOX
        elif strtobool(options.get('_locationDistanceFromPoint')):
            options['location_choice'] = StationOptions.LOCATION_POINT
        elif strtobool(options.get('_locationFromEvents')):
            options['location_choice'] = StationOptions.LOCATION_EVENTS
        return options


class StationOptionsWidget(QtGui.QDialog, StationOptionsWidget.Ui_StationOptionsWidget):
    """
    Dialog window for event options used in creating a webservice query.
    """
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent=parent)
        self.setupUi(self)

        self.adapter = StationOptionsAdapter()
        self.adapter.connect_to_widget(self)

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
