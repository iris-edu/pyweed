#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

# Basic packages
import sys
import logging

# For debugging, raise an exception on attempted chained assignment
# See http://pandas.pydata.org/pandas-docs/version/0.19.1/indexing.html#returning-a-view-versus-a-copy
import pandas as pd
pd.set_option('mode.chained_assignment', 'raise')

# Configure PyQt4 -- in order for the Python console to work, we need to load a particular
# version of some internal libraries. This must be done before the first import of the PyQt4 libraries.
# See http://stackoverflow.com/questions/11513132/embedding-ipython-qt-console-in-a-pyqt-application/20610786#20610786
import os
os.environ['QT_API'] = 'pyqt'
import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)
from PyQt4 import QtCore
from PyQt4 import QtGui

# Configure matplotlib backend
import matplotlib
matplotlib.use('AGG')

# Pyweed UI components
from gui.MainWindow import MainWindow
from preferences import Preferences


__appName__ = "PYWEED"
__version__ = "0.1.0"


LOGGER = logging.getLogger(__name__)


class NoConsoleLoggingFilter(logging.Filter):
    """
    Logging filter that excludes the (very noisy) output from the attached Python console
    """
    exclude = ('ipykernel', 'traitlets',)
    def filter(self, record):
        for exclude in self.exclude:
            if record.name.startswith(exclude):
                return False
        return True


class PyWEED(object):

    def __init__(self, app):
        self.app = app
        self.configure_logging()
        self.preferences = self.get_preferences()

    def get_preferences(self):
        # Load configurable preferences from ~/.pyweed/config.ini
        preferences = Preferences()
        try:
            preferences.load()
        except Exception as e:
            LOGGER.error("Unable to load configuration preferences -- using defaults.\n%s", e)
        return preferences

    def configure_logging(self):
        """
        Configure the root logger
        """
        logger = logging.getLogger()
        try:
            log_level = getattr(logging, self.preferences.Logging.level)
            logger.setLevel(log_level)
        except Exception as e:
            logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        handler.addFilter(NoConsoleLoggingFilter())
        logger.addHandler(handler)

    def start_gui(self):
        self.gui = MainWindow(__appName__, __version__, self.preferences)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    pyweed = PyWEED(app)
    pyweed.start_gui()
    sys.exit(app.exec_())

