# -*- coding: utf-8 -*-
"""
Preferences dialog

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from PyQt5 import QtWidgets
from pyweed.gui.uic import PreferencesDialog
from logging import getLogger
from obspy.clients.fdsn.header import URL_MAPPINGS
from pyweed.preferences import safe_int
from pyweed.gui.Adapters import ComboBoxAdapter


LOGGER = getLogger(__name__)


class PreferencesDialog(QtWidgets.QDialog, PreferencesDialog.Ui_PreferencesDialog):
    """
    Dialog window for editing preferences.
    """
    def __init__(self, pyweed, parent=None):
        super(PreferencesDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.pyweed = pyweed

        # Ordered list of all available data centers
        dcs = sorted(URL_MAPPINGS.keys())

        self.eventDataCenterAdapter = ComboBoxAdapter(
            self.eventDataCenterComboBox,
            [(dc, URL_MAPPINGS[dc]) for dc in dcs]
        )

        self.stationDataCenterAdapter = ComboBoxAdapter(
            self.stationDataCenterComboBox,
            [(dc, URL_MAPPINGS[dc]) for dc in dcs]
        )

        self.okButton.pressed.connect(self.accept)
        self.cancelButton.pressed.connect(self.reject)

    def showEvent(self, *args, **kwargs):
        """
        Perform any necessary initialization each time the dialog is opened
        """
        super(PreferencesDialog, self).showEvent(*args, **kwargs)
        # Indicate the currently selected data centers
        self.eventDataCenterAdapter.setValue(
            self.pyweed.event_data_center
        )
        self.stationDataCenterAdapter.setValue(
            self.pyweed.station_data_center
        )
        self.cacheSizeSpinBox.setValue(
            safe_int(self.pyweed.preferences.Waveforms.cacheSize, 10)
        )

    def accept(self):
        """
        Validate and update the client
        """
        try:
            self.pyweed.set_event_data_center(
                self.eventDataCenterAdapter.getValue()
            )
            self.pyweed.set_station_data_center(
                self.stationDataCenterAdapter.getValue()
            )
        except Exception as e:
            # Error usually means that the user selected a data center that doesn't provide the given service
            QtWidgets.QMessageBox.critical(
                self,
                "Unable to update data center",
                str(e)
            )
            # Don't call super() which would close the preferences dialog
            return

        self.pyweed.preferences.Waveforms.cacheSize = self.cacheSizeSpinBox.value()

        return super(PreferencesDialog, self).accept()
