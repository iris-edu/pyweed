# Custom QTableWidgetItem with a matplotlib canvas
#

from PyQt4 import QtCore
from PyQt4 import QtGui

from qt4mplcanvas import Qt4MplCanvas

class MyCanvasTableWidgetItem (QtGui.QTableWidgetItem):
    """
    Custom QTableWidgetItem with a matplotlib canvas
    """

    def __init__ (self):
        super(MyCanvasTableWidgetItem, self).__init__()
        self.waveform_canvas = Qt4MplCanvas(self)
        self.waveform_canvas.setSizePolicy(sizePolicy)
        self.waveform_canvas.setMinimumSize(QtCore.QSize(600, 200))
