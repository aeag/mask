from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from qgis.core import *
from qgis.gui import *
from .mask_parameters import *
import os

def set_layer_symbology( layer, symbology ):
    if symbology is not None:
        doc = QDomDocument( "qgis" )
        doc.setContent( symbology )
        errorMsg = ''
        layer.readSymbology( doc.firstChildElement("qgis"), errorMsg )

def get_layer_symbology( layer ):
    doc = QDomDocument( QDomImplementation().createDocumentType( "qgis", "http://mrcc.com/qgis.dtd", "SYSTEM" ) )
    rootNode = doc.createElement( "qgis" );
    doc.appendChild( rootNode );
    errorMsg = ''
    layer.writeSymbology( rootNode, doc, errorMsg )
    return doc.toByteArray()

def set_default_layer_symbology( layer ):
    settings = QSettings()
    
    parameters = MaskParameters()
    defaults = settings.value( "mask/defaults", None )
    if defaults is not None:
        parameters.unserialize( defaults )
        set_layer_symbology( layer, parameters.style )
    else:
        default_style = os.path.join( os.path.dirname(__file__), "default_mask_style.qml" )
        layer.loadNamedStyle( default_style )


