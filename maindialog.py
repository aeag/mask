from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from ui_plugin_mask import Ui_MainDialog

class MainDialog( QDialog ):
    def __init__( self, layer ):
        QDialog.__init__( self, None )

        self.ui = Ui_MainDialog()
        self.ui.setupUi(self)

        self.ui.bufferUnits.setValidator(QDoubleValidator())
        self.ui.bufferSegments.setValidator(QIntValidator())
        self.ui.simplifyTolerance.setValidator(QDoubleValidator())

        # create a dummy memory layer
        self.layer = layer
        self.style = QgsStyleV2()

        self.ui.editStyleBtn.clicked.connect( self.on_style_edit )

        # mask_mode: selection | mask
        self.mask_mode = None
        #
        self.do_buffer = False
        self.buffer_units = 0
        self.buffer_segments = 0

        self.update_style( self.layer )

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

    def accept( self ):
        # get data before closing
        idx = self.ui.contentCombo.currentIndex()
        self.mask_mode = ('selection', 'mask')[idx]
        self.do_buffer = self.ui.bufferGroup.isEnabled()
        self.buffer_units = float(self.ui.bufferUnits.text() or 0)
        self.buffer_segments = float(self.ui.bufferSegments.text() or 0)
        self.do_simplify = self.ui.simplifyGroup.isEnabled()
        self.simplify_tolerance = float(self.ui.simplifyTolerance.text() or 0)

        QDialog.accept( self )

