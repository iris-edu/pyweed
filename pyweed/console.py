from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
from PyQt4 import QtGui, QtCore


class EmbedIPython(RichIPythonWidget):

    def __init__(self, **kwarg):
        super(RichIPythonWidget, self).__init__()
        self.kernel_manager = QtInProcessKernelManager()
        self.kernel_manager.start_kernel()
        self.kernel = self.kernel_manager.kernel
        self.kernel.gui = 'qt4'
        self.kernel.shell.push(kwarg)
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()


class ConsoleDialog(QtGui.QDialog):
    def __init__(self, *args, **kwargs):
        super(ConsoleDialog, self).__init__(*args, **kwargs)
        self.widget = EmbedIPython(app=self.parentWidget())
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.widget)


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    widget = ConsoleDialog()
    widget.show()
    sys.exit(app.exec_())
