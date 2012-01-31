# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Documents and Settings\PPociask\.qgis\python\plugins\Polygonizer\ui_polygonizer.ui'
#
# Created: Wed Feb 09 09:53:39 2011
#      by: PyQt4 UI code generator 4.5.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(423, 165)
        Form.setAutoFillBackground(False)
        self.btnOK = QtGui.QPushButton(Form)
        self.btnOK.setGeometry(QtCore.QRect(200, 130, 98, 27))
        self.btnOK.setObjectName("btnOK")
        self.btnCancel = QtGui.QPushButton(Form)
        self.btnCancel.setGeometry(QtCore.QRect(310, 130, 98, 27))
        self.btnCancel.setFlat(False)
        self.btnCancel.setObjectName("btnCancel")
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 10, 151, 17))
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(10, 70, 81, 17))
        self.label_2.setObjectName("label_2")
        self.cmbLayer = QtGui.QComboBox(Form)
        self.cmbLayer.setGeometry(QtCore.QRect(10, 30, 401, 27))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbLayer.sizePolicy().hasHeightForWidth())
        self.cmbLayer.setSizePolicy(sizePolicy)
        self.cmbLayer.setObjectName("cmbLayer")
        self.btnBrowse = QtGui.QPushButton(Form)
        self.btnBrowse.setGeometry(QtCore.QRect(310, 90, 98, 27))
        self.btnBrowse.setObjectName("btnBrowse")
        self.eOutput = QtGui.QLineEdit(Form)
        self.eOutput.setGeometry(QtCore.QRect(10, 90, 291, 27))
        self.eOutput.setObjectName("eOutput")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Polygonizer", None, QtGui.QApplication.UnicodeUTF8))
        self.btnOK.setText(QtGui.QApplication.translate("Form", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("Form", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Input line vector layer:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Output file:", None, QtGui.QApplication.UnicodeUTF8))
        self.btnBrowse.setText(QtGui.QApplication.translate("Form", "Browse", None, QtGui.QApplication.UnicodeUTF8))

