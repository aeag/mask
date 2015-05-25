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

        self.ui.selectAllBtn.clicked.connect( self.on_selectall )
        self.ui.unselectAllBtn.clicked.connect( self.on_unselectall )

        # list of limited layers (list of layer id)
        self.limited = []

    def set_limited_layers( self, limited ):
        self.limited = limited

    def get_limited_layers( self ):
        return self.limited

    def on_selectall( self ):
        "Select all layers for label filtering"
        ll = self.ui.layerTable
        for i in range(ll.rowCount()):
            ll.cellWidget( i, 0 ).setChecked( True )

    def on_unselectall( self ):
        "Unselect all layers for label filtering"
        ll = self.ui.layerTable
        for i in range(ll.rowCount()):
            ll.cellWidget( i, 0 ).setChecked( False )

    def update_from_layers( self, is_new = False ):
        layers = QgsMapLayerRegistry.instance().mapLayers()
        n = 0
        for name, layer in layers.iteritems():

            if layer.name() == 'Mask':
                continue
            # skip non vector layers
            if not isinstance(layer, QgsVectorLayer):
                continue

            pal = QgsPalLayerSettings()
            pal.readFromLayer(layer)
            # skip layers without labels
            if not pal.enabled:
                continue

            do_limit = False
            did_limit = layer.id() in self.limited
            do_limit = has_mask_filter( layer )

            if do_limit and not did_limit:
                self.limited.append( layer.id() )
            if not do_limit and did_limit:
                self.limited.remove( layer.id() )

            self.ui.layerTable.insertRow(n)
            name_item = QTableWidgetItem()
            name_item.setData( Qt.DisplayRole, layer.name() )
            self.ui.layerTable.setItem( n, 1, name_item )
            w = QCheckBox( self.ui.layerTable )
            w.setEnabled( pal.enabled )
            w.setChecked( do_limit or is_new )
            self.ui.layerTable.setCellWidget( n, 0, w )
            item = QTableWidgetItem()
            item.setData( Qt.UserRole, layer )
            self.ui.layerTable.setItem( n, 0, item )
            n+=1

        self.ui.selectAllBtn.setEnabled( n != 0 )
        self.ui.unselectAllBtn.setEnabled( n != 0 )

    def update_labeling_from_list( self ):
        ll = self.ui.layerTable
        pal = QgsPalLayerSettings()
        for i in range(ll.rowCount()):
            do_limit = ll.cellWidget( i, 0 ).isChecked()
            layer = ll.item(i, 0).data( Qt.UserRole )
            pal.readFromLayer( layer )
            did_limit = layer.id() in self.limited

            if not did_limit and do_limit:
                # add spatial filtering
                pal = add_mask_filter( pal, layer )
                self.limited.append( layer.id() )
            if did_limit and not do_limit:
                pal = remove_mask_filter( pal )
                self.limited.remove( layer.id() )

            pal.writeToLayer( layer )

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

