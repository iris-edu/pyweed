# Custom widget that embeds an image
#
# To be inserted into the QTableWidget with setCellWidget() rather than setItem().
#
# http://stackoverflow.com/questions/5553342/adding-images-to-a-qtablewidget-in-pyqt

from PyQt4 import QtGui


class MyTableWidgetImageWidget(QtGui.QLabel):

    def __init__(self, parent=None, imagePath=None):
        super(MyTableWidgetImageWidget, self).__init__(parent)
        pic = QtGui.QPixmap(imagePath)
        # NOTE:  From QPixmap we could use scaledToWidth() but the resulting images aren't so pretty
        # pic = pic.scaledToWidth(500)
        self.setPixmap(pic)
        # NOTE:  From QLabel we could use setScaledContents() but this doesn't preserve the aspect ratio
        # self.setScaledContents(True)
