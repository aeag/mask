from qgis.core import *

SPATIAL_FILTER = "$in_mask"

def has_mask_filter( layer ):
    # check if a layer has already a mask filter enabled
    pal = QgsPalLayerSettings()
    pal.readFromLayer( layer )
    if not pal.enabled:
        return False
    show_expr = pal.dataDefinedProperties.get( QgsPalLayerSettings.Show )
    if show_expr is None:
        return False
    return show_expr.expressionString() == SPATIAL_FILTER

def remove_mask_filter( pal ):
    npal = QgsPalLayerSettings( pal )
    if npal.enabled and npal.dataDefinedProperties.get( QgsPalLayerSettings.Show ) is not None and \
            npal.dataDefinedProperties[ QgsPalLayerSettings.Show ].expressionString() == SPATIAL_FILTER:
        npal.dataDefinedProperties = dict([(k,v) for k,v in npal.dataDefinedProperties.iteritems() if k != QgsPalLayerSettings.Show] )
    return npal

def add_mask_filter( pal ):
    npal = QgsPalLayerSettings( pal )
    npal.setDataDefinedProperty( QgsPalLayerSettings.Show, True, True, SPATIAL_FILTER, '' )
    return npal
