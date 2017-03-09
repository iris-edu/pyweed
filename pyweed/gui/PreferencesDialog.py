from PyQt4 import QtGui
from gui.uic import PreferencesDialog
from logging import getLogger
from obspy.clients.fdsn.header import URL_MAPPINGS

LOGGER = getLogger(__name__)


class PreferencesDialog(QtGui.QDialog, PreferencesDialog.Ui_PreferencesDialog):
    """
    Dialog window for editing preferences.
    """
    def __init__(self, pyweed=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.pyweed = pyweed

        # Create radio buttons for the data center options
        self.dataCenters = sorted(URL_MAPPINGS.keys())
        self.radioButtons = QtGui.QButtonGroup(self)
        layout = self.dataCentersGroupBox.layout()
        for idx, dataCenter in enumerate(self.dataCenters):
            button = QtGui.QRadioButton(dataCenter)
            layout.addWidget(button)
            self.radioButtons.addButton(button, idx)

        self.okButton.pressed.connect(self.accept)
        self.cancelButton.pressed.connect(self.reject)

    def getSelectedDataCenter(self):
        return self.dataCenters[self.radioButtons.checkedId()]
