# -*- coding: utf-8 -*-
"""
Base class for the *Dialog widgets.
This is necessary because there are some significant differences among platforms, which we want to
normalize for all of our secondary windows.

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from PyQt4 import QtGui, QtCore
import platform

# Identify the platform
IS_DARWIN = (platform.system() == 'Darwin')
IS_LINUX = (platform.system() == 'Linux')


class BaseDialog(QtGui.QDialog):
    def __init__(self, parent=None, *args, **kwargs):
        # On non-Mac platforms, a dialog with a parent will always float above the parent. We want these
        # windows to be independent, so in that case remove the parent.
        # (We need the parent on Mac because it allows all windows to share a menu.)
        if not IS_DARWIN:
            parent = None
        super(BaseDialog, self).__init__(parent=parent, *args, **kwargs)
        # On Linux, dialogs don't have window controls, this can be fixed by turning off that window flag
        if IS_LINUX:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.Dialog)
