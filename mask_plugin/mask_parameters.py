"""
Class to store mask parameters

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from qgis.core import *
import pickle
import base64

class MaskParameters:
    def __init__( self ):
        # selection | mask
        self.do_buffer = False
        self.buffer_units = 1
        self.buffer_segments = 5
        self.do_simplify = True
        self.simplify_tolerance = 1.0
        self.do_save_as = False
        self.file_path = None
        self.file_format = None
        self.style = None
        # polygon mask method : 0: exact, 1: centroid, 2: pointOnSurface
        self.polygon_mask_method = 2
        # line mask method = 0: intersects, 1: contains
        self.line_mask_method = 0

        # layers (list of id) where labeling has to be limited
        self.limited_layers = []

        self.geometry = None

    def serialize( self, with_style = True ):
        if with_style:
            style = self.style
        else:
            style = None
        return pickle.dumps([self.do_buffer,
                             self.buffer_units,
                             self.buffer_segments,
                             self.do_simplify,
                             self.simplify_tolerance,
                             self.do_save_as,
                             self.file_path,
                             self.file_format,
                             self.limited_layers,
                             style,
                             self.polygon_mask_method,
                             self.line_mask_method])

    def unserialize( self, st ):
        (self.do_buffer,
         self.buffer_units,
         self.buffer_segments,
         self.do_simplify,
         self.simplify_tolerance,
         self.do_save_as,
         self.file_path,
         self.file_format,
         self.limited_layers,
         style,
         self.polygon_mask_method,
         self.line_mask_method
         ) = pickle.loads( st )
        if style is not None:
            self.style = style

    def load_from_layer( self, layer ):
        # try to load parameters from a mask layer

        # return False on failure
        pr = layer.dataProvider()
        fields = pr.fields()
        if fields.size() < 1:
            return False
        field = None
        for i, f in enumerate(fields):
            if f.name() == "params":
                field = i
        if field is None:
            return False

        it = pr.getFeatures()
        fet = QgsFeature()
        it.nextFeature(fet)
        st = fet.attributes()[field]
        self.unserialize( base64.b64decode(st) )
        self.geometry = QgsGeometry( fet.geometry() )

        return True

    def save_to_layer( self, layer ):
        # do not serialize style (for shapefiles)
        serialized = base64.b64encode( self.serialize( with_style = False ) )
        # insert or replace into ...
        pr = layer.dataProvider()
        if pr.featureCount() == 0:
            if pr.fields().size() == 0:
                layer.startEditing()
                ok = layer.addAttribute( QgsField( "params", QVariant.String) )
                if not ok:
                    print "problem adding attribute (save_to_layer)"
                layer.commitChanges()

            # id1 : geometry + parameters
            fet1 = QgsFeature()
            fet1.setAttributes( [serialized] )
            fet1.setGeometry(self.geometry)
            pr.addFeatures([ fet1 ])
        else:
            # get the first feature
            it = pr.getFeatures()
            fet = QgsFeature()
            ok = it.nextFeature(fet)

            ok = pr.changeAttributeValues( { fet.id() : { 0 : serialized } } )
            ok = pr.changeGeometryValues( { fet.id() : self.geometry } )
        layer.updateExtents()
