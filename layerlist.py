from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from ui_layer_list import Ui_LayerListWidget

class LayerListWidget( QWidget ):
    SPATIAL_FILTER_BEGIN = "CASE WHEN contains($mask_geometry,$geometry) THEN "
    SPATIAL_FILTER_END = " ELSE '' END"

    def __init__( self, parent ):
        QWidget.__init__(self, parent)

        self.ui = Ui_LayerListWidget()
        self.ui.setupUi( self )

        # model layer_name => (layer, do_limit_labeling (bool), original_labeling_settings)
        self.model = {}

    def set_model( self, model ):
        self.model = model

    def get_model( self ):
        return self.model

    def has_mask_filter( self, layer ):
        # check if a layer has already a mask filter enabled
        pal = QgsPalLayerSettings()
        pal.readFromLayer( layer )
        if not pal.enabled:
            return False
        return pal.fieldName.find(self.SPATIAL_FILTER_BEGIN) == 0

    def update_from_layers( self ):
        layers = QgsMapLayerRegistry.instance().mapLayers()
        n = 0
        for name, layer in layers.iteritems():

            do_limit = False
            pal = QgsPalLayerSettings()
            pal.readFromLayer(layer)
            if name not in self.model.keys():
                do_limit = self.has_mask_filter( layer )
                self.model[name] = (layer, do_limit)
            else:
                _, do_limit = self.model[name]

            self.ui.layerTable.insertRow(n)
            name_item = QTableWidgetItem()
            name_item.setData( Qt.DisplayRole, layer.name() )
            self.ui.layerTable.setItem( n, 1, name_item )
            w = QCheckBox( self.ui.layerTable )
            w.setEnabled( pal.enabled )
            w.setChecked( do_limit )
            self.ui.layerTable.setCellWidget( n, 0, w )
            item = QTableWidgetItem()
            item.setData( Qt.UserRole, layer )
            self.ui.layerTable.setItem( n, 0, item )
            n+=1

    def update_labeling_from_list( self ):
        ll = self.ui.layerTable
        pal = QgsPalLayerSettings()
        for i in range(ll.rowCount()):
            do_limit = ll.cellWidget( i, 0 ).isChecked()
            layer = ll.item(i, 0).data( Qt.UserRole )
            pal.readFromLayer( layer )
            _, did_limit = self.model[layer.id()]

            if not did_limit and do_limit:
                # add spatial filtering
                pal.fieldName = self.SPATIAL_FILTER_BEGIN + pal.fieldName + self.SPATIAL_FILTER_END
                pal.isExpression = True
            if did_limit and not do_limit:
                # restore original pal
                if self.has_mask_filter( layer ):
                    l = len(pal.fieldName)
                    l1 = len(self.SPATIAL_FILTER_BEGIN)
                    l2 = len(self.SPATIAL_FILTER_END)
                    pal.fieldName = pal.fieldName[l1:l-l2]

            pal.writeToLayer( layer )
            self.model[layer.id()] = (layer, do_limit)
                



