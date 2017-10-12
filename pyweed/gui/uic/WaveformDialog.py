# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyweed/gui/uic/WaveformDialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_WaveformDialog(object):
    def setupUi(self, WaveformDialog):
        WaveformDialog.setObjectName(_fromUtf8("WaveformDialog"))
        WaveformDialog.resize(1212, 724)
        self.verticalLayout = QtGui.QVBoxLayout(WaveformDialog)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.topFrame = QtGui.QFrame(WaveformDialog)
        self.topFrame.setFrameShape(QtGui.QFrame.NoFrame)
        self.topFrame.setFrameShadow(QtGui.QFrame.Plain)
        self.topFrame.setObjectName(_fromUtf8("topFrame"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.topFrame)
        self.horizontalLayout.setMargin(2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.downloadGroupBox = QtGui.QGroupBox(self.topFrame)
        self.downloadGroupBox.setEnabled(True)
        self.downloadGroupBox.setObjectName(_fromUtf8("downloadGroupBox"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.downloadGroupBox)
        self.verticalLayout_6.setMargin(2)
        self.verticalLayout_6.setSpacing(2)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setVerticalSpacing(2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.secondsBeforeLabel = QtGui.QLabel(self.downloadGroupBox)
        self.secondsBeforeLabel.setObjectName(_fromUtf8("secondsBeforeLabel"))
        self.gridLayout.addWidget(self.secondsBeforeLabel, 0, 0, 1, 1)
        self.label = QtGui.QLabel(self.downloadGroupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 2, 1, 1)
        self.secondsAfterPhaseComboBox = QtGui.QComboBox(self.downloadGroupBox)
        self.secondsAfterPhaseComboBox.setObjectName(_fromUtf8("secondsAfterPhaseComboBox"))
        self.gridLayout.addWidget(self.secondsAfterPhaseComboBox, 1, 3, 1, 1)
        self.secondsBeforePhaseComboBox = QtGui.QComboBox(self.downloadGroupBox)
        self.secondsBeforePhaseComboBox.setObjectName(_fromUtf8("secondsBeforePhaseComboBox"))
        self.gridLayout.addWidget(self.secondsBeforePhaseComboBox, 0, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 4, 1, 1)
        self.secondsAfterSpinBox = QtGui.QSpinBox(self.downloadGroupBox)
        self.secondsAfterSpinBox.setMaximum(21600)
        self.secondsAfterSpinBox.setSingleStep(100)
        self.secondsAfterSpinBox.setProperty("value", 600)
        self.secondsAfterSpinBox.setObjectName(_fromUtf8("secondsAfterSpinBox"))
        self.gridLayout.addWidget(self.secondsAfterSpinBox, 1, 1, 1, 1)
        self.secondsBeforeSpinBox = QtGui.QSpinBox(self.downloadGroupBox)
        self.secondsBeforeSpinBox.setMaximum(3600)
        self.secondsBeforeSpinBox.setSingleStep(10)
        self.secondsBeforeSpinBox.setProperty("value", 60)
        self.secondsBeforeSpinBox.setObjectName(_fromUtf8("secondsBeforeSpinBox"))
        self.gridLayout.addWidget(self.secondsBeforeSpinBox, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.downloadGroupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 2, 1, 1)
        self.secondsAfterLabel = QtGui.QLabel(self.downloadGroupBox)
        self.secondsAfterLabel.setObjectName(_fromUtf8("secondsAfterLabel"))
        self.gridLayout.addWidget(self.secondsAfterLabel, 1, 0, 1, 1)
        self.verticalLayout_6.addLayout(self.gridLayout)
        self.widget_5 = QtGui.QWidget(self.downloadGroupBox)
        self.widget_5.setObjectName(_fromUtf8("widget_5"))
        self.horizontalLayout_7 = QtGui.QHBoxLayout(self.widget_5)
        self.horizontalLayout_7.setMargin(2)
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.downloadPushButton = QtGui.QPushButton(self.widget_5)
        self.downloadPushButton.setMinimumSize(QtCore.QSize(200, 0))
        self.downloadPushButton.setCheckable(False)
        self.downloadPushButton.setObjectName(_fromUtf8("downloadPushButton"))
        self.horizontalLayout_7.addWidget(self.downloadPushButton)
        self.downloadStatusLabel = QtGui.QLabel(self.widget_5)
        self.downloadStatusLabel.setObjectName(_fromUtf8("downloadStatusLabel"))
        self.horizontalLayout_7.addWidget(self.downloadStatusLabel, QtCore.Qt.AlignLeft)
        self.verticalLayout_6.addWidget(self.widget_5)
        self.horizontalLayout.addWidget(self.downloadGroupBox)
        self.saveGroupBox = QtGui.QGroupBox(self.topFrame)
        self.saveGroupBox.setEnabled(True)
        self.saveGroupBox.setObjectName(_fromUtf8("saveGroupBox"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.saveGroupBox)
        self.verticalLayout_5.setMargin(2)
        self.verticalLayout_5.setSpacing(2)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setVerticalSpacing(2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.saveFormatComboBox = QtGui.QComboBox(self.saveGroupBox)
        self.saveFormatComboBox.setObjectName(_fromUtf8("saveFormatComboBox"))
        self.horizontalLayout_4.addWidget(self.saveFormatComboBox)
        spacerItem1 = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.horizontalLayout_4.setStretch(1, 1)
        self.gridLayout_2.addLayout(self.horizontalLayout_4, 1, 1, 1, 1)
        self.saveDirectoryLabel = QtGui.QLabel(self.saveGroupBox)
        self.saveDirectoryLabel.setObjectName(_fromUtf8("saveDirectoryLabel"))
        self.gridLayout_2.addWidget(self.saveDirectoryLabel, 0, 0, 1, 1)
        self.saveFormatLabel = QtGui.QLabel(self.saveGroupBox)
        self.saveFormatLabel.setObjectName(_fromUtf8("saveFormatLabel"))
        self.gridLayout_2.addWidget(self.saveFormatLabel, 1, 0, 1, 1)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.saveDirectoryPushButton = QtGui.QPushButton(self.saveGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveDirectoryPushButton.sizePolicy().hasHeightForWidth())
        self.saveDirectoryPushButton.setSizePolicy(sizePolicy)
        self.saveDirectoryPushButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.saveDirectoryPushButton.setStyleSheet(_fromUtf8("QPushButton { text-align: left; }"))
        self.saveDirectoryPushButton.setObjectName(_fromUtf8("saveDirectoryPushButton"))
        self.horizontalLayout_6.addWidget(self.saveDirectoryPushButton)
        self.saveDirectoryBrowseToolButton = QtGui.QToolButton(self.saveGroupBox)
        self.saveDirectoryBrowseToolButton.setIconSize(QtCore.QSize(16, 16))
        self.saveDirectoryBrowseToolButton.setObjectName(_fromUtf8("saveDirectoryBrowseToolButton"))
        self.horizontalLayout_6.addWidget(self.saveDirectoryBrowseToolButton)
        spacerItem2 = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem2)
        self.horizontalLayout_6.setStretch(2, 1)
        self.gridLayout_2.addLayout(self.horizontalLayout_6, 0, 1, 1, 1)
        self.verticalLayout_5.addLayout(self.gridLayout_2)
        self.widget_6 = QtGui.QWidget(self.saveGroupBox)
        self.widget_6.setObjectName(_fromUtf8("widget_6"))
        self.horizontalLayout_8 = QtGui.QHBoxLayout(self.widget_6)
        self.horizontalLayout_8.setMargin(2)
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.savePushButton = QtGui.QPushButton(self.widget_6)
        self.savePushButton.setMinimumSize(QtCore.QSize(200, 0))
        self.savePushButton.setCheckable(False)
        self.savePushButton.setObjectName(_fromUtf8("savePushButton"))
        self.horizontalLayout_8.addWidget(self.savePushButton)
        self.saveStatusLabel = QtGui.QLabel(self.widget_6)
        self.saveStatusLabel.setObjectName(_fromUtf8("saveStatusLabel"))
        self.horizontalLayout_8.addWidget(self.saveStatusLabel, QtCore.Qt.AlignLeft)
        self.verticalLayout_5.addWidget(self.widget_6)
        self.horizontalLayout.addWidget(self.saveGroupBox)
        self.verticalLayout.addWidget(self.topFrame)
        self.selectionTableFrame = QtGui.QFrame(WaveformDialog)
        self.selectionTableFrame.setObjectName(_fromUtf8("selectionTableFrame"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.selectionTableFrame)
        self.verticalLayout_2.setMargin(2)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.filterGroupBox = QtGui.QGroupBox(self.selectionTableFrame)
        self.filterGroupBox.setEnabled(True)
        self.filterGroupBox.setObjectName(_fromUtf8("filterGroupBox"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.filterGroupBox)
        self.horizontalLayout_2.setMargin(2)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.eventComboBox = QtGui.QComboBox(self.filterGroupBox)
        self.eventComboBox.setObjectName(_fromUtf8("eventComboBox"))
        self.horizontalLayout_2.addWidget(self.eventComboBox)
        self.networkComboBox = QtGui.QComboBox(self.filterGroupBox)
        self.networkComboBox.setObjectName(_fromUtf8("networkComboBox"))
        self.horizontalLayout_2.addWidget(self.networkComboBox)
        self.stationComboBox = QtGui.QComboBox(self.filterGroupBox)
        self.stationComboBox.setObjectName(_fromUtf8("stationComboBox"))
        self.horizontalLayout_2.addWidget(self.stationComboBox)
        self.horizontalLayout_2.setStretch(0, 3)
        self.horizontalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.setStretch(2, 1)
        self.verticalLayout_2.addWidget(self.filterGroupBox)
        self.selectionTable = QtGui.QTableWidget(self.selectionTableFrame)
        self.selectionTable.setMinimumSize(QtCore.QSize(500, 100))
        self.selectionTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.selectionTable.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.selectionTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.selectionTable.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.selectionTable.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.selectionTable.setShowGrid(False)
        self.selectionTable.setObjectName(_fromUtf8("selectionTable"))
        self.selectionTable.setColumnCount(0)
        self.selectionTable.setRowCount(0)
        self.selectionTable.horizontalHeader().setStretchLastSection(False)
        self.selectionTable.verticalHeader().setVisible(True)
        self.verticalLayout_2.addWidget(self.selectionTable)
        self.verticalLayout.addWidget(self.selectionTableFrame)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(WaveformDialog)
        QtCore.QMetaObject.connectSlotsByName(WaveformDialog)

    def retranslateUi(self, WaveformDialog):
        WaveformDialog.setWindowTitle(_translate("WaveformDialog", "Dialog", None))
        self.downloadGroupBox.setTitle(_translate("WaveformDialog", "Download / Preview Waveforms", None))
        self.secondsBeforeLabel.setText(_translate("WaveformDialog", "Start:", None))
        self.label.setText(_translate("WaveformDialog", "secs before", None))
        self.label_2.setText(_translate("WaveformDialog", "secs after", None))
        self.secondsAfterLabel.setText(_translate("WaveformDialog", "End:", None))
        self.downloadPushButton.setText(_translate("WaveformDialog", "Download", None))
        self.downloadStatusLabel.setText(_translate("WaveformDialog", "Download status", None))
        self.saveGroupBox.setTitle(_translate("WaveformDialog", "Save Waveforms", None))
        self.saveDirectoryLabel.setText(_translate("WaveformDialog", "To:", None))
        self.saveFormatLabel.setText(_translate("WaveformDialog", "As:", None))
        self.saveDirectoryPushButton.setText(_translate("WaveformDialog", "Directory", None))
        self.saveDirectoryBrowseToolButton.setText(_translate("WaveformDialog", "Open", None))
        self.savePushButton.setText(_translate("WaveformDialog", "Save", None))
        self.saveStatusLabel.setText(_translate("WaveformDialog", "Save status", None))
        self.filterGroupBox.setTitle(_translate("WaveformDialog", "Table Filters", None))
        self.selectionTable.setSortingEnabled(True)

