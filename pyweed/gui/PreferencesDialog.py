# -*- coding: utf-8 -*-
"""
Preferences dialog

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from PyQt4 import QtGui
from pyweed.gui.uic import PreferencesDialog
from logging import getLogger
from obspy.clients.fdsn.header import URL_MAPPINGS
from obspy.clients.fdsn.client import Client

LOGGER = getLogger(__name__)


class PreferencesDialog(QtGui.QDialog, PreferencesDialog.Ui_PreferencesDialog):
    """
    Dialog window for editing preferences.
    """
    def __init__(self, pyweed, parent=None):
        super(PreferencesDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.pyweed = pyweed

        # Ordered list of all available data centers
        self.data_centers = sorted(URL_MAPPINGS.keys())

        # Put these in the comboboxes
        for data_center in self.data_centers:
            label = "%s: %s" % (data_center, URL_MAPPINGS[data_center])
            self.eventDataCenterComboBox.addItem(label, data_center)
            self.stationDataCenterComboBox.addItem(label, data_center)

        self.okButton.pressed.connect(self.accept)
        self.cancelButton.pressed.connect(self.reject)

    def showEvent(self, *args, **kwargs):
        """
        Perform any necessary initialization each time the dialog is opened
        """
        super(PreferencesDialog, self).showEvent(*args, **kwargs)
        # Indicate the currently selected data centers
        self.eventDataCenterComboBox.setCurrentIndex(self.data_centers.index(self.pyweed.event_data_center))
        self.stationDataCenterComboBox.setCurrentIndex(self.data_centers.index(self.pyweed.station_data_center))
        self.cacheSizeSpinBox.setValue(int(self.pyweed.preferences.Waveforms.cacheSize))

    def accept(self):
        """
        Validate and update the client
        """
        try:
            self.pyweed.set_event_data_center(
                self.data_centers[self.eventDataCenterComboBox.currentIndex()])
            self.pyweed.set_station_data_center(
                self.data_centers[self.stationDataCenterComboBox.currentIndex()])
        except Exception as e:
            # Error usually means that the user selected a data center that doesn't provide the given service
            QtGui.QMessageBox.critical(
                self,
                "Unable to update data center",
                str(e)
            )
            # Don't call super() which would close the preferences dialog
            return

        self.pyweed.preferences.Waveforms.cacheSize = self.cacheSizeSpinBox.value()

        return super(PreferencesDialog, self).accept()
