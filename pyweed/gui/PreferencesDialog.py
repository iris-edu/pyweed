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

        # Create radio buttons for the data center options
        self.data_centers = sorted(URL_MAPPINGS.keys())
        self.radioButtons = QtGui.QButtonGroup(self)
        layout = self.dataCentersGroupBox.layout()
        for idx, data_center in enumerate(self.data_centers):
            button = QtGui.QRadioButton(data_center)
            layout.addWidget(button)
            self.radioButtons.addButton(button, idx)

        self.okButton.pressed.connect(self.accept)
        self.cancelButton.pressed.connect(self.reject)

    def showEvent(self, *args, **kwargs):
        """
        Perform any necessary initialization each time the dialog is opened
        """
        super(PreferencesDialog, self).showEvent(*args, **kwargs)
        # Indicate the currently selected data center
        try:
            idx = self.data_centers.index(self.pyweed.data_center)
            button = self.radioButtons.button(idx)
            if button:
                button.setChecked(True)
        except ValueError:
            pass

    def accept(self):
        """
        Validate and update the client
        """
        data_center = self.data_centers[self.radioButtons.checkedId()]
        if data_center != self.pyweed.data_center:
            client = Client(data_center)
            # If the data center doesn't provide all the necessary services, show an error
            missing_services = [
                service for service in ('event', 'station', 'dataselect')
                if service not in client.services
            ]
            if missing_services:
                missing_services_str = ", ".join(missing_services)
                QtGui.QMessageBox.critical(
                    self,
                    "Missing services",
                    "This data center doesn't provide one or more services:\n%s" % missing_services_str
                )
                # Don't call super() which would close the preferences dialog
                return
            else:
                self.pyweed.data_center = data_center
                self.pyweed.client = client

        return super(PreferencesDialog, self).accept()
