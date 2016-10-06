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

    def __init__(self, parent=None, width=100, height=100, plottable=None):
        super(MyTableWidgetCanvasWidget, self).__init__(parent)
        self.plottable = plottable
                
        ### Set up Matplotlib canvas
        ##self.setMinimumSize(QtCore.QSize(width, height))
        ##self.canvas = Qt4MplCanvas(self)
        ##self.canvas.setObjectName(QtCore.QString("canvas1")) # TODO:  Is this needed?
        ### Keep a reference to the figure and adjust the size
        ##self.fig = self.canvas.fig
        ##dpi = self.fig.get_dpi()
        ##self.canvas.fig.set_size_inches(width/dpi, height/dpi, forward=True)
        ##self.plottable.plot(fig=self.canvas.fig)
        ##self.canvas.fig.canvas.draw()
        
        # Set widget size properties
        self.setMinimumSize(QtCore.QSize(width,height))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        
        # Set up Matplotlib canvas
        self.canvas = Qt4MplCanvas(self)
        #sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        #sizePolicy.setHorizontalStretch(0)
        #sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        #self.canvas.setSizePolicy(sizePolicy)
        self.canvas.setObjectName(QtCore.QString("canvas1"))
        
        ### Keep a reference to the figure and adjust the size
        self.fig = self.canvas.fig
        dpi = self.fig.get_dpi()
        self.fig.set_size_inches(width/dpi, height/dpi, forward=True)
        
        # Call the plotttalb plot() method
        self.plottable.plot(fig=self.fig)
        self.fig.canvas.draw()
        

    def paintEvent(self, event):
        self.plottable.plot(fig=self.fig)
        self.fig.canvas.draw()
        
