from PyQt4 import QtGui, QtCore
from gui.uic import StationOptionsWidget
import logging

LOGGER = logging.getLogger(__name__)


class StationOptionsWidget(QtGui.QDialog, StationOptionsWidget.Ui_StationOptionsWidget):
    """
    Dialog window for event options used in creating a webservice query.
    """
    def __init__(self, pyweed, parent=None):
        super(self.__class__, self).__init__(parent=parent)
        self.setupUi(self)

        # Initialize input fields using preferences
        prefs = pyweed.preferences.StationOptions
        self.networkLineEdit.setText(prefs.network)
        self.stationLineEdit.setText(prefs.station)
        self.locationLineEdit.setText(prefs.location)
        self.channelLineEdit.setText(prefs.channel)
        self.locationRangeWestDoubleSpinBox.setValue(float(prefs.locationRangeWest))
        self.locationRangeEastDoubleSpinBox.setValue(float(prefs.locationRangeEast))
        self.locationRangeSouthDoubleSpinBox.setValue(float(prefs.locationRangeSouth))
        self.locationRangeNorthDoubleSpinBox.setValue(float(prefs.locationRangeNorth))
        self.distanceFromPointMinRadiusDoubleSpinBox.setValue(float(prefs.distanceFromPointMinRadius))
        self.distanceFromPointMaxRadiusDoubleSpinBox.setValue(float(prefs.distanceFromPointMaxRadius))
        self.distanceFromPointEastDoubleSpinBox.setValue(float(prefs.distanceFromPointEast))
        self.distanceFromPointNorthDoubleSpinBox.setValue(float(prefs.distanceFromPointNorth))

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
            if str(self.locationRangeWestDoubleSpinBox.text()) != '':
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
