# -*- coding: utf-8 -*-
"""
Dialog showing logging information.

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from PyQt4 import QtGui
from pyweed.gui.uic import LoggingDialog
from pyweed.gui.MyTextEditLoggingHandler import MyTextEditLoggingHandler
import logging


class LoggingDialog(QtGui.QDialog, LoggingDialog.Ui_LoggingDialog):
    """
    Dialog window displaying all logs.
    """
    def __init__(self, parent=None):
        super(LoggingDialog, self).__init__(parent=parent)
        self.setupUi(self)
        self.setWindowTitle('Logs')

        # Initialize loggingPlainTextEdit
        self.loggingPlainTextEdit.setReadOnly(True)

        # Add a widget logging handler to the logger
        loggingHandler = MyTextEditLoggingHandler(widget=self.loggingPlainTextEdit)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        loggingHandler.setFormatter(formatter)

        logging.getLogger().addHandler(loggingHandler)
