from PyQt4 import QtCore


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
    # Signal to indicate success
    done = QtCore.pyqtSignal(object)
