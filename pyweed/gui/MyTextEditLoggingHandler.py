# -*- coding: utf-8 -*-
"""
Display logging messages in a Qt textEdit widget

http://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

import logging


class MyTextEditLoggingHandler(logging.Handler):
    def __init__(self, signal=None):
        super(MyTextEditLoggingHandler, self).__init__(logging.INFO)
        self.signal = signal

    def emit(self, record):
        msg = self.format(record)
        self.signal.emit(msg)
