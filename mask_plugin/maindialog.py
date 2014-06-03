from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from qgis.core import *
from qgis.gui import *

from ui_plugin_mask import Ui_MainDialog
from layerlist import LayerListWidget
from mask_parameters import MaskParameters

def is_in_qgis_core( sym ):
    import qgis.core
    return sym in dir(qgis.core)

# default parameters
# an inverted polygon styling with a white semi-transparent filling
DEFAULT_PARAMETERS = "(lp0\nI00\naF1000.0\naI5\naI01\naF1.0\naI00\naV\np1\naVESRI Shapefile\np2\na(lp3\nacsip\n_unpickle_type\np4\n(S'PyQt4.QtCore'\np5\nS'QByteArray'\np6\n(S'<!DOCTYPE qgis PUBLIC \\'http://mrcc.com/qgis.dtd\\' \\'SYSTEM\\'>\\n<qgis simplifyDrawingHints=\"1\" minLabelScale=\"0\" maxLabelScale=\"1e+08\" simplifyDrawingTol=\"1\" simplifyMaxScale=\"1\" simplifyLocal=\"1\" scaleBasedLabelVisibilityFlag=\"0\">\\n <renderer-v2 type=\"invertedPolygonRenderer\">\\n  <renderer-v2 symbollevels=\"0\" type=\"singleSymbol\">\\n   <symbols>\\n    <symbol alpha=\"1\" type=\"fill\" name=\"0\">\\n     <layer pass=\"0\" class=\"SimpleFill\" locked=\"0\">\\n      <prop k=\"border_width_map_unit_scale\" v=\"0,0\"/>\\n      <prop k=\"border_width_unit\" v=\"MM\"/>\\n      <prop k=\"color\" v=\"255,255,255,255\"/>\\n      <prop k=\"color_border\" v=\"0,0,0,255\"/>\\n      <prop k=\"joinstyle\" v=\"bevel\"/>\\n      <prop k=\"offset\" v=\"0,0\"/>\\n      <prop k=\"offset_map_unit_scale\" v=\"0,0\"/>\\n      <prop k=\"offset_unit\" v=\"MM\"/>\\n      <prop k=\"style\" v=\"solid\"/>\\n      <prop k=\"style_border\" v=\"solid\"/>\\n      <prop k=\"width_border\" v=\"0.26\"/>\\n     </layer>\\n    </symbol>\\n   </symbols>\\n   <rotation/>\\n   <sizescale scalemethod=\"area\"/>\\n  </renderer-v2>\\n </renderer-v2>\\n <customproperties/>\\n <blendMode>0</blendMode>\\n <featureBlendMode>0</featureBlendMode>\\n <layerTransparency>17</layerTransparency>\\n <displayfield>params</displayfield>\\n <label>0</label>\\n <labelattributes>\\n  <label fieldname=\"\" text=\"\\xc3\\x89tiquette\"/>\\n  <family fieldname=\"\" name=\"Ubuntu\"/>\\n  <size fieldname=\"\" units=\"pt\" value=\"12\"/>\\n  <bold fieldname=\"\" on=\"0\"/>\\n  <italic fieldname=\"\" on=\"0\"/>\\n  <underline fieldname=\"\" on=\"0\"/>\\n  <strikeout fieldname=\"\" on=\"0\"/>\\n  <color fieldname=\"\" red=\"0\" blue=\"0\" green=\"0\"/>\\n  <x fieldname=\"\"/>\\n  <y fieldname=\"\"/>\\n  <offset x=\"0\" y=\"0\" units=\"pt\" yfieldname=\"\" xfieldname=\"\"/>\\n  <angle fieldname=\"\" value=\"0\" auto=\"0\"/>\\n  <alignment fieldname=\"\" value=\"center\"/>\\n  <buffercolor fieldname=\"\" red=\"255\" blue=\"255\" green=\"255\"/>\\n  <buffersize fieldname=\"\" units=\"pt\" value=\"1\"/>\\n  <bufferenabled fieldname=\"\" on=\"\"/>\\n  <multilineenabled fieldname=\"\" on=\"\"/>\\n  <selectedonly on=\"\"/>\\n </labelattributes>\\n <edittypes>\\n  <edittype labelontop=\"0\" editable=\"0\" name=\"params\"/>\\n </edittypes>\\n <editform>.</editform>\\n <editforminit></editforminit>\\n <featformsuppress>0</featformsuppress>\\n <annotationform>.</annotationform>\\n <editorlayout>generatedlayout</editorlayout>\\n <excludeAttributesWMS/>\\n <excludeAttributesWFS/>\\n <attributeactions/>\\n</qgis>\\n'\np7\ntp8\ntp9\nRp10\naI1\na."

