from PyQt4 import QtGui, QtCore
from gui.uic import EventOptionsWidget
from gui.MyDoubleValidator import MyDoubleValidator
import logging

LOGGER = logging.getLogger(__name__)


class EventOptionsWidget(QtGui.QDialog, EventOptionsWidget.Ui_EventOptionsWidget):
    """
    Dialog window for event options used in creating a webservice query.
    """
    def __init__(self, parent=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

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

    @QtCore.pyqtSlot()
    def getOptions(self):
        """
        Return a dictionary containing everything specified in the EventQueryDialog.
        All dictionary values are properly formatted for use in querying event services.

        Names of event options must match argument names defined here:
          https://docs.obspy.org/packages/autogen/obspy.clients.fdsn.client.Client.get_events.html
        """
        options = {}

        # times, magnitudes and depths are all guaranteed to be present
        options['starttime'] = str(self.starttimeDateTimeEdit.text()).rstrip(' UTC').replace(' ','T')
        options['endtime'] = str(self.endtimeDateTimeEdit.text()).rstrip(' UTC').replace(' ','T')
        options['minmagnitude'] = str(self.minMagDoubleSpinBox.value())
        options['maxmagnitude'] = str(self.maxMagDoubleSpinBox.value())
        options['mindepth'] = str(self.minDepthDoubleSpinBox.value())
        options['maxdepth'] = str(self.maxDepthDoubleSpinBox.value())

        # catalog, type, and lat-lon ranges are optional
        #if str(self.catalogComboBox.currentText()) != 'All Catalogs':
            #options['catalog'] = str(self.type.currentText())
        if str(self.magTypeComboBox.currentText()) != 'All Types':
            options['magnitudetype'] = str(self.magTypeComboBox.currentText())
        if self.locationRangeRadioButton.isChecked():
            if str(self.locationRangeWestDoubleSpinBox.value()) != '':
                options['minlongitude'] = str(self.locationRangeWestDoubleSpinBox.text())
            if str(self.locationRangeEastDoubleSpinBox.text()) != '':
                options['maxlongitude'] = str(self.locationRangeEastDoubleSpinBox.text())
            if str(self.locationRangeSouthDoubleSpinBox.text()) != '':
                options['minlatitude'] = str(self.locationRangeSouthDoubleSpinBox.text())
            if str(self.locationRangeNorthDoubleSpinBox.text()) != '':
                options['maxlatitude'] = str(self.locationRangeNorthDoubleSpinBox.text())
        if self.locationDistanceFromPointRadioButton.isChecked():
            if str(self.distanceFromPointMinRadiusDoubleSpinBox.text()) != '':
                options['minradius'] = str(self.distanceFromPointMinRadiusDoubleSpinBox.text())
            if str(self.distanceFromPointMaxRadiusDoubleSpinBox.text()) != '':
                options['maxradius'] = str(self.distanceFromPointMaxRadiusDoubleSpinBox.text())
            if str(self.distanceFromPointEastDoubleSpinBox.text()) != '':
                options['longitude'] = str(self.distanceFromPointEastDoubleSpinBox.text())
            if str(self.distanceFromPointNorthDoubleSpinBox.text()) != '':
                options['latitude'] = str(self.distanceFromPointNorthDoubleSpinBox.text())

        return options


