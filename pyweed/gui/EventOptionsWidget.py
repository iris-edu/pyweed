from PyQt4 import QtGui, QtCore
from gui.uic import EventOptionsWidget
from gui.MyDoubleValidator import MyDoubleValidator
import logging
from obspy.core.utcdatetime import UTCDateTime
from distutils.util import strtobool
from utils import OptionsAdapter
from copy import copy
from events import EventOptions

LOGGER = logging.getLogger(__name__)


class EventOptionsAdapter(OptionsAdapter):
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
            '_timeDuringStations': widget.timeDuringStationsRadioButton,
            '_locationRange': widget.locationRangeRadioButton,
            '_locationDistanceFromPoint': widget.locationDistanceFromPointRadioButton,
            '_locationDistanceFromEvents': widget.locationDistanceFromEventsRadioButton,
        }

    def options_to_inputs(self, options):
        inputs = super(EventOptionsAdapter, self).options_to_inputs(options)
        # Set the radio buttons based on the EventOptions settings
        inputs['_timeBetween'] = str(options.time_choice == EventOptions.TIME_RANGE)
        inputs['_timeDuringStations'] = str(options.time_choice == EventOptions.TIME_STATIONS)
        inputs['_locationRange'] = str(options.location_choice == EventOptions.LOCATION_BOX)
        inputs['_locationDistanceFromPoint'] = str(options.location_choice == EventOptions.LOCATION_POINT)
        inputs['_locationDistanceFromEvents'] = str(options.location_choice == EventOptions.LOCATION_STATIONS)
        return inputs

    def inputs_to_options(self, inputs):
        options = super(EventOptionsAdapter, self).inputs_to_options(inputs)
        if options.get('_timeBetween'):
            options['time_choice'] = EventOptions.TIME_RANGE
        elif options.get('_timeDuringStations'):
            options['time_choice'] = EventOptions.TIME_STATIONS
        if options.get('_locationRange'):
            options['location_choice'] = EventOptions.LOCATION_BOX
        elif options.get('_locationDistanceFromPoint'):
            options['location_choice'] = EventOptions.LOCATION_POINT
        elif options.get('_locationDistanceFromEvents'):
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

#         # Initialize input fields using preferences
#         prefs = parent.preferences.EventOptions
#         self.minMagDoubleSpinBox.setValue(float(prefs.minmag))
#         self.maxMagDoubleSpinBox.setValue(float(prefs.maxmag))
#         self.minDepthDoubleSpinBox.setValue(float(prefs.mindepth))
#         self.maxDepthDoubleSpinBox.setValue(float(prefs.maxdepth))
#         self.locationRangeWestDoubleSpinBox.setValue(float(prefs.locationRangeWest))
#         self.locationRangeEastDoubleSpinBox.setValue(float(prefs.locationRangeEast))
#         self.locationRangeSouthDoubleSpinBox.setValue(float(prefs.locationRangeSouth))
#         self.locationRangeNorthDoubleSpinBox.setValue(float(prefs.locationRangeNorth))
#         self.distanceFromPointMinRadiusDoubleSpinBox.setValue(float(prefs.distanceFromPointMinRadius))
#         self.distanceFromPointMaxRadiusDoubleSpinBox.setValue(float(prefs.distanceFromPointMaxRadius))
#         self.distanceFromPointEastDoubleSpinBox.setValue(float(prefs.distanceFromPointEast))
#         self.distanceFromPointNorthDoubleSpinBox.setValue(float(prefs.distanceFromPointNorth))

        # Initialize the date selectors # TODO: using preferences
        #self.starttimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        #self.endtimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
#         today = QtCore.QDateTime.currentDateTimeUtc()
#         monthAgo = today.addMonths(-1)
#         self.starttimeDateTimeEdit.setDateTime(monthAgo)
#         self.endtimeDateTimeEdit.setDateTime(today)
#
#         # Intialize time and location type selection using preferences
#         getattr(self, prefs.selectedTimeButton).setChecked(True)
#         getattr(self, prefs.selectedLocationButton).setChecked(True)

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



