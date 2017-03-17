"""
/***************************************************************************
Name                  : Mask 
Description          : Aide à la création de masque
Date                 : Feb/12 
copyright            : (C) 2011 by AEAG
                       (c) 2014 Oslandia
email                : xavier.culos@eau-adour-garonne.fr 
                       hugo.mercier@oslandia.com
todo: 

 add help file
 let's user change user defined parameters. 
 use a qml file to set masqk style. default qml inside plugin ? 
   Parameter 1: choose memory output or shp output + directory (default HOME directory)
   Parameter 2 : choose a qml file. Qml should be parsed to check if qymbology apply to polygon features

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

# Import the PyQt and QGIS libraries
import os
from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from qgis.core import *
# for user-defined functions
from qgis.utils import qgsfunction

from .maindialog import MainDialog
from .layerlist import LayerListDialog
from .mask_filter import *
from .mask_parameters import *
from .htmldialog import HtmlDialog
from . import style_tools

# Initialize Qt resources from file resources.py
from . import resources_rc

_fromUtf8 = lambda s: (s.decode("utf-8").encode("latin-1")) if s else s
_toUtf8 = lambda s: s.decode("latin-1").encode("utf-8") if s else s

aeag_mask_instance = None

# to be called from another plugin
# from mask import aeag_mask
# aeag_mask.do()
def do(crs=None, poly=None, name=None):
    # crs = QgsCoordinateReferenceSystem
    # poly = list of geometries
    global aeag_mask_instance
    this = aeag_mask_instance
    this.layer = this.apply_mask_parameters(this.layer, this.parameters, crs, poly, name, keep_layer = False )
    this.save_to_project( this.layer, this.parameters )

def is_in_qgis_core( sym ):
    import qgis.core
    return sym in dir(qgis.core)

class MaskGeometryFunction( QgsExpression.Function ):
    def __init__( self, mask ):
        QgsExpression.Function.__init__(self, "$mask_geometry", 0, "Python", self.tr("""<h1>$mask_geometry</h1>
Variable filled by mask plugin.<br/>
When mask has been triggered on some polygon, mask_geometry is filled with the mask geometry and can be reused for expression/python calculation. in_mask variable uses that geometry to compute a boolean.
<h2>Return value</h2>
The geometry of the current mask
        """))
        self.mask = mask

    def tr(self, message):
        return QCoreApplication.translate('MaskGeometryFunction', message)

    def func(self, values, feature, parent):
        return self.mask.mask_geometry()[0]

class InMaskFunction( QgsExpression.Function ):
    def __init__( self, mask ):
        QgsExpression.Function.__init__(self, "in_mask", 1, "Python", self.tr("""<h1>in_mask function</h1>
