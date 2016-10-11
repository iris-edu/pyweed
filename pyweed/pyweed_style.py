"""
Qt Stylesheet.

:copyright:
    Mazama Science
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

stylesheet = """

/* Example for testing */
/*
QFrame, QLabel, QToolTip {
    border: 2px solid green;
    border-radius: 4px;
    padding: 2px;
}
*/

/* Example for testing */
/* QTableWidget::item:focus { background-color:gray50; color:red;  border: 0px } */

QTableView {
    gridline-color: white;
}

QTableView::item {
    margin 0px;
    padding: 2px
}


/* Waveforms table -----------------------------------------------------------*/

QDialog#WaveformDialog QTableView#selectionTable {
    selection-background-color: white;
    selection-color: black;
}

"""