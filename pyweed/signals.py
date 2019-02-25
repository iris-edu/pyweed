# -*- coding: utf-8 -*-
"""
Base classes standardizing some Qt signals.

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from PyQt5 import QtCore


# NOTE:  http://stackoverflow.com/questions/9957195/updating-gui-elements-in-multithreaded-pyqt
class SignalingThread(QtCore.QThread):
    """
    Mixin that serves to standardize how we use signals to pass information around
    """
    # Signal to indicate success
    done = QtCore.pyqtSignal(object)

    def __del__(self):
        self.wait()


class SignalingObject(QtCore.QObject):
    """
    Mixin for other objects that manage threaded work, and need to signal completion
    """
    # Signal to indicate success
    done = QtCore.pyqtSignal(object)
