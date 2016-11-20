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


/* ----- Waveforms Dialog ----------------------------------------------------*/

QDialog#WaveformDialog QTableView#selectionTable {
    selection-background-color: white;
    selection-color: black;
}


/* Prevent WaveformDialog.directoryPushButton from staying highlighted */

QDialog#WaveformDialog directoryPushButton:focus {
    background-color: white;
}

/* Remove border from frames */

QDialog#WaveformDialog QFrame {
    margin: 0px;
    padding: 0px;
    border: 0px none black;
}

/* Start/Stop toggle buttons */

QDialog#WaveformDialog QToolButton {
  color: white;
  background-color: seagreen;
}

QDialog#WaveformDialog QToolButton:checked {
  color: black;
  background-color: salmon;
}



/* Example
QPushButton
{
    color: #b1b1b1;
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    border-radius: 6;
    padding: 3px;
    font-size: 12px;
    padding-left: 5px;
    padding-right: 5px;
}

QPushButton:pressed
{
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2d2d2d, stop: 0.1 #2b2b2b, stop: 0.5 #292929, stop: 0.9 #282828, stop: 1 #252525);
}

QPushButton:hover
{
    border: 2px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
}

QPushButton:focus {
    background-color: red;
}
*/

"""
