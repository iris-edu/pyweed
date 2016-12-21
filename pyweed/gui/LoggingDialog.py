from PyQt4 import QtGui
from gui.uic import LoggingDialog
from gui.MyTextEditLoggingHandler import MyTextEditLoggingHandler
import logging


class LoggingDialog(QtGui.QDialog, LoggingDialog.Ui_LoggingDialog):
    """
    Dialog window displaying all logs.
    """
    def __init__(self, parent=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Logs')

        # Initialize loggingPlainTextEdit
        self.loggingPlainTextEdit.setReadOnly(True)

        # Add a widget logging handler to the logger
        loggingHandler = MyTextEditLoggingHandler(widget=self.loggingPlainTextEdit)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        loggingHandler.setFormatter(formatter)

        logging.getLogger().addHandler(loggingHandler)


