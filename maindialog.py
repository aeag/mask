from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from ui_plugin_mask import Ui_MainDialog
from layerlist import LayerListWidget

class MainDialog( QDialog ):

    def __init__( self, layer ):
        QDialog.__init__( self, None )

        self.ui = Ui_MainDialog()
        self.ui.setupUi(self)
        self.ui.layer_list = LayerListWidget( self.ui.labelingGroup )
        self.ui.labelingLayout.addWidget( self.ui.layer_list )

        self.ui.bufferUnits.setValidator(QDoubleValidator())
        self.ui.bufferSegments.setValidator(QIntValidator())
        self.ui.simplifyTolerance.setValidator(QDoubleValidator())

        # create a dummy memory layer
        self.layer = layer
        self.style = QgsStyleV2()

        # connect edit style
        self.ui.editStyleBtn.clicked.connect( self.on_style_edit )
        # connect file browser
        self.ui.browseBtn.clicked.connect( self.on_file_browse )

        # mask_mode: selection | mask
        self.mask_mode = None
        #
        self.do_buffer = False
        self.buffer_units = 0
        self.buffer_segments = 0

        self.do_save_as = False
        self.file_path = None
        self.file_format = None

        self.update_style( self.layer )

        # init save format list
        for k,v in QgsVectorFileWriter.ogrDriverList().iteritems():
            self.ui.formatCombo.addItem( k )

    def on_file_browse( self ):
        fn = QFileDialog.getSaveFileName( None, "Select a filename to save the mask layer to" )
        if not fn:
            return

        self.ui.filePath.setText( fn )

    def on_style_edit( self ):
        # QgsRenderV2PropertiesDialog has a Cancel button that is not correctly plugged
        # rewrap the widget with a buttonbox
        dlg = QDialog(self)

        dlg.layout = QVBoxLayout( dlg )
        dlg.widget = QgsRendererV2PropertiesDialog(self.layer, self.style, True)
        dlg.widget.setLayout( dlg.layout )
        dlg.buttons = QDialogButtonBox( dlg )

        dlg.layout.addWidget( dlg.widget )
        dlg.layout.addWidget( dlg.buttons )

        dlg.buttons.setOrientation(Qt.Horizontal)
        dlg.buttons.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        def on_style_edit_accept( d ):
            # this will update the layer's style
            dlg.widget.onOK()
            dlg.accept()  

        dlg.buttons.accepted.connect( lambda d=dlg: on_style_edit_accept(d) )
        dlg.buttons.rejected.connect( dlg.reject )

        r = dlg.exec_()
        if r == 1:
            self.update_style( self.layer )

    def update_style( self, layer ):
        syms = layer.rendererV2().symbols()
        # only display the first symbol
        if len(syms) > 0:
            pix = QPixmap()
            pix.convertFromImage( syms[0].bigSymbolPreviewImage() )
            self.ui.stylePreview.setPixmap( pix )

    def set_labeling_model( self, model ):
        self.ui.layer_list.set_model( model )

    def get_labeling_model( self ):
        return self.ui.layer_list.get_model()

    def exec_( self ):
        self.ui.layer_list.update_from_layers()
        return QDialog.exec_( self )

    def accept( self ):
        # get data before closing
        idx = self.ui.contentCombo.currentIndex()
        self.mask_mode = ('selection', 'mask')[idx]
        self.do_buffer = self.ui.bufferGroup.isEnabled()
        self.buffer_units = float(self.ui.bufferUnits.text() or 0)
        self.buffer_segments = float(self.ui.bufferSegments.text() or 0)
        self.do_simplify = self.ui.simplifyGroup.isEnabled()
        self.simplify_tolerance = float(self.ui.simplifyTolerance.text() or 0)

        # get save as
        self.do_save_as = self.ui.saveLayerGroup.isEnabled()
        self.file_path = self.ui.filePath.text()
        self.file_format = self.ui.formatCombo.currentText()

        # update layers 
        self.ui.layer_list.update_labeling_from_list()

        QDialog.accept( self )

