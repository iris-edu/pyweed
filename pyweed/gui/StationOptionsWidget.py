from PyQt4 import QtGui, QtCore
from gui.uic import StationOptionsWidget
import logging

LOGGER = logging.getLogger(__name__)


class StationOptionsWidget(QtGui.QDialog, StationOptionsWidget.Ui_StationOptionsWidget):
    """
    Dialog window for event options used in creating a webservice query.
    """
    def __init__(self, parent=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        # Initialize input fields using preferences
        prefs = parent.preferences.StationOptions
        self.networkLineEdit.setText(prefs.network)
        self.stationLineEdit.setText(prefs.station)
        self.locationLineEdit.setText(prefs.location)
        self.channelLineEdit.setText(prefs.channel)
        self.locationRangeWestLineEdit.setText(prefs.locationRangeWest)
        self.locationRangeEastLineEdit.setText(prefs.locationRangeEast)
        self.locationRangeSouthLineEdit.setText(prefs.locationRangeSouth)
        self.locationRangeNorthLineEdit.setText(prefs.locationRangeNorth)
        self.distanceFromPointMinRadiusLineEdit.setText(prefs.distanceFromPointMinRadius)
        self.distanceFromPointMaxRadiusLineEdit.setText(prefs.distanceFromPointMaxRadius)
        self.distanceFromPointEastLineEdit.setText(prefs.distanceFromPointEast)
        self.distanceFromPointNorthLineEdit.setText(prefs.distanceFromPointNorth)

        # Initialize the date selectors # TODO: using preferences
        #self.starttimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss')
        #self.endtimeDateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss')
        today = QtCore.QDateTime.currentDateTimeUtc()
        monthAgo = today.addMonths(-1)
        self.starttimeDateTimeEdit.setDateTime(monthAgo)
        self.endtimeDateTimeEdit.setDateTime(today)

        # TODO:  Intialize time and location type selection using preferences
        getattr(self, prefs.selectedTimeButton).setChecked(True)
        getattr(self, prefs.selectedLocationButton).setChecked(True)

    @QtCore.pyqtSlot(int)
    def onLocationButtonClicked(self, button_id):
        def enableItem(item, enabled):
            if isinstance(item, QtGui.QLayout):
                for i in range(item.count()):
                    enableItem(item.itemAt(i), enabled)
            elif hasattr(item, 'setEnabled'):
                item.setEnabled(enabled)
        enableItem(self.locationRangeLayout, button_id == 1)

    @QtCore.pyqtSlot()
    def getOptions(self):
        """
        Return a dictionary containing everything specified in the StationQueryDialog.
        All dictionary values are properly formatted for use in querying station services.

        # NOTE:  Names of event options must match argument names defined here:
        # NOTE:    https://docs.obspy.org/packages/autogen/obspy.clients.fdsn.client.Client.get_stations.html
        """
        options = {}

        # times, magnitudes and depths are all guaranteed to be present
        options['starttime'] = str(self.starttimeDateTimeEdit.text()).rstrip(' UTC').replace(' ','T')
        options['endtime'] = str(self.endtimeDateTimeEdit.text()).rstrip(' UTC').replace(' ','T')

        # SNCL and lat-lon ranges are optional
        if str(self.networkLineEdit.text()) != '':
            options['network'] = str(self.networkLineEdit.text())
        if str(self.networkLineEdit.text()) != '':
            options['station'] = str(self.stationLineEdit.text())
        if str(self.stationLineEdit.text()) != '':
            options['location'] = str(self.locationLineEdit.text())
        if str(self.locationLineEdit.text()) != '':
            options['channel'] = str(self.channelLineEdit.text())
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
