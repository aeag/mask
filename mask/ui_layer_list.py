# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_layer_list.ui'
#
# Created: Thu Jun  5 10:10:26 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_LayerListWidget(object):
    def setupUi(self, LayerListWidget):
        LayerListWidget.setObjectName(_fromUtf8("LayerListWidget"))
        LayerListWidget.resize(768, 438)
        self.verticalLayout = QtGui.QVBoxLayout(LayerListWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(LayerListWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.polygonOperatorCombo = QtGui.QComboBox(LayerListWidget)
        self.polygonOperatorCombo.setObjectName(_fromUtf8("polygonOperatorCombo"))
        self.polygonOperatorCombo.addItem(_fromUtf8(""))
        self.polygonOperatorCombo.addItem(_fromUtf8(""))
        self.polygonOperatorCombo.addItem(_fromUtf8(""))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.polygonOperatorCombo)
        self.label_2 = QtGui.QLabel(LayerListWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.lineOperatorCombo = QtGui.QComboBox(LayerListWidget)
        self.lineOperatorCombo.setObjectName(_fromUtf8("lineOperatorCombo"))
        self.lineOperatorCombo.addItem(_fromUtf8(""))
        self.lineOperatorCombo.addItem(_fromUtf8(""))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.lineOperatorCombo)
        self.verticalLayout.addLayout(self.formLayout)
        self.layerTable = QtGui.QTableWidget(LayerListWidget)
        self.layerTable.setObjectName(_fromUtf8("layerTable"))
        self.layerTable.setColumnCount(2)
        self.layerTable.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.layerTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.layerTable.setHorizontalHeaderItem(1, item)
        self.layerTable.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.layerTable)

        self.retranslateUi(LayerListWidget)
        self.polygonOperatorCombo.setCurrentIndex(0)
        self.lineOperatorCombo.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(LayerListWidget)

    def retranslateUi(self, LayerListWidget):
        LayerListWidget.setWindowTitle(QtGui.QApplication.translate("LayerListWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("LayerListWidget", "Function used for labeling filtering on polygons", None, QtGui.QApplication.UnicodeUTF8))
        self.polygonOperatorCombo.setItemText(0, QtGui.QApplication.translate("LayerListWidget", "Exact (slow and will disable simplification)", None, QtGui.QApplication.UnicodeUTF8))
        self.polygonOperatorCombo.setItemText(1, QtGui.QApplication.translate("LayerListWidget", "The mask geometry contains the centroid", None, QtGui.QApplication.UnicodeUTF8))
        self.polygonOperatorCombo.setItemText(2, QtGui.QApplication.translate("LayerListWidget", "The mask geometry contains a point on the polygon surface", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("LayerListWidget", "Function used for labeling filtering on lines", None, QtGui.QApplication.UnicodeUTF8))
        self.lineOperatorCombo.setItemText(0, QtGui.QApplication.translate("LayerListWidget", "The mask geometry intersects the line", None, QtGui.QApplication.UnicodeUTF8))
        self.lineOperatorCombo.setItemText(1, QtGui.QApplication.translate("LayerListWidget", "The mask geometry contains the line", None, QtGui.QApplication.UnicodeUTF8))
        item = self.layerTable.horizontalHeaderItem(0)
        item.setText(QtGui.QApplication.translate("LayerListWidget", "Limit", None, QtGui.QApplication.UnicodeUTF8))
        item = self.layerTable.horizontalHeaderItem(1)
        item.setText(QtGui.QApplication.translate("LayerListWidget", "Layer", None, QtGui.QApplication.UnicodeUTF8))

