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
import time # TODO:  remove?

# Vectors and dataframes
import numpy as np
import pandas as pd

# PyQt4 packages
import os
os.environ['QT_API'] = 'pyqt'
import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)
from PyQt4 import QtCore
from PyQt4 import QtGui

# Pyweed UI components
from gui.MainWindow import MainWindow


__appName__ = "PYWEED"
__version__ = "0.1.0"


LOGGER = logging.getLogger(__name__)



# ----- Request/Response watchers ----------------------------------------------

# NOTE:  http://stackoverflow.com/questions/9957195/updating-gui-elements-in-multithreaded-pyqt
class waveformResponseWatcherThread(QtCore.QThread):
    """
    This thread is started when the WaveformsDialog initializes.

    When a message appears on the waveformResponseQueue, this thread
    emits a waveformResponseSignal which then triggers waveformResponseHandler().
    """
    waveformResponseSignal = QtCore.pyqtSignal()

    def __init__(self, waveformResponseQueue):
        QtCore.QThread.__init__(self)
        self.waveformResponseQueue = waveformResponseQueue

    def run(self):
        """
        Wait for entries to appear on the queue and then signal the main
        thread that data are available.
        """
        while True:
            # NOTE:  A small sleep gives the main thread a chance to respond to GUI events
            time.sleep(0.2)
            if not self.waveformResponseQueue.empty():
                self.waveformResponseSignal.emit()


# NOTE:  http://stackoverflow.com/questions/9957195/updating-gui-elements-in-multithreaded-pyqt
class waveformRequestWatcherThread(QtCore.QThread):
    """
    This thread is started when the WaveformsDialog initializes.

    When a message appears on the waveformRequestQueue, this thread
    emits a waveformRequestSignal which then triggers waveformRequestHandler().
    """
    waveformRequestSignal = QtCore.pyqtSignal()

    def __init__(self, waveformRequestQueue):
        QtCore.QThread.__init__(self)
        self.waveformRequestQueue = waveformRequestQueue

    def run(self):
        """
        Wait for entries to appear on the queue and then signal the main
        thread that a request has been made.
        """
        while True:
            # NOTE:  A small sleep gives the main thread a chance to respond to GUI events
            time.sleep(0.2)
            if not self.waveformRequestQueue.empty():
                self.waveformRequestSignal.emit()


# ----- Splash Screen ------------------------------------------------------------

# ----- Main Window ------------------------------------------------------------



if __name__ == "__main__":
    pd.set_option('mode.chained_assignment','raise')
    app = QtGui.QApplication(sys.argv)
    # app.setStyleSheet(stylesheet)
    GUI = MainWindow(__appName__, __version__)
    sys.exit(app.exec_())

