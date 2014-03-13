from qgis.core import *

SPATIAL_FILTER_BEGIN = "CASE WHEN $in_mask THEN "
SPATIAL_FILTER_END = " ELSE '' END"

def has_mask_filter( layer ):
    # check if a layer has already a mask filter enabled
    pal = QgsPalLayerSettings()
    pal.readFromLayer( layer )
    if not pal.enabled:
        return False
    return pal.fieldName.find(SPATIAL_FILTER_BEGIN) == 0

def remove_mask_filter( pal ):
    npal = QgsPalLayerSettings( pal )
    if npal.enabled and npal.fieldName.find(SPATIAL_FILTER_BEGIN) == 0:
        l = len(npal.fieldName)
        l1 = len(SPATIAL_FILTER_BEGIN)
        l2 = len(SPATIAL_FILTER_END)
        npal.fieldName = npal.fieldName[l1:l-l2]
    return npal

def add_mask_filter( pal ):
    npal = QgsPalLayerSettings( pal )
    npal.fieldName = SPATIAL_FILTER_BEGIN + npal.fieldName + SPATIAL_FILTER_END
    npal.isExpression = True
    return npal

