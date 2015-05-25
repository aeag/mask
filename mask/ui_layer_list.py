# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_layer_list.ui'
#
# Created: Tue Apr 07 16:01:09 2015
#      by: PyQt4 UI code generator 4.10.2
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
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.selectAllBtn = QtGui.QPushButton(LayerListWidget)
        self.selectAllBtn.setObjectName(_fromUtf8("selectAllBtn"))
        self.horizontalLayout.addWidget(self.selectAllBtn)
        self.unselectAllBtn = QtGui.QPushButton(LayerListWidget)
        self.unselectAllBtn.setObjectName(_fromUtf8("unselectAllBtn"))
        self.horizontalLayout.addWidget(self.unselectAllBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(LayerListWidget)
        self.polygonOperatorCombo.setCurrentIndex(0)
        self.lineOperatorCombo.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(LayerListWidget)

    def retranslateUi(self, LayerListWidget):
        LayerListWidget.setWindowTitle(_translate("LayerListWidget", "Form", None))
        self.label.setText(_translate("LayerListWidget", "Function used for labeling filtering on polygons", None))
        self.polygonOperatorCombo.setItemText(0, _translate("LayerListWidget", "Exact (slow and will disable simplification)", None))
        self.polygonOperatorCombo.setItemText(1, _translate("LayerListWidget", "The mask geometry contains the centroid", None))
        self.polygonOperatorCombo.setItemText(2, _translate("LayerListWidget", "The mask geometry contains a point on the polygon surface", None))
        self.label_2.setText(_translate("LayerListWidget", "Function used for labeling filtering on lines", None))
        self.lineOperatorCombo.setItemText(0, _translate("LayerListWidget", "The mask geometry intersects the line", None))
        self.lineOperatorCombo.setItemText(1, _translate("LayerListWidget", "The mask geometry contains the line", None))
        item = self.layerTable.horizontalHeaderItem(0)
        item.setText(_translate("LayerListWidget", "Limit", None))
        item = self.layerTable.horizontalHeaderItem(1)
        item.setText(_translate("LayerListWidget", "Layer", None))
        self.selectAllBtn.setText(_translate("LayerListWidget", "Select all", None))
        self.unselectAllBtn.setText(_translate("LayerListWidget", "Unselect all", None))

