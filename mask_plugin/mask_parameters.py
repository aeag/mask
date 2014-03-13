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

class MaskParameters:
    def __init__( self ):
        # selection | mask
        self.mask_mode = 'mask'
        self.do_buffer = False
        self.buffer_units = 1
        self.buffer_segments = 5
        self.do_simplify = True
        self.simplify_tolerance = 1.0
        self.do_save_as = False
        self.file_path = None
        self.file_format = None
        self.style = None

        # layers (list of id) where labeling has to be limited
        self.limited_layers = []

        self.geometry = None

    def serialize( self ):
        return pickle.dumps([self.mask_mode,
                             self.do_buffer,
                             self.buffer_units,
                             self.buffer_segments,
                             self.do_simplify,
                             self.simplify_tolerance,
                             self.do_save_as,
                             self.file_path,
                             self.file_format,
                             self.limited_layers,
                             self.style])

    def unserialize( self, st ):
        (self.mask_mode,
         self.do_buffer,
         self.buffer_units,
         self.buffer_segments,
         self.do_simplify,
         self.simplify_tolerance,
         self.do_save_as,
         self.file_path,
         self.file_format,
         self.limited_layers,
         self.style) = pickle.loads( st )

    def load_from_layer( self, layer ):
        # try to load parameters from a mask layer

        # return False on failure
        pr = layer.dataProvider()
        fields = pr.fields()
        print fields
        if fields.size() < 1:
            return False
        if fields[0].name() != 'params':
            return False

        it = pr.getFeatures()
        fet = QgsFeature()
        it.nextFeature(fet)
        self.unserialize( fet.attributes()[0] )
        self.geometry = QgsGeometry( fet.geometry() )

        return True

    def save_to_layer( self, layer ):
        # store parameters to the given layer
        serialized = self.serialize()
        # insert or replace into ...
        pr = layer.dataProvider()
        if pr.featureCount() == 0:
            # add a text attribute to store parameters
            layer.startEditing()
            layer.addAttribute( QgsField( "params", QVariant.String ) )
            # id1 : geometry + parameters
            fet1 = QgsFeature()
            fet1.setAttributes( [serialized] )
            fet1.setGeometry(self.geometry)
            pr.addFeatures([ fet1 ])
            layer.commitChanges()
        else:
            pr.changeAttributeValues( { 1 : { 0 : serialized } } )
            pr.changeGeometryValues( { 1 : self.geometry } )
        layer.updateExtents()
