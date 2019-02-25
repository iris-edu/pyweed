# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyweed/gui/uic/SpinnerWidget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SpinnerWidget(object):
    def setupUi(self, SpinnerWidget):
        SpinnerWidget.setObjectName("SpinnerWidget")
        SpinnerWidget.resize(306, 207)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SpinnerWidget.sizePolicy().hasHeightForWidth())
        SpinnerWidget.setSizePolicy(sizePolicy)
        SpinnerWidget.setStyleSheet("QFrame { background-color: rgba(224,224,224,192)} \n"
"QLabel { background-color: transparent }")
        self.verticalLayout = QtWidgets.QVBoxLayout(SpinnerWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.icon = QtWidgets.QLabel(SpinnerWidget)
        self.icon.setText("")
        self.icon.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.icon.setObjectName("icon")
        self.verticalLayout.addWidget(self.icon)
        self.label = QtWidgets.QLabel(SpinnerWidget)
        self.label.setText("")
        self.label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cancelButton = QtWidgets.QPushButton(SpinnerWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cancelButton.sizePolicy().hasHeightForWidth())
        self.cancelButton.setSizePolicy(sizePolicy)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(SpinnerWidget)
        QtCore.QMetaObject.connectSlotsByName(SpinnerWidget)

    def retranslateUi(self, SpinnerWidget):
        _translate = QtCore.QCoreApplication.translate
        SpinnerWidget.setWindowTitle(_translate("SpinnerWidget", "Form"))
        self.cancelButton.setText(_translate("SpinnerWidget", "Cancel"))

