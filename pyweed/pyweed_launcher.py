#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyWEED GUI Launcher

This exists mainly to show the splash screen as quickly as possible, by deferring lots of the expensive
library imports required for the application itself.

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

import sys
import os
from future.utils import PY2
import matplotlib

# If running under windows, redirect stdout/stderr, since writing to them will crash Python if there's
# not a console. See https://bugs.python.org/issue706263
if sys.executable.endswith('pythonw.exe'):
    nul = open(os.devnull, 'w')
    sys.stderr = nul
    sys.stdout = nul

# Set up the PROJ_LIB environment variable needed by matplotlib
# See https://github.com/conda-forge/basemap-feedstock/issues/30
if not os.environ.get('PROJ_LIB') and os.environ.get('CONDA_PREFIX'):
    os.environ['PROJ_LIB'] = os.path.join(os.environ['CONDA_PREFIX'], 'share', 'proj')

# Configure matplotlib backend
matplotlib.use('AGG')

# For debugging, raise an exception on attempted chained assignment
# See http://pandas.pydata.org/pandas-docs/version/0.19.1/indexing.html#returning-a-view-versus-a-copy
# import pandas as pd
# pd.set_option('mode.chained_assignment', 'raise')

if PY2:
    # Configure PyQt5 -- in order for the Python console to work in Python 2, we need to load a particular
    # version of some internal libraries. This must be done before the first import of the PyQt5 libraries.
    # See http://stackoverflow.com/questions/11513132/embedding-ipython-qt-console-in-a-pyqt-application/20610786#20610786
    os.environ['QT_API'] = 'pyqt'
    import sip
    sip.setapi("QString", 2)
    sip.setapi("QVariant", 2)


def init_strptime():
    """ Workaround for https://github.com/obspy/obspy/issues/2147 """
    try:
        import locale
        # locale.setlocale(locale.LC_TIME, ('en_US', 'UTF-8'))
        from obspy.clients.fdsn.routing.routing_client import RoutingClient  # NOQA
        locale.setlocale(locale.LC_TIME, '')
    except Exception:
        pass
init_strptime()


def fix_locale():
    """
    Fix for issues with locale-bound number handling, we basically force decimals to use '.' rather than ','
    """
    from PyQt5.QtCore import QLocale
    QLocale.setDefault(QLocale.c())


def get_pyweed():
    """
    Load the PyWEED GUI code, this is where most of the expensive stuff happens
    """
    from pyweed.gui.PyWeedGUI import PyWeedGUI
    return PyWeedGUI()


def launch():
    """
    Basic startup process.
    """
    from PyQt5 import QtCore, QtWidgets
    from pyweed.gui.SplashScreenHandler import SplashScreenHandler
    import pyweed.gui.qrc  # NOQA

    # See https://stackoverflow.com/questions/31952711/
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)

    fix_locale()

    app = QtWidgets.QApplication(sys.argv)
    splashScreenHandler = SplashScreenHandler()
    app.processEvents()
    pyweed = get_pyweed()
    splashScreenHandler.finish(pyweed.mainWindow)
    sys.exit(app.exec_())


if __name__ == "__main__":
    launch()
