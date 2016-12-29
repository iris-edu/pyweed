from PyQt4 import QtGui, QtCore
from gui.uic import EventOptionsWidget
from gui.MyDoubleValidator import MyDoubleValidator
import logging
from obspy.core.utcdatetime import UTCDateTime
from distutils.util import strtobool

LOGGER = logging.getLogger(__name__)


class EventOptionsWidget(QtGui.QDialog, EventOptionsWidget.Ui_EventOptionsWidget):
    """
    Dialog window for event options used in creating a webservice query.
    """
    def __init__(self, parent=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.inputs = {
            'starttime': self.starttimeDateTimeEdit,
            'endtime': self.endtimeDateTimeEdit,
            'minmagnitude': self.minMagDoubleSpinBox,
            'maxmagnitude': self.maxMagDoubleSpinBox,
            'mindepth': self.minDepthDoubleSpinBox,
            'maxdepth': self.maxDepthDoubleSpinBox,
            'magnitudetype': self.magTypeComboBox,
            'minlongitude': self.locationRangeWestDoubleSpinBox,
            'maxlongitude': self.locationRangeEastDoubleSpinBox,
            'minlatitude': self.locationRangeSouthDoubleSpinBox,
            'maxlatitude': self.locationRangeNorthDoubleSpinBox,
            'minradius': self.distanceFromPointMinRadiusDoubleSpinBox,
            'maxradius': self.distanceFromPointMaxRadiusDoubleSpinBox,
            'longitude': self.distanceFromPointEastDoubleSpinBox,
            'latitude': self.distanceFromPointNorthDoubleSpinBox,
            '_timeBetween': self.timeBetweenRadioButton,
            '_timeDuringStations': self.timeDuringStationsRadioButton,
            '_locationRange': self.locationRangeRadioButton,
            '_locationDistanceFromPoint': self.locationDistanceFromPointRadioButton,
            '_locationDistanceFromEvents': self.locationDistanceFromEventsRadioButton,
        }

        # Initialize input fields using preferences
        prefs = parent.preferences.EventOptions
        self.minMagDoubleSpinBox.setValue(float(prefs.minmag))
        self.maxMagDoubleSpinBox.setValue(float(prefs.maxmag))
        self.minDepthDoubleSpinBox.setValue(float(prefs.mindepth))
        self.maxDepthDoubleSpinBox.setValue(float(prefs.maxdepth))
        self.locationRangeWestDoubleSpinBox.setValue(float(prefs.locationRangeWest))
        self.locationRangeEastDoubleSpinBox.setValue(float(prefs.locationRangeEast))
        self.locationRangeSouthDoubleSpinBox.setValue(float(prefs.locationRangeSouth))
        self.locationRangeNorthDoubleSpinBox.setValue(float(prefs.locationRangeNorth))
        self.distanceFromPointMinRadiusDoubleSpinBox.setValue(float(prefs.distanceFromPointMinRadius))
        self.distanceFromPointMaxRadiusDoubleSpinBox.setValue(float(prefs.distanceFromPointMaxRadius))
        self.distanceFromPointEastDoubleSpinBox.setValue(float(prefs.distanceFromPointEast))
        self.distanceFromPointNorthDoubleSpinBox.setValue(float(prefs.distanceFromPointNorth))

        # Initialize the date selectors # TODO: using preferences
        #self.starttimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        #self.endtimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss UTC')
        today = QtCore.QDateTime.currentDateTimeUtc()
        monthAgo = today.addMonths(-1)
        self.starttimeDateTimeEdit.setDateTime(monthAgo)
        self.endtimeDateTimeEdit.setDateTime(today)

        # Intialize time and location type selection using preferences
        getattr(self, prefs.selectedTimeButton).setChecked(True)
        getattr(self, prefs.selectedLocationButton).setChecked(True)

    def setOptions(self, options):
        for k, v in options.iteritems():
            input = self.inputs.get(k)
            if input:
                if isinstance(input, QtGui.QDateTimeEdit):
                    # Ugh, complicated conversion from UTCDateTime
                    dt = QtCore.QDateTime.fromString(v, QtCore.Qt.ISODate)
                    input.setDateTime(dt)
                elif isinstance(input, QtGui.QDoubleSpinBox):
                    # Float value
                    input.setValue(float(v))
                elif isinstance(input, QtGui.QComboBox):
                    # Combo box
                    index = input.findText(v)
                    if index > -1:
                        input.setCurrentIndex(index)
                elif isinstance(input, QtGui.QLineEdit):
                    # Text input
                    input.setText(v)
                elif isinstance(input, QtGui.QAbstractButton):
                    # Radio/checkbox button
                    input.setChecked(strtobool(v))
                else:
                    LOGGER.warning("Don't know how to read option %s (%s)", k, v)

    @QtCore.pyqtSlot()
    def getOptions(self):
        """
        Return a dictionary containing everything specified in the EventQueryDialog.
        All dictionary values are properly formatted for use in querying event services.

        Names of event options must match argument names defined here:
          https://docs.obspy.org/packages/autogen/obspy.clients.fdsn.client.Client.get_events.html
        """
        options = {}
        for k, input in self.inputs.iteritems():
            if isinstance(input, QtGui.QDateTimeEdit):
                # DateTime
                options[k] = input.dateTime().toString(QtCore.Qt.ISODate)
            elif isinstance(input, QtGui.QAbstractButton):
                # Radio/checkbox button
                options[k] = str(input.isChecked())
            elif hasattr(input, 'text'):
                options[k] = input.text()
            else:
                LOGGER.warning("Don't know how to write input %s (%s)", k, input)

        return options



