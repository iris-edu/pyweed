from PyQt4 import QtGui, QtCore
from gui.uic import StationOptionsWidget
import logging
from gui.utils import OptionsAdapter
from station_options import StationOptions

LOGGER = logging.getLogger(__name__)


class StationOptionsAdapter(OptionsAdapter):
    def connect_to_widget(self, widget):
        self.inputs = {
            'starttime': widget.starttimeDateTimeEdit,
            'endtime': widget.endtimeDateTimeEdit,
            'minmagnitude': widget.minMagDoubleSpinBox,
            'maxmagnitude': widget.maxMagDoubleSpinBox,
            'mindepth': widget.minDepthDoubleSpinBox,
            'maxdepth': widget.maxDepthDoubleSpinBox,
            'magnitudetype': widget.magTypeComboBox,
            'minlongitude': widget.locationRangeWestDoubleSpinBox,
            'maxlongitude': widget.locationRangeEastDoubleSpinBox,
            'minlatitude': widget.locationRangeSouthDoubleSpinBox,
            'maxlatitude': widget.locationRangeNorthDoubleSpinBox,
            'minradius': widget.distanceFromPointMinRadiusDoubleSpinBox,
            'maxradius': widget.distanceFromPointMaxRadiusDoubleSpinBox,
            'longitude': widget.distanceFromPointEastDoubleSpinBox,
            'latitude': widget.distanceFromPointNorthDoubleSpinBox,
            '_timeBetween': widget.timeBetweenRadioButton,
            '_timeDuringEvents': widget.timeDuringEventsRadioButton,
            '_locationRange': widget.locationRangeRadioButton,
            '_locationDistanceFromPoint': widget.locationDistanceFromPointRadioButton,
            '_locationDistanceFromEvents': widget.locationDistanceFromEventsRadioButton,
        }

    def options_to_inputs(self, options):
        inputs = super(StationOptionsAdapter, self).options_to_inputs(options)
        # Set the radio buttons based on the EventOptions settings
        inputs['_timeBetween'] = str(options.time_choice == StationOptions.TIME_RANGE)
        inputs['_timeDuringStations'] = str(options.time_choice == StationOptions.TIME_EVENTS)
        inputs['_locationRange'] = str(options.location_choice == StationOptions.LOCATION_BOX)
        inputs['_locationDistanceFromPoint'] = str(options.location_choice == StationOptions.LOCATION_POINT)
        inputs['_locationDistanceFromEvents'] = str(options.location_choice == StationOptions.LOCATION_EVENTS)
        return inputs

    def inputs_to_options(self, inputs):
        options = super(StationOptionsAdapter, self).inputs_to_options(inputs)
        if options.get('_timeBetween'):
            options['time_choice'] = StationOptions.TIME_RANGE
        elif options.get('_timeDuringStations'):
            options['time_choice'] = StationOptions.TIME_EVENTS
        if options.get('_locationRange'):
            options['location_choice'] = StationOptions.LOCATION_BOX
        elif options.get('_locationDistanceFromPoint'):
            options['location_choice'] = StationOptions.LOCATION_POINT
        elif options.get('_locationDistanceFromEvents'):
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
