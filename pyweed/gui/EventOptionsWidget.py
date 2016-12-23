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
        self.minmagLineEdit.setValue(float(prefs.minmag))
        self.maxmagLineEdit.setText(prefs.maxmag)
        self.mindepthLineEdit.setText(prefs.mindepth)
        self.maxdepthLineEdit.setText(prefs.maxdepth)
        self.locationRangeWestLineEdit.setText(prefs.locationRangeWest)
        self.locationRangeEastLineEdit.setText(prefs.locationRangeEast)
        self.locationRangeSouthLineEdit.setText(prefs.locationRangeSouth)
        self.locationRangeNorthLineEdit.setText(prefs.locationRangeNorth)
        self.distanceFromPointMinRadiusLineEdit.setText(prefs.distanceFromPointMinRadius)
        self.distanceFromPointMaxRadiusLineEdit.setText(prefs.distanceFromPointMaxRadius)
        self.distanceFromPointEastLineEdit.setText(prefs.distanceFromPointEast)
        self.distanceFromPointNorthLineEdit.setText(prefs.distanceFromPointNorth)

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
        options['minmagnitude'] = str(self.minmagLineEdit.value())
        options['maxmagnitude'] = str(self.maxmagLineEdit.text())
        options['mindepth'] = str(self.mindepthLineEdit.text())
        options['maxdepth'] = str(self.maxdepthLineEdit.text())

        # catalog, type, and lat-lon ranges are optional
        #if str(self.catalogComboBox.currentText()) != 'All Catalogs':
            #options['catalog'] = str(self.type.currentText())
        if str(self.magtypeComboBox.currentText()) != 'All Types':
            options['magnitudetype'] = str(self.magtypeComboBox.currentText())
        if self.locationRangeRadioButton.isChecked():
            if str(self.locationRangeWestLineEdit.text()) != '':
                options['minlongitude'] = str(self.locationRangeWestLineEdit.text())
            if str(self.locationRangeEastLineEdit.text()) != '':
                options['maxlongitude'] = str(self.locationRangeEastLineEdit.text())
            if str(self.locationRangeSouthLineEdit.text()) != '':
                options['minlatitude'] = str(self.locationRangeSouthLineEdit.text())
            if str(self.locationRangeNorthLineEdit.text()) != '':
                options['maxlatitude'] = str(self.locationRangeNorthLineEdit.text())
        if self.locationDistanceFromPointRadioButton.isChecked():
            if str(self.distanceFromPointMinRadiusLineEdit.text()) != '':
                options['minradius'] = str(self.distanceFromPointMinRadiusLineEdit.text())
            if str(self.distanceFromPointMaxRadiusLineEdit.text()) != '':
                options['maxradius'] = str(self.distanceFromPointMaxRadiusLineEdit.text())
            if str(self.distanceFromPointEastLineEdit.text()) != '':
                options['longitude'] = str(self.distanceFromPointEastLineEdit.text())
            if str(self.distanceFromPointNorthLineEdit.text()) != '':
                options['latitude'] = str(self.distanceFromPointNorthLineEdit.text())

        return options


