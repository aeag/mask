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

from maindialog import MainDialog

# Initialize Qt resources from file resources.py
import resources_rc

_fromUtf8 = lambda s: (s.decode("utf-8").encode("latin-1")) if s else s
_toUtf8 = lambda s: s.decode("latin-1").encode("utf-8") if s else s

class MaskGeometryFunction( QgsExpression.Function ):
    def __init__( self, mask ):
        QgsExpression.Function.__init__( self, "$mask_geometry", 0, "Python", "Help" )
        self.mask = mask

    def func( self, values, feature, parent ):
        return self.mask.mask_geometry()

class MaskComplementGeometryFunction( QgsExpression.Function ):
    def __init__( self, mask ):
        QgsExpression.Function.__init__( self, "$mask_complement_geometry", 0, "Python", "Help" )
        self.mask = mask

    def func( self, values, feature, parent ):
        return self.mask.mask_complement_geometry()

class aeag_mask: 

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.toolBar = None
        self.act_aeag_mask = None
        self.act_aeag_toolbar_help = None
        self.canvas = self.iface.mapCanvas()
        self.geometry = None
        self.complement_geometry = None

        self.mask_geometry_function = MaskGeometryFunction( self )
        QgsExpression.registerFunction( self.mask_geometry_function )
        self.mask_complement_geometry_function = MaskComplementGeometryFunction( self )
        QgsExpression.registerFunction( self.mask_complement_geometry_function )

        self.labeling_model = {}
        
    def initGui(self):  
        self.toolBar = self.iface.pluginToolBar()
        
        self.act_aeag_mask = QAction(QIcon(":plugins/mask/aeag_mask.png"), _fromUtf8("Create mask"), self.iface.mainWindow())
#        self.act_aeag_mask.setCheckable(True)
        self.toolBar.addAction(self.act_aeag_mask)
        
        self.iface.addPluginToMenu("&Mask", self.act_aeag_mask)    
        
        # Add actions to the toolbar
        self.act_aeag_mask.triggered.connect(self.run)
        
        #add a link to helpfile for toolbar & menu aeag , if not exist


    def unload(self):
        self.toolBar.removeAction(self.act_aeag_mask)
        self.iface.removePluginMenu("&Mask", self.act_aeag_mask)
        QgsExpression.unregisterFunction( "$mask_geometry" )
        QgsExpression.unregisterFunction( "$mask_complement_geometry" )

    # run method that performs all the real work
    def run( self ):
        dest_crs = self.canvas.mapRenderer().destinationCrs()
        mask_layer = QgsVectorLayer("MultiPolygon?crs=%s" % dest_crs.authid(), "Mask", "memory")
        
        dlg = MainDialog( mask_layer )
        dlg.set_labeling_model( self.labeling_model )
        r = dlg.exec_()
        if r == 1:
            poly = self.get_selected_polygons()

            geom = self.get_final_geometry( poly, dest_crs, dlg.do_simplify, dlg.simplify_tolerance )
            if not geom:
                # TODO warn user
                print "no geometry"
                return

            if dlg.do_buffer:
                geom = geom.buffer( dlg.buffer_units, dlg.buffer_segments )

            self.geometry = geom

            rect = self.canvas.extent()
            rect.scale(2)
            mask = QgsGeometry.fromRect( rect )
            self.complement_geometry = mask.difference( geom )

            if dlg.mask_mode == 'mask':
                self.add_layer( mask_layer, self.complement_geometry )
            else:
                self.add_layer( mask_layer, self.geometry )

    def get_selected_polygons( self ):
        "return array of (polygon_feature,crs) from current selection"
        geos = []
        layers = QgsMapLayerRegistry.instance().mapLayers()
        for name, layer in layers.iteritems():
            if not layer.type() == QgsMapLayer.VectorLayer:
                continue
            if not layer.isValid():
                continue
            for feature in layer.selectedFeatures():
                if feature.geometry() and feature.geometry().type() == QGis.Polygon:
                    geos.append( (feature, layer.crs()) )
        return geos

    def get_final_geometry( self, geoms, dest_crs, do_simplify = False, simplify_tol = 0.0 ):
        geom = None
        for f,crs in geoms:
            g = f.geometry()
            if crs.authid() != dest_crs.authid():
                print "transform"
                xform = QgsCoordinateTransform( crs, dest_crs )
                g.transform( xform )

            if do_simplify:
                g = g.simplify( simplify_tol )
            if geom is None:
                geom = QgsGeometry(g)
            else:
                # do an union here
                geom = geom.combine( g )

        return geom

    def add_layer( self, layer, geometry ):

        pr = layer.dataProvider()
        fet = QgsFeature()
        fet.setGeometry(geometry)
        pr.addFeatures([ fet ])
        layer.updateExtents()        
            
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        self.iface.legendInterface().refreshLayerSymbology( layer ) 
        QgsMapLayerRegistry.instance().clearAllLayerCaches () #clean cache to allow mask layer to appear on refresh
        self.canvas.refresh()

    def mask_geometry( self ):
        if not self.geometry:
            return QgsGeometry()
        return self.geometry

    def mask_complement_geometry( self ):
        if not self.complement_geometry:
            return QgsGeometry()
        return self.complement_geometry



