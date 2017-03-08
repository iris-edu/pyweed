from PyQt4 import QtGui, QtCore
from gui.uic import EventOptionsWidget
import logging
from distutils.util import strtobool
from utils import OptionsAdapter
from event_options import EventOptions

LOGGER = logging.getLogger(__name__)


class EventOptionsAdapter(OptionsAdapter):
    def connect_to_widget(self, widget):
        # Map widget inputs to options
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
            '_timeFromStations': widget.timeFromStationsRadioButton,
            '_locationGlobal': widget.locationGlobalRadioButton,
            '_locationRange': widget.locationRangeRadioButton,
            '_locationDistanceFromPoint': widget.locationDistanceFromPointRadioButton,
            '_locationFromStations': widget.locationFromStationsRadioButton,
        }

    def options_to_inputs(self, options):
        inputs = super(EventOptionsAdapter, self).options_to_inputs(options)
        # Set the radio buttons based on the EventOptions settings
        inputs['_timeBetween'] = str(options.time_choice == EventOptions.TIME_RANGE)
        inputs['_timeFromStations'] = str(options.time_choice == EventOptions.TIME_STATIONS)
        inputs['_locationGlobal'] = str(options.location_choice == EventOptions.LOCATION_GLOBAL)
        inputs['_locationRange'] = str(options.location_choice == EventOptions.LOCATION_BOX)
        inputs['_locationDistanceFromPoint'] = str(options.location_choice == EventOptions.LOCATION_POINT)
        inputs['_locationFromStations'] = str(options.location_choice == EventOptions.LOCATION_STATIONS)
        return inputs

    def inputs_to_options(self, inputs):
        options = super(EventOptionsAdapter, self).inputs_to_options(inputs)
        # Set various options based on radio button selections
        if strtobool(options.get('_timeBetween')):
            options['time_choice'] = EventOptions.TIME_RANGE
        elif strtobool(options.get('_timeFromStations')):
            options['time_choice'] = EventOptions.TIME_STATIONS
        if strtobool(options.get('_locationGlobal')):
            options['location_choice'] = EventOptions.LOCATION_GLOBAL
        elif strtobool(options.get('_locationRange')):
            options['location_choice'] = EventOptions.LOCATION_BOX
        elif strtobool(options.get('_locationDistanceFromPoint')):
            options['location_choice'] = EventOptions.LOCATION_POINT
        elif strtobool(options.get('_locationFromStations')):
            options['location_choice'] = EventOptions.LOCATION_STATIONS
        return options


class EventOptionsWidget(QtGui.QDialog, EventOptionsWidget.Ui_EventOptionsWidget):
    """
    Dialog window for event options used in creating a webservice query.
    """
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent=parent)
        self.setupUi(self)

        self.adapter = EventOptionsAdapter()
        self.adapter.connect_to_widget(self)

        # Hook up the shortcut buttons
        self.time30DaysPushButton.clicked.connect(self.setTime30Days)
        self.time1YearPushButton.clicked.connect(self.setTime1Year)

    def setOptions(self, options):
        self.adapter.write_to_widget(options)

    @QtCore.pyqtSlot()
    def getOptions(self):
        """
        Return a dictionary containing everything specified in the EventQueryDialog.
        All dictionary values are properly formatted for use in querying event services.

        Names of event options must match argument names defined here:
          https://docs.obspy.org/packages/autogen/obspy.clients.fdsn.client.Client.get_events.html
        """
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
