from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from qgis.core import *
from qgis.gui import *

from ui_plugin_mask import Ui_MainDialog
from layerlist import LayerListWidget
from mask_parameters import MaskParameters

class MainDialog( QDialog ):

    def __init__( self, layer, parameters ):
        QDialog.__init__( self, None )

        self.ui = Ui_MainDialog()
        self.ui.setupUi(self)
        self.ui.layer_list = LayerListWidget( self.ui.labelingGroup )
        self.ui.labelingLayout.addWidget( self.ui.layer_list )

        self.ui.bufferUnits.setValidator(QDoubleValidator())
        self.ui.bufferSegments.setValidator(QIntValidator())
        self.ui.simplifyTolerance.setValidator(QDoubleValidator())

        self.layer = layer
        self.parameters = parameters
        self.style = QgsStyleV2()

        # connect edit style
        self.ui.editStyleBtn.clicked.connect( self.on_style_edit )
        # connect file browser
        self.ui.browseBtn.clicked.connect( self.on_file_browse )
        # add a "save as defaults" button
        self.ui.saveDefaultsBtn = QPushButton( self.tr("Save as defaults"), self.ui.buttonBox )
        self.ui.buttonBox.addButton( self.ui.saveDefaultsBtn, QDialogButtonBox.ActionRole )
        self.ui.saveDefaultsBtn.clicked.connect( self.on_save_defaults )
        # add a "load defaults" button
        self.ui.loadDefaultsBtn = QPushButton( self.tr("Load defaults"), self.ui.buttonBox )
        self.ui.buttonBox.addButton( self.ui.loadDefaultsBtn, QDialogButtonBox.ActionRole )
        self.ui.loadDefaultsBtn.clicked.connect( self.load_defaults )

        self.ui.layer_list.ui.operatorCombo.currentIndexChanged[int].connect( self.on_operator_changed )

        # init save format list
        for k,v in QgsVectorFileWriter.ogrDriverList().iteritems():
            self.ui.formatCombo.addItem( k )

        # save current style
        self.save_style_parameters = MaskParameters()
        self.update_parameters_from_style( self.save_style_parameters )

    def on_operator_changed( self, idx ):
        if idx == 0 and self.ui.simplifyGroup.isChecked():
            self.ui.simplifyGroup.setChecked( False )

    def update_style_from_parameters( self, parameters ):
        if parameters.style is not None:
            doc = QDomDocument( "qgis" )
            doc.setContent( parameters.style )
            errorMsg = ''
            self.layer.readSymbology( doc.firstChildElement("qgis"), errorMsg )
            self.update_style_preview( self.layer )

    def update_parameters_from_style( self, parameters ):
        doc = QDomDocument( QDomImplementation().createDocumentType( "qgis", "http://mrcc.com/qgis.dtd", "SYSTEM" ) )
        rootNode = doc.createElement( "qgis" );
        doc.appendChild( rootNode );
        errorMsg = ''
        self.layer.writeSymbology( rootNode, doc, errorMsg )
        parameters.style = doc.toByteArray()

    def update_ui_from_parameters( self, parameters ):
        self.update_style_from_parameters( parameters )
        self.ui.bufferGroup.setChecked( parameters.do_buffer )
        self.ui.saveLayerGroup.setChecked( parameters.do_save_as )
        self.ui.bufferUnits.setText( str(parameters.buffer_units) )
        self.ui.bufferSegments.setText( str(parameters.buffer_segments) )
        self.ui.formatCombo.setCurrentIndex( -1 if parameters.file_format is None else QgsVectorFileWriter.ogrDriverList().keys().index(parameters.file_format) )
        self.ui.filePath.setText( parameters.file_path )
        self.ui.simplifyGroup.setChecked( parameters.do_simplify )
        self.ui.simplifyTolerance.setText( str(parameters.simplify_tolerance) )
        self.ui.layer_list.ui.operatorCombo.setCurrentIndex( parameters.mask_method )

    def update_parameters_from_ui( self, parameters ):
        self.update_parameters_from_style( parameters )
        parameters.do_buffer = self.ui.bufferGroup.isChecked()
        parameters.buffer_units = float(self.ui.bufferUnits.text() or 0)
        parameters.buffer_segments = int(self.ui.bufferSegments.text() or 0)
        parameters.do_save_as = self.ui.saveLayerGroup.isChecked()
        parameters.file_format = None if self.ui.formatCombo.currentIndex() == -1 else QgsVectorFileWriter.ogrDriverList().keys()[self.ui.formatCombo.currentIndex()]
        parameters.file_path = self.ui.filePath.text()
        parameters.do_simplify = self.ui.simplifyGroup.isChecked()
        parameters.simplify_tolerance = float(self.ui.simplifyTolerance.text() or 0.0)
        parameters.mask_method = self.ui.layer_list.ui.operatorCombo.currentIndex()

    def load_defaults( self ):
        settings = QSettings("AEAG", "QGIS Mask")

        defaults = settings.value( "defaults", None )
        if defaults is not None:
            parameters = MaskParameters()
            parameters.unserialize( defaults )
            self.update_ui_from_parameters( parameters )

    def on_save_defaults( self ):
        settings = QSettings("AEAG", "QGIS Mask")

        parameters = MaskParameters()
        self.update_parameters_from_ui( parameters )
        defaults = parameters.serialize()
        settings.setValue( "defaults", defaults )

    def on_file_browse( self ):
        settings = QSettings("AEAG", "QGIS Mask")

        dir = settings.value("file_dir", '')

        fn = QFileDialog.getSaveFileName( None, "Select a filename to save the mask layer to", dir )
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
            self.update_style_preview( self.layer )

    def update_style_preview( self, layer ):
        syms = layer.rendererV2().symbols()
        # only display the first symbol
        if len(syms) > 0:
            pix = QPixmap()
            pix.convertFromImage( syms[0].bigSymbolPreviewImage() )
            self.ui.stylePreview.setPixmap( pix )

    def exec_( self ):
        self.ui.layer_list.update_from_layers()

        if self.parameters.style is None:
            self.load_defaults()
        else:
            self.update_ui_from_parameters( self.parameters )

        # disable simplification if the simplifier is not available
        if 'QgsMapToPixelSimplifier' not in dir():
            self.ui.simplifyGroup.setEnabled( False )
            self.parameters.do_simplify = False
        # disable pointOnSurface if not available
        if 'pointOnSurface' not in dir(QgsGeometry):
            self.ui.layer_list.ui.operatorCombo.removeItem(2)
            if self.parameters.mask_method == 2:
                self.parameters.mask_method = 1

        self.update_style_preview( self.layer )

        return QDialog.exec_( self )

    def reject( self ):
        # restore layer's style on cancel
        self.update_style_from_parameters( self.save_style_parameters )
        QDialog.reject( self )

    def accept( self ):
        # get data before closing
        self.update_parameters_from_ui( self.parameters )

        # update labeling from parameters
        self.ui.layer_list.update_labeling_from_list()

        if self.parameters.mask_method == 0:
            # test if some limited layers have simplification turned on
            limited = self.ui.layer_list.get_limited_layers()
            slayers = []
            for name, layer in QgsMapLayerRegistry.instance().mapLayers().iteritems():
                if layer.id() in limited and int(layer.simplifyMethod().simplifyHints()) > 0:
                    # simplification is enabled
                    slayers.append(layer)
            if len(slayers) > 0:
                r = QMessageBox.question( None, self.tr("Warning"),
                                         self.tr("Some layer have rendering simplification turned on, which is not compatible with the labeling filtering you choose. Force simplification disabling ?"),
                                          buttons = QMessageBox.Yes | QMessageBox.No )
                if r == QMessageBox.Yes:
                    for l in slayers:
                        m = layer.simplifyMethod()
                        m.setSimplifyHints( QgsVectorSimplifyMethod.SimplifyHints(0) )
                        layer.setSimplifyMethod( m )


        QDialog.accept( self )

