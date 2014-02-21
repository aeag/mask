from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from ui_layer_list import Ui_LayerListWidget

from mask_filter import *

class LayerListWidget( QWidget ):
    def __init__( self, parent ):
        QWidget.__init__(self, parent)

        self.ui = Ui_LayerListWidget()
        self.ui.setupUi( self )

        # model layer_name => (do_limit_labeling (bool), original pal)
        self.model = {}

    def set_model( self, model ):
        self.model = model

    def get_model( self ):
        return self.model

    def update_from_layers( self ):
        layers = QgsMapLayerRegistry.instance().mapLayers()
        n = 0
        for name, layer in layers.iteritems():

            if layer.name() == 'Mask':
                continue

            do_limit = False
            pal = QgsPalLayerSettings()
            pal.readFromLayer(layer)
            if name not in self.model.keys():
                do_limit = has_mask_filter( layer )
                orig_pal = remove_mask_filter( pal )
                self.model[name] = (do_limit, orig_pal)
            else:
                do_limit, _ = self.model[name]

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
            did_limit, orig_pal = self.model[layer.id()]

            if not did_limit and do_limit:
                # add spatial filtering
                pal = add_mask_filter( pal )
            if did_limit and not do_limit:
                pal = remove_mask_filter( pal )

            pal.writeToLayer( layer )
            self.model[layer.id()] = (do_limit, orig_pal)
                

class LayerListDialog( QDialog ):
    def __init__( self, parent ):
        QDialog.__init__(self, parent)

        # add a button box
        self.layout = QVBoxLayout()

        self.layer_list = LayerListWidget( self )
        self.button_box = QDialogButtonBox( self )
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.button_box.accepted.connect( self.accept )
        self.button_box.rejected.connect( self.reject )

        self.layout.addWidget( self.layer_list )
        self.layout.addWidget( self.button_box )

        self.setLayout( self.layout )

    def set_labeling_model( self, model ):
        self.layer_list.set_model( model )

    def exec_( self ):
        self.layer_list.update_from_layers()
        return QDialog.exec_( self )

    def accept( self ):
        # update layers 
        self.layer_list.update_labeling_from_list()
        QDialog.accept( self )

