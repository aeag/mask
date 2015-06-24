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

        self.orig_geometry = None
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
                             self.line_mask_method,
                             [ g.asWkb() for g in self.orig_geometry ] if self.orig_geometry is not None else None,
                             self.geometry.asWkb() if self.geometry is not None else None])

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
         self.line_mask_method,
         orig_geom,
         geom
         ) = pickle.loads( st )
        self.style = None
        self.geometry = None
        if style is not None:
            self.style = style
        if geom is not None:
            self.geometry = QgsGeometry()
            self.geometry.fromWkb( geom )
        if orig_geom is not None:
            gl = []
            for g in orig_geom:
                geo = QgsGeometry()
                geo.fromWkb( g )
                gl.append( geo )
            self.orig_geometry = gl

    def have_same_layer_options( self, other ):
        "Returns true if the other parameters have the same layer options (file path, file format) than self"
        if not self.do_save_as:
            return not other.do_save_as
        else:
            if not other.do_save_as:
                return False
            else:
                return self.file_path == other.file_path and self.file_format == other.file_format

    def save_to_project( self ):
        serialized = base64.b64encode( self.serialize() )
        QgsProject.instance().writeEntry( "Mask", "parameters", serialized )
        return True

    def load_from_project( self ):
        st, ok = QgsProject.instance().readEntry( "Mask", "parameters" )
        if st == '':
            return False

        self.unserialize( base64.b64decode(st) )
        return True

