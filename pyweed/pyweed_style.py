"""
Qt Stylesheet.

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

# Qt StyleSheet
#
# See:  http://doc.qt.io/qt-4.8/stylesheet-reference.html
# See:  https://github.com/ColinDuquesnoy/QDarkStyleSheet/blob/master/qdarkstyle/style.qss

from __future__ import (absolute_import, division, print_function)

stylesheet = """

/* See:   */

/* ----- Default Settings ----------------------------------------------------*/

/* Tighten up all tables and remove visible gridlines */

QTableView::item {
    margin: 0px;
    padding: 2px
}

QTableView {
    gridline-color: white;
}

/* Tighten up all frames */

QFrame {
    margin: 0px;
    padding: 0px;
}

/* Increase 'disabled' contrast */

QSpinBox:!enabled {
    color: gray;
}

/* ----- Waveforms Dialog ----------------------------------------------------*/

/* Remove border from frames */

QDialog#WaveformDialog QFrame {
    margin: 0px;
    padding: 0px;
    border: 0px none black;
}

QDialog#WaveformDialog QTableView#selectionTable {
    selection-background-color: white;
    selection-color: black;
}

/* Start/Stop toggle buttons */

QDialog#WaveformDialog QToolButton { /* unchecked = up = "action canceled" */
  padding: 3px;
  background-color: #d3d3d3;
  border-left: 2px solid #d3d3d3;
  border-top: 2px solid #d3d3d3;
  border-right: 2px solid #696969;
  border-bottom: 2px solid #696969;
}

QDialog#WaveformDialog QToolButton:checked { /* checked = down = "action activated" */
  padding: 3px;
  background-color: white;
  border-left: 2px solid #696969;
  border-top: 2px solid #696969;
  border-right: 2px solid #d3d3d3;
  border-bottom: 2px solid #d3d3d3;
}



/* Prevent WaveformDialog.directoryPushButton from staying highlighted */

QDialog#WaveformDialog directoryPushButton:focus {
    background-color: white;
}


"""