class MainDialog( QDialog ):

    applied = pyqtSignal()

    def __init__( self, layer, parameters, is_new ):
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
        if self.parameters.file_format is None:
            self.parameters.file_format = "ESRI Shapefile"
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

        # connect the "apply" button
        for btn in self.ui.buttonBox.buttons():
            if self.ui.buttonBox.buttonRole(btn) == QDialogButtonBox.ApplyRole:
                btn.clicked.connect( self.on_apply )
                break

        # save current style
        self.save_style_parameters = MaskParameters()
        self.update_parameters_from_style( self.save_style_parameters )

        if is_new:
            self.setWindowTitle( self.tr("Create a mask") )
        else:
            self.setWindowTitle( self.tr("Update the current mask") )

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
        self.ui.formatLbl.setText( '' if parameters.file_format is None else parameters.file_format )
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
        parameters.file_format = self.parameters.file_format
        parameters.file_path = self.ui.filePath.text()
        parameters.do_simplify = self.ui.simplifyGroup.isChecked()
        parameters.simplify_tolerance = float(self.ui.simplifyTolerance.text() or 0.0)
        parameters.mask_method = self.ui.layer_list.ui.operatorCombo.currentIndex()

    def load_defaults( self ):
        settings = QSettings()

        parameters = MaskParameters()
        defaults = settings.value( "mask_plugin/defaults", DEFAULT_PARAMETERS )
        parameters.unserialize( defaults )
        self.update_ui_from_parameters( parameters )

    def on_save_defaults( self ):
        settings = QSettings()

        parameters = MaskParameters()
        self.update_parameters_from_ui( parameters )
        defaults = parameters.serialize()
        settings.setValue( "mask_plugin/defaults", defaults )

    def on_file_browse( self ):
        settings = QSettings()

        # look for directory
        path = QgsProject.instance().homePath()
        if path == '':
            path = settings.value("mask_plugin/file_dir", '')
            if path == '':
                path = QDir.homePath()

        drivers = QgsVectorFileWriter.ogrDriverList()
        filterList = []
        filterMap = {}
        for ln, n in drivers.iteritems():
            # grrr, driverMetadata is not really consistent
            if n == "ESRI Shapefile":
                ext = "shp"
                glob = "*.shp"
            else:
                md = QgsVectorFileWriter.MetaData()
                if QgsVectorFileWriter.driverMetadata( n, md ):
                    ext = md.ext
                    glob = md.glob
                else:
                    continue

            fn = "%s (%s)" % (ln,glob)
            filterMap[fn] = (n, ext, glob)
            filterList += [ fn ]


        fileFilters = ';;'.join( filterList )
        fd = QFileDialog( None, self.tr("Select a filename to save the mask layer to"), path, fileFilters )
        save_format_name = self.parameters.file_format
        self.save_format = None
        for k,v in filterMap.iteritems():
            if v[0] == save_format_name:
                self.save_format = v
                fd.selectNameFilter( k )
                break

        def on_filter_selected( ff ):
            self.save_format = filterMap[ff]

        fd.filterSelected.connect( on_filter_selected )
        fd.setAcceptMode( QFileDialog.AcceptSave )
        r = fd.exec_()
        if r == 1:
            fn = fd.selectedFiles()[0]
            driver, ext, glob = self.save_format
            if not fn.endswith("." + ext):
                fn += "." + ext

            self.ui.filePath.setText( fn )
            self.ui.formatLbl.setText( self.save_format[0] )
            self.parameters.file_format = self.save_format[0]

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
        if not is_in_qgis_core('QgsMapToPixelSimplifier'):
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
        self.apply()
        QDialog.accept( self )

    def apply( self ):
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


    def on_apply( self ):
        self.apply()
        self.applied.emit()