Expression function added by mask plugin. Returns true if current feature crosses mask geometry.<br/>
The spatial expression to use is set from the mask UI button (exact, fast using centroids, intermediate using point on surface).<br/>
in_mask takes a CRS EPSG code as first parameter, which is the CRS code of the evaluated features.<br/>
It can be used to filter labels only in that area, or since QGIS 2.13, legend items only visible in mask area.<br/> 
<h2>Return value</h2>
true/false (0/1)<br/>
<h2>Usage</h2>
in_mask(2154)"""))
        self.mask = mask

    def tr(self, message):
        return QCoreApplication.translate('InMaskFunction', message)

    def func(self, values, feature, parent):
        return self.mask.in_mask( feature, values[0] )

class aeag_mask(QObject):

    def __init__(self, iface):
        QObject.__init__( self )

        global aeag_mask_instance
        aeag_mask_instance = self

        # install translator
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'mask_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Save reference to the QGIS interface
        self.iface = iface
        self.toolBar = None
        self.act_aeag_mask = None
        self.act_aeag_toolbar_help = None
        self.canvas = self.iface.mapCanvas()

        self.composers = {}

        # test qgis version for the presence of signals
        self.has_atlas_signals = 'renderBegun' in dir(QgsAtlasComposition)
        # test qgis version for the presence of the simplifier
        self.has_simplifier = is_in_qgis_core('QgsMapToPixelSimplifier')
        # test qgis version for the presence of pointOnSurface
        self.has_point_on_surface = 'pointOnSurface' in dir(QgsGeometry)

        self.MASK_NAME = "Mask"

        self.reset_mask_layer()

    def reset_mask_layer( self ):
        self.layer = None
        # mask parameters
        self.parameters = MaskParameters()

        self.save_to_project( self.layer, self.parameters )

        for name, layer in QgsMapLayerRegistry.instance().mapLayers().items():
            if has_mask_filter( layer ):
                # remove mask filter from layer, if any
                pal = QgsPalLayerSettings()
                pal.readFromLayer( layer )
                pal = remove_mask_filter( pal )
                pal.writeToLayer( layer )

        self.simplified_geometries = {}

    def initGui(self):  
        self.mask_geometry_function = MaskGeometryFunction( self )
        QgsExpression.registerFunction( self.mask_geometry_function )
        self.in_mask_function = InMaskFunction( self )
        QgsExpression.registerFunction( self.in_mask_function )

        #
        self.disable_remove_mask_signal = False
        self.disable_add_layer_signal = False
        self.registry = QgsMapLayerRegistry.instance()
        self.registry.layerWillBeRemoved.connect( self.on_remove_mask )

        self.act_aeag_mask = QAction(QIcon(":plugins/mask/aeag_mask.png"), self.tr("Create a mask"), self.iface.mainWindow())

        # Specific to AEAG for internal integration. Please keep it
        try:
            from aeag import aeag
            self.toolBar = aeag.aeagToolbarAdd(self.act_aeag_mask)
        except:
            self.toolBar = self.iface.pluginToolBar()
            self.toolBar.addAction(self.act_aeag_mask)
            self.iface.addPluginToMenu("&Mask", self.act_aeag_mask)    

        # turn it to true to enable test
        if False:
            self.act_test = QAction(QIcon(":plugins/mask/aeag_mask.png"), _fromUtf8("Test"), self.iface.mainWindow())
            self.toolBar.addAction( self.act_test )
            self.iface.addPluginToMenu("&Mask", self.act_test)
            self.act_test.triggered.connect(self.do_test)

        # Add documentation links to the menu
        self.act_aeag_about = QAction( self.tr("About"), self.iface.mainWindow() )
        self.act_aeag_about.triggered.connect( self.on_about )
        self.act_aeag_doc = QAction( self.tr("Documentation"), self.iface.mainWindow() )
        self.act_aeag_doc.triggered.connect( self.on_doc )
        self.iface.addPluginToMenu("&Mask", self.act_aeag_about)
        self.iface.addPluginToMenu("&Mask", self.act_aeag_doc)
        
        # Add actions to the toolbar
        self.act_aeag_mask.triggered.connect(self.run)
        
        # look for an existing mask layer
        mask_id, ok = QgsProject.instance().readEntry( "Mask", "layer_id" )
        self.layer = self.registry.mapLayer( mask_id )

        if self.has_atlas_signals:
            # register composer signals
            self.iface.composerAdded.connect( self.on_composer_added )
            self.iface.composerWillBeRemoved.connect( self.on_composer_removed )

            # register already existing composers
            for compo in self.iface.activeComposers():
                self.on_composer_added( compo )

        # register to the change of active layer for enabling/disabling of the action
        self.old_active_layer = None
        self.iface.mapCanvas().currentLayerChanged.connect( self.on_current_layer_changed )
        self.on_current_layer_changed( None )

        # register to project reading
        # connect to QgisApp::projectRead to make sure MemoryLayerSaver has been called before (it connects to QgsProject::readProject)
        self.iface.mainWindow().projectRead.connect( self.on_project_open )

    def load_from_project( self ):
        # return layer, parameters
        parameters = MaskParameters()
        ok = parameters.load_from_project()
        if not ok:
            # no parameters in the project
            # look for a vector layer called 'Mask'
            for id, l in list(QgsMapLayerRegistry.instance().mapLayers().items()):
                if l.type() == QgsMapLayer.VectorLayer and l.name() == 'Mask':
                    return self.load_from_layer(l)

        layer_id, ok = QgsProject.instance().readEntry( "Mask", "layer_id" )
        layer = QgsMapLayerRegistry.instance().mapLayer( layer_id )
        return layer, parameters

    def save_to_project( self, layer, parameters ):
        QgsProject.instance().writeEntry( "Mask", "layer_id", layer.id() if layer else "" )
        parameters.save_to_project()

    def on_project_open( self ):
        self.layer, self.parameters = self.load_from_project()

        if self.layer is not None:
            self.layer = self.apply_mask_parameters( self.layer, self.parameters, dest_crs = None, poly = None, name = self.layer.name(), keep_layer = False )
            self.act_aeag_mask.setEnabled( True )

    def on_current_layer_changed( self, layer ):
        if self.layer is None:
            _, poly = self.get_selected_polygons()
            self.act_aeag_mask.setEnabled( poly != [] )
        else:
            self.act_aeag_mask.setEnabled( True )

        if layer and layer.type() != QgsMapLayer.VectorLayer:
            self.old_active_layer = None
            return

        if self.old_active_layer is not None:
            self.old_active_layer.selectionChanged.disconnect( self.on_current_layer_selection_changed )
        if layer is not None:
            layer.selectionChanged.connect( self.on_current_layer_selection_changed )

        if layer != self.old_active_layer:
            self.old_active_layer = layer

    def on_current_layer_selection_changed( self ):
        if self.layer is None:
            _, poly = self.get_selected_polygons()
            self.act_aeag_mask.setEnabled( poly != [] )

    def unload(self):
        # Specific to AEAG for internal integration. Please keep it
        try:
            from aeag import aeag
            self.toolBar = aeag.aeagToolbarRemove(self.toolBar, self.act_aeag_mask)
        except:
            self.toolBar.removeAction(self.act_aeag_mask)
            self.iface.removePluginMenu("&Mask", self.act_aeag_mask)

        if False:
            self.toolBar.removeAction(self.act_test)
            self.iface.removePluginMenu("&Mask", self.act_test)

        # remove doc links
        self.iface.removePluginMenu("&Mask", self.act_aeag_about)
        self.iface.removePluginMenu("&Mask", self.act_aeag_doc)

        QgsExpression.unregisterFunction( "$mask_geometry" )
        QgsExpression.unregisterFunction( "in_mask" )

        self.registry.layerWillBeRemoved.disconnect( self.on_remove_mask )

        if self.has_atlas_signals:
            self.iface.composerAdded.disconnect( self.on_composer_added )
            self.iface.composerWillBeRemoved.disconnect( self.on_composer_removed )
            # remove composer signals
            for compo in self.iface.activeComposers():
                self.on_composer_removed( compo )

        self.iface.mapCanvas().currentLayerChanged.disconnect( self.on_current_layer_changed )
        self.iface.mainWindow().projectRead.disconnect( self.on_project_open )

    def on_about( self ):
        dlg = HtmlDialog( None, "about.html" )
        dlg.exec_()

    def on_doc( self ):
        QDesktopServices.openUrl(QUrl("https://github.com/aeag/mask/wiki"))

    # force loading of parameters from a layer
    # for backward compatibility with older versions
    def load_from_layer( self, layer ):
        # return layer, parameters
        parameters = MaskParameters()
        ok = parameters.load_from_layer(layer)
        if not ok:
            return layer, parameters
        QgsProject.instance().writeEntry( "Mask", "layer_id", layer.id() )
        layer = self.apply_mask_parameters(layer, parameters, dest_crs = None, poly = None, name = layer.name(), keep_layer = False)
        return layer, parameters

    def on_composer_added( self, compo ):
        composition = compo.composition()
        self.composers[composition] = []
        items = composition.composerMapItems()
        composition.atlasComposition().renderBegun.connect( self.on_atlas_begin_render )
        composition.atlasComposition().renderEnded.connect( self.on_atlas_end_render )

        composition.composerMapAdded.connect( lambda item: self.on_composer_map_added(composition, item) )
        composition.itemRemoved.connect( lambda item: self.on_composer_item_removed(composition,item) )
        for item in items:
            if item.type() == QgsComposerItem.ComposerMap:
                self.on_composer_map_added( composition, item )

    def on_composer_map_added( self, compo, item ):
        # The second argument, which is supposed to be a QgsComposerMap is always a QObject.
        # ?! So we circumvent this problem in passing the QgsComposition container
        # and getting track of composer maps
        for composer_map in compo.composerMapItems():
            if composer_map not in self.composers[compo]:
                self.composers[compo].append(composer_map)
                composer_map.preparedForAtlas.connect( lambda this=self,c=compo: this.on_prepared_for_atlas(c, composer_map) )
                break

    def on_composer_item_removed( self, compo, _ ):
        for composer_map in self.composers[compo]:
            if composer_map not in compo.composerMapItems():
                self.composers[compo].remove(composer_map)
                composer_map.preparedForAtlas.disconnect()
                break

    def on_composer_removed( self, compo ):
        composition = compo.composition()
        items = composition.composerMapItems()
        composition.atlasComposition().renderBegun.disconnect( self.on_atlas_begin_render )
        composition.atlasComposition().renderEnded.disconnect( self.on_atlas_end_render )
        composition.composerMapAdded.disconnect()
        composition.itemRemoved.disconnect()
        for item in items:
            self.on_composer_item_removed( composition, item )
        del self.composers[composition]

    def compute_mask_geometries( self, parameters, poly ):
        geom = None
        for g in poly:
            if geom is None:
                geom = QgsGeometry(g)
            else:
                # do an union here
                geom = geom.combine( g )

        if parameters.do_buffer:
            geom = geom.buffer( parameters.buffer_units, parameters.buffer_segments )

        # reset the simplified geometries dict
        self.simplified_geometries = {}

        return geom

    def on_prepared_for_atlas( self, compo, item ):
        # called for each atlas feature
        if not self.layer:
            return

        if hasattr(compo.atlasComposition(), "currentGeometry"): #qgis 2.14
            geom = compo.atlasComposition().currentGeometry()
        elif hasattr(compo, "createExpressionContext"): #qgis 2.12
            ctxt = compo.createExpressionContext()
            e = QgsExpression("@atlas_geometry")
            geom = e.evaluate(ctxt)
        else:
            geom = QgsExpression.specialColumn("$atlasgeometry")

        masked_atlas_geometry = [geom]
        self.layer = self.apply_mask_parameters( self.layer,
                                                 self.parameters, dest_crs = self.layer.crs(),
                                                 poly = masked_atlas_geometry,
                                                 name = self.layer.name(),
                                                 cleanup_and_zoom = False # no need to zoom, it has already been scaled by atlas
                                                 )
 
        # update maps
        for compoview in self.iface.activeComposers():
            if compoview.composition().atlasMode() == QgsComposition.PreviewAtlas:
                # process events to go out of the current rendering, if any
                QCoreApplication.processEvents()
                compoview.composition().refreshItems()

    def on_atlas_begin_render( self ):
        if not self.layer:
            return

        # save the mask geometry
        self.geometries_backup = [ QgsGeometry(g) for g in self.parameters.orig_geometry]

    def on_atlas_end_render( self ):
        if not self.layer:
            return

        # restore the mask geometry
        self.parameters.orig_geometry = self.geometries_backup
        self.layer = self.apply_mask_parameters( self.layer,
                                                 self.parameters,
                                                 dest_crs = None,
                                                 poly = None,
                                                 name = self.layer.name(),
                                                 cleanup_and_zoom = False # no need to zoom, it has already been scaled by atlas
                                                 )
        self.simplified_geometries = {}

        # process events to go out of the current rendering, if any
        QCoreApplication.processEvents()
        # update maps
        for compoview in self.iface.activeComposers():
            compoview.composition().refreshItems()

    def apply_mask_parameters( self, layer, parameters, dest_crs = None, poly = None, name = None, cleanup_and_zoom = True, keep_layer = True ):
        # Apply given mask parameters to the given layer. Returns the new layer
        # The given layer is removed and then recreated in the layer tree
        # if poly is not None, it is used as the mask geometry
        # else, the geometry is taken from parameters.geometry
        if name is None:
            mask_name = self.MASK_NAME
        else:
            mask_name = name

        if poly is None:
            dest_crs, poly = self.get_selected_polygons()
            if poly == [] and (parameters.orig_geometry is not None) and (layer is not None):
                dest_crs = layer.crs()
                poly = parameters.orig_geometry
            
        if layer is None and poly is None:
            QMessageBox.critical( None, self.tr("Mask plugin error"), self.tr("No polygon selection !") )
            return
        
        if layer is None:
            # create a new layer
            layer = QgsVectorLayer("MultiPolygon?crs=%s" % dest_crs.authid(), mask_name, "memory")
            style_tools.set_default_layer_symbology( layer )
            # add a mask filter to all layer
            for name, l in self.registry.mapLayers().items():
                if not isinstance(l, QgsVectorLayer):
                    continue
                pal = QgsPalLayerSettings()
                pal.readFromLayer(l)
                if not pal.enabled:
                    continue
                npal = add_mask_filter( pal, l )
                npal.writeToLayer( l )

        parameters.layer = layer
        # compute the geometry
        parameters.orig_geometry = [ QgsGeometry(g) for g in poly ]
        parameters.geometry = self.compute_mask_geometries( parameters, poly )

        # disable rendering
        self.canvas.setRenderFlag( False )

        if not keep_layer:
            # save layer's style
            layer_style = self.get_layer_style( layer )
            # remove the old layer
            self.disable_remove_mask_signal = True
            self.registry.removeMapLayer( layer.id() )
            self.disable_remove_mask_signal = False

            # (re)create the layer
            is_mem = not parameters.do_save_as
            nlayer = None
            try:
                nlayer = self.create_layer( parameters, mask_name, is_mem, dest_crs, layer_style )
            except RuntimeError as ex:
                e = ex.message
                if e == 1:
                    QMessageBox.critical( None, self.tr("Mask plugin error"), self.tr("Driver not found !") )
                elif e == 2:
                    QMessageBox.critical( None, self.tr("Mask plugin error"), self.tr("Cannot create data source !") )
                elif e == 3:
                    QMessageBox.critical( None, self.tr("Mask plugin error"), self.tr("Cannot create layer !") )
                elif e == 4:
                    QMessageBox.critical( None, self.tr("Mask plugin error"), self.tr("Attribute type unsupported !") )
                elif e == 5:
                    QMessageBox.critical( None, self.tr("Mask plugin error"), self.tr("Attribute creation failed !") )
                elif e == 6:
                    QMessageBox.critical( None, self.tr("Mask plugin error"), self.tr("Projection error !") )
                elif e == 7:
                    QMessageBox.critical( None, self.tr("Mask plugin error"), self.tr("Feature write failed !") )
                elif e == 8:
                    QMessageBox.critical( None, self.tr("Mask plugin error"), self.tr("Invalid layer !") )
                return

            if nlayer is None:
                QMessageBox.critical( None, self.tr("Mask plugin error"), self.tr("Problem saving the mask layer") )
                return

            # add the new layer
            layer = nlayer
            QgsProject.instance().writeEntry( "Mask", "layer_id", nlayer.id() )
            self.add_layer( layer )
            parameters.layer = layer
        else:
            # replace the mask geometry
            pr = layer.dataProvider()
            fid = 0
            for f in pr.getFeatures():
                fid = f.id()
            pr.changeGeometryValues( {fid: parameters.geometry} )
        
        if cleanup_and_zoom:
            #RH 04 05 2015 > clean up selection of all layers 
            for l in self.canvas.layers():
                if l.type() != QgsMapLayer.VectorLayer:
                    # Ignore this layer as it's not a vector
                    continue
                if l.featureCount() == 0:
                    # There are no features - skip
                    continue
                l.removeSelection()

            #RH 04 05 2015 > zooms to mask layer
            canvas = self.iface.mapCanvas()
            extent = layer.extent()
            extent.scale(1.1) #scales extent by 10% unzoomed
            canvas.setExtent(extent)
        
        # refresh
        self.canvas.clearCache()
        self.canvas.setRenderFlag( True ) # will call refresh

        return layer

    # run method that performs all the real work
    def run( self ):
        dest_crs, poly = self.get_selected_polygons()
        is_new = False


        layer, parameters = self.load_from_project()

        if not layer:
            if not poly:
                QMessageBox.critical( None, self.tr("Mask plugin error"), self.tr("No polygon selection !") )
                return
            layer = QgsVectorLayer("MultiPolygon?crs=%s" % dest_crs.authid(), self.MASK_NAME, "memory")
            style_tools.set_default_layer_symbology( layer )
            is_new = True
        

        parameters.layer = layer

        dlg = MainDialog( parameters, is_new )

        # for "Apply" and "Ok"
        self.layer = layer
        def on_applied_():
            keep_layer = not is_new and self.parameters.have_same_layer_options( parameters )
            new_layer = self.apply_mask_parameters( self.layer, parameters, keep_layer = keep_layer )
            self.save_to_project( new_layer, parameters )
            self.layer = new_layer
            self.parameters = parameters        

        # connect apply
        dlg.applied.connect( on_applied_ )
        r = dlg.exec_()
        if r == 1: # Ok
            on_applied_()

        self.update_menus()

    def update_menus( self ):
        # update menus based on whether the layer mask exists or not
        if self.layer is not None:
            self.act_aeag_mask.setText(self.tr("Update the current mask"))
        else:
            self.act_aeag_mask.setText(self.tr("Create a mask"))
        # update icon state
        self.on_current_layer_changed( self.iface.activeLayer() )

    def on_remove_mask( self, layer_id ):
        if self.disable_remove_mask_signal:
            return

        if self.layer is not None and layer_id == self.layer.id():
            self.reset_mask_layer()

        self.update_menus()

    def get_selected_polygons( self ):
        "return array of (polygon_feature,crs) from current selection"
        geos = []
        layer = self.iface.activeLayer()
        if not isinstance(layer, QgsVectorLayer):
            return None, []
        for feature in layer.selectedFeatures():
            if feature.geometry() and feature.geometry().type() == QGis.Polygon:
                geos.append( QgsGeometry(feature.geometry()) )
        return layer.crs(), geos

    def add_layer( self, layer ):
        # add a layer to the registry, if not already there
        layers = self.registry.mapLayers()
        for name, alayer in layers.items():
            if alayer == layer:
                return

        self.registry.addMapLayer(layer, False)
        # make sure the mask layer is on top of other layers
        lt = QgsProject.instance().layerTreeRoot()
        # insert a new on top
        self.disable_add_layer_signal = True
        lt.insertChildNode( 0, QgsLayerTreeLayer(layer) )
        self.disable_add_layer_signal = False

    def get_layer_style( self, layer ):
        if layer is None:
            return None
        return (layer.layerTransparency(), layer.featureBlendMode(), layer.blendMode(), layer.rendererV2().clone())

    def set_layer_style( self, nlayer, style ):
        nlayer.setLayerTransparency( style[0] )
        nlayer.setFeatureBlendMode( style[1] )
        nlayer.setBlendMode( style[2] )
        nlayer.setRendererV2( style[3] )

    def set_default_layer_style( self, layer ):
        settings = QSettings()

        parameters = MaskParameters()
        defaults = settings.value( "mask/defaults", None )
        if defaults is not None:
            parameters.unserialize( defaults )
        else:
            default_style = os.path.join( os.path.dirname(__file__), "default_mask_style.qml" )
            layer.loadNamedStyle( default_style )

    def create_layer( self, parameters, name, is_memory, dest_crs, layer_style = None ):
        save_as = parameters.file_path
        file_format = parameters.file_format
        # save paramaters
        serialized = base64.b64encode( parameters.serialize(with_style = False, with_geometry = False) )

        # save geometry
        layer = QgsVectorLayer("MultiPolygon?crs=%s" % dest_crs.authid(), name, "memory")
        pr = layer.dataProvider()
        layer.startEditing()
        ok = layer.addAttribute( QgsField( "params", QVariant.String) )
        fet1 = QgsFeature(0)
        fet1.setAttributes( [serialized] )
        fet1.setGeometry(parameters.geometry)
        ok = pr.addFeatures([ fet1 ])
        layer.commitChanges()

        # copy layer style
        if layer_style is not None:
            self.set_layer_style( layer, layer_style )


        if is_memory:
            return layer

        if os.path.isfile( save_as ):
            # delete first if already exists
            if save_as.endswith(".shp"):
                QgsVectorFileWriter.deleteShapeFile( save_as )
            else:
                os.unlink( save_as )

        # create the disk layer
        error = QgsVectorFileWriter.writeAsVectorFormat( layer,
                                                         save_as,
                                                         "System",
                                                         dest_crs,
                                                         file_format)
        if error == 0:
            nlayer = QgsVectorLayer( save_as, name, "ogr" )
            if not nlayer.dataProvider().isValid():
                return None
            if not nlayer.hasGeometryType():
                return None
            # force CRS
            nlayer.setCrs( dest_crs )

            # copy layer style
            layer_style = self.get_layer_style( layer )
            self.set_layer_style( nlayer, layer_style )
            return nlayer
        else:
            raise RuntimeError(error)
        return None

    def mask_geometry( self ):
        if not self.parameters.geometry:
            geom = QgsGeometry()
            return geom, QgsRectangle()

        geom = QgsGeometry(self.parameters.geometry) # COPY !!

        if self.parameters.do_simplify:
            if hasattr( self.canvas, 'mapSettings' ):
                tol = self.parameters.simplify_tolerance * self.canvas.mapSettings().mapUnitsPerPixel()
            else:
                tol = self.parameters.simplify_tolerance * self.canvas.mapRenderer().mapUnitsPerPixel()

            if tol in list(self.simplified_geometries.keys()):
                geom, bbox = self.simplified_geometries[tol]
            else:
                if self.has_simplifier:
                    QgsMapToPixelSimplifier.simplifyGeometry( geom, 1, tol )
                    if not geom.isGeosValid():
                        # make valid
                        geom = geom.buffer( 0.0, 1 )
                bbox = geom.boundingBox()
                self.simplified_geometries[tol] = (QgsGeometry(geom), QgsRectangle(bbox) )
        else:
            bbox = geom.boundingBox()

        return geom, bbox

    def in_mask( self, feature, srid ):
        if feature is None: # expression overview
            return False
        if self.layer is None:
            return False

        try:
            # layer is not None but destroyed ?
            self.layer
        except:
            self.reset_mask_layer()
            return False;
            
        # mask layer empty due to unloaded memlayersaver plugin > no filtering  
        if  self.layer.featureCount()==0 : 
            return True;
        

        mask_geom, bbox = self.mask_geometry()
        geom = QgsGeometry( feature.geometry() )
        if not geom.isGeosValid():
            geom = geom.buffer( 0.0, 1 )
        if geom is None:
            print('geometry absente')  #debug 

            return False


        if self.layer.crs().postgisSrid() != srid:
            src_crs = QgsCoordinateReferenceSystem( srid )
            dest_crs = self.layer.crs()
            xform = QgsCoordinateTransform( src_crs, dest_crs )
            geom.transform( xform )
        
        if geom.type() == QGis.Polygon:
            if self.parameters.polygon_mask_method == 2 and not self.has_point_on_surface:
                self.parameters.polygon_mask_method = 1

            if self.parameters.polygon_mask_method == 0:
                # this method can only work when no geometry simplification is involved
                return ( mask_geom.overlaps(geom) or mask_geom.contains(geom))
            elif self.parameters.polygon_mask_method == 1:
                # the fastest method, but with possible inaccuracies
                pt = geom.vertexAt(0)
                return bbox.contains( pt ) and mask_geom.contains(geom.centroid())
            elif self.parameters.polygon_mask_method == 2:
                # will always work
                pt = geom.vertexAt(0)
                return bbox.contains( pt ) and mask_geom.contains(geom.pointOnSurface())
            else:
                return False
        elif geom.type() == QGis.Line:
            if self.parameters.line_mask_method == 0:
                return mask_geom.intersects(geom)
            elif self.parameters.line_mask_method == 1:
                return mask_geom.contains(geom)
            else:
                return False
        elif geom.type() == QGis.Point:
            return mask_geom.intersects(geom)
        else:
            return False

    def do_test( self ):
        # This test is hard to run without a full QGIS app running
        # with renderer, canvas
        # a layer with labeling filter enabled must be the current layer
        import time

        parameters = [
            # simplify mask layer, simplify label layer, mask_method
            ( False, False, 0 ),
            ( True, True, 0 ), # cannot be used, for reference only
            ( False, False, 1 ),
            ( False, False, 2 ),
            ( True, False, 1 ),
            ( True, False, 2 ),
            ( False, True, 1 ),
            ( False, True, 2 ),
            ( True, True, 1 ),
            ( True, True, 2 )
            ]

        # (False, False, 0) 0.3265
        # (True, True, 0) 0.1790
        # (False, False, 1) 0.2520
        # (False, False, 2) 0.3000
        # (True, False, 1) 0.1950
        # (True, False, 2) 0.2345
        # (False, True, 1) 0.2195
        # (False, True, 2) 0.2315
        # (True, True, 1) 0.1550 <--
        # (True, True, 2) 0.1850 <--

        # the number of time each test must be run
        N = 5

        # layer with labels to filter
        layer = self.iface.activeLayer()

        class RenderCallback:
            # this class deals with asyncrhonous render signals
            def __init__( self, parent, params, layer ):
                self.it = 0
                self.nRefresh = 20
                self.start = time.clock()
                self.parent = parent
                self.params = params
                self.param_it = 0
                self.layer = layer

                self.setup( 0 )
                self.parent.canvas.renderComplete.connect( self.update_render )
                self.parent.canvas.refresh()

            def setup( self, idx ):
                simplify_mask, simplify_label, mask_method = self.params[idx]
                self.parent.parameters.do_simplify = simplify_mask
                self.parent.parameters.simplify_tolerance = 1.0

                m = self.layer.simplifyMethod()
                m.setSimplifyHints( QgsVectorSimplifyMethod.SimplifyHints( 1 if simplify_label else 0 ) )
                self.layer.setSimplifyMethod( m )

                self.parent.mask_method = mask_method
                
            def update_render( self, painter ):
                self.it = self.it + 1
                if self.it < self.nRefresh:
                    self.parent.canvas.refresh()
                else:
                    end = time.clock()
                    print(self.params[self.param_it], "%.4f" % ((end-self.start) / self.nRefresh))
                    self.param_it += 1
                    if self.param_it < len(self.params):
                        self.setup( self.param_it )
                        self.it = 0
                        self.start = end
                        self.parent.canvas.refresh()
                    else:
                        print("end")
                        self.parent.canvas.renderComplete.disconnect( self.update_render )

        self.cb = RenderCallback( self, parameters, layer )





