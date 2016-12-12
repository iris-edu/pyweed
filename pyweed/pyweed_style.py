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

/*
QFrame {
    margin: 0px;
    padding: 0px;
}
*/

/* Increase 'disabled' contrast */

QSpinBox:!enabled {
    color: gray;
}

/* Modify default GroupBox style */

QGroupBox {
    background-color: #e7e7e7;
    border: 1px solid lightGray;
    border-radius: 3px;
    margin-top: 1.0em;
}
/*
groupBox.setStyleSheet("QGroupBox { background-color: \
    rgb(255, 255, 255); border: 3px solid rgb(255, 0, 0); }")
    */

QGroupBox::title {
    subcontrol-origin: margin;
    font-size: 12px;
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
  background-color: lightGray;
  border-left: 2px solid lightGray;
  border-top: 2px solid lightGray;
  border-right: 2px solid darkGray;
  border-bottom: 2px solid darkGray;
}

QDialog#WaveformDialog QToolButton:checked { /* checked = down = "action activated" */
  padding: 3px;
  background-color: white;
  border-left: 2px solid darkGray;
  border-top: 2px solid darkGray;
  border-right: 2px solid lightGray;
  border-bottom: 2px solid lightGray;
}





/* Prevent WaveformDialog.directoryPushButton from staying highlighted */

QDialog#WaveformDialog directoryPushButton:focus {
    background-color: white;
}


"""
