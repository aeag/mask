from qgis.core import (QgsVectorLayer, QgsPalLayerSettings, QgsProperty)

SPATIAL_FILTER = "in_mask"


def has_mask_filter(layer):
    if not isinstance(layer, QgsVectorLayer):
        return False

    # check if a layer has already a mask filter enabled
    pal = QgsPalLayerSettings()
    pal.readFromLayer(layer)
    if not pal.enabled:
        return False

    show_expr = pal.dataDefinedProperties().property(QgsPalLayerSettings.Show)
    if show_expr is None:
        return False

    return show_expr.expressionString().startswith(SPATIAL_FILTER)


def remove_mask_filter(pal):
    npal = QgsPalLayerSettings(pal)
    dprop = npal.dataDefinedProperties()

    if npal.enabled and dprop.property(QgsPalLayerSettings.Show) is not None and \
            dprop.property(QgsPalLayerSettings.Show).expressionString().startswith(SPATIAL_FILTER):
        dprop.setProperty(QgsPalLayerSettings.Show, True)

    return npal


def add_mask_filter(pal, layer):
    npal = QgsPalLayerSettings(pal)
    expr = "%s(%d)" % (SPATIAL_FILTER, layer.crs().postgisSrid())
    prop = QgsProperty()
    prop.setExpressionString(expr)
    npal.dataDefinedProperties().setProperty(QgsPalLayerSettings.Show, prop)

    return npal
