# Display logging messages in a Qt textEdit widget
#
# http://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt

import logging

class MyTextEditLoggingHandler(logging.Handler):
    def __init__(self, widget=None):
        super(self.__class__, self).__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)    

