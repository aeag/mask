from qgis.core import QgsMessageLog, QgsReadWriteContext
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtXml import QDomDocument, QDomImplementation

from mask.__about__ import DIR_PLUGIN_ROOT

from .mask_parameters import MaskParameters


def set_layer_symbology(layer, symbology):
    if symbology is not None:
        doc = QDomDocument("qgis")
        doc.setContent(symbology)
        errorMsg = ""
        ctx = QgsReadWriteContext()
        r = layer.readSymbology(doc.firstChildElement("qgis"), errorMsg, ctx)
        QgsMessageLog.logMessage(f"set_layer_symbology {r}", "Extensions")


def get_layer_symbology(layer):
    doc = QDomDocument(
        QDomImplementation().createDocumentType(
            "qgis", "http://mrcc.com/qgis.dtd", "SYSTEM"
        )
    )
    rootNode = doc.createElement("qgis")
    doc.appendChild(rootNode)
    errorMsg = ""
    ctx = QgsReadWriteContext()
    layer.writeSymbology(rootNode, doc, errorMsg, ctx)
    return doc.toByteArray()


def set_default_layer_symbology(layer):
    """Applique le style par défaut (du QGis/ini) à la couche
    A partir du fichier QML sinon

    Args:
        layer (QgsVectorLayer): La couche masque
    """

    settings = QSettings()

    parameters = MaskParameters()
    defaults = settings.value("mask/defaults", None)
    if defaults is not None:
        parameters.unserialize(defaults)

        QgsMessageLog.logMessage(
            f"set_default_layer_symbology LAYER= {layer}", "Extensions"
        )
        QgsMessageLog.logMessage(
            f"set_default_layer_symbology STYLE= {parameters.style}", "Extensions"
        )

        set_layer_symbology(layer, parameters.style)

        s = get_layer_symbology(layer)
        QgsMessageLog.logMessage(
            f"set_default_layer_symbology AFTER= {s}", "Extensions"
        )
    else:
        default_style = str(DIR_PLUGIN_ROOT / "resources" / "default_mask_style.qml")
        layer.loadNamedStyle(default_style)
