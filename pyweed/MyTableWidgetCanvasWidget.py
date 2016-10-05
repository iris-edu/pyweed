# Custom Widget that embeds a Qt4MplCanvas
#
# To be inserted into the QTableWidget with setCellWidget() instead of setItem().
#
# http://stackoverflow.com/questions/5553342/adding-images-to-a-qtablewidget-in-pyqt

from PyQt4 import QtCore
from PyQt4 import QtGui

from qt4mplcanvas import Qt4MplCanvas

class MyTableWidgetCanvasWidget (QtGui.QWidget):
    """
    Custom Widget that embeds a Qt4MplCanvas
    
    To be inserted into the QTableWidget with setCellWidget() instead of setItem().

    http://stackoverflow.com/questions/5553342/adding-images-to-a-qtablewidget-in-pyqt
    """

    def __init__(self, parent=None, stream=None):
        super(MyTableWidgetCanvasWidget, self).__init__(parent)
        self.setMinimumSize(QtCore.QSize(500, 200))
        self.resize(QtCore.QSize(500, 200))
        self.canvas = Qt4MplCanvas(self)
        self.canvas.setMinimumSize(QtCore.QSize(500, 200))
        self.canvas.setObjectName(QtCore.QString("canvas1"))
        self.stream = stream
        self.stream.plot(fig=self.canvas.fig)
        self.canvas.fig.canvas.draw()

    def paintEvent(self, event):
        self.stream.plot(fig=self.canvas.fig)
        self.canvas.fig.canvas.draw()
        
