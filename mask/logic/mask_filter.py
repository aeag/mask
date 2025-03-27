#! python3  # noqa: E265

from qgis.core import (
    QgsMessageLog,
    QgsPalLayerSettings,
    QgsProperty,
    QgsRuleBasedLabeling,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)

SPATIAL_FILTER = "in_mask"


def has_mask_filter(layer):
    if not isinstance(layer, QgsVectorLayer):
        return False

    # check if a layer has already a mask filter enabled
    if layer.labeling() is None:
        return False

    # simple labelling
    if isinstance(layer.labeling(), QgsVectorLayerSimpleLabeling):
        settings = layer.labeling().settings()
        show_expr = settings.dataDefinedProperties().property(
            QgsPalLayerSettings.Property.Show
        )
        if show_expr is None:
            return False

        return show_expr.expressionString().startswith(SPATIAL_FILTER)

    # rules based labeling
    if isinstance(layer.labeling(), QgsRuleBasedLabeling):
        # we test only the first rule
        for rule in layer.labeling().rootRule().children():
            settings = rule.settings()
            show_expr = settings.dataDefinedProperties().property(
                QgsPalLayerSettings.Property.Show
            )
            if show_expr is None:
                return False

            return show_expr.expressionString().startswith(SPATIAL_FILTER)


def remove_mask_filter(layer):
    if not isinstance(layer, QgsVectorLayer):
        return False

    # check if a layer has already a mask filter enabled
    if layer.labeling() is None:
        return False

    settings = layer.labeling().settings()

    try:
        # simple labeling. new settings
        if (
            settings.dataDefinedProperties().hasProperty(
                QgsPalLayerSettings.Property.Show
            )
            and settings.dataDefinedProperties()
            .property(QgsPalLayerSettings.Property.Show)
            .expressionString()
            .startswith(SPATIAL_FILTER)
            and isinstance(layer.labeling(), QgsVectorLayerSimpleLabeling)
        ):
            settings = QgsPalLayerSettings(layer.labeling().settings())
            settings.dataDefinedProperties().setProperty(
                QgsPalLayerSettings.Property.Show, True
            )
            layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))

        # rules based labeling filter
        if isinstance(layer.labeling(), QgsRuleBasedLabeling):
            for rule in layer.labeling().rootRule().children():
                settings = rule.settings()
                if settings.dataDefinedProperties().hasProperty(
                    QgsPalLayerSettings.Property.Show
                ) and settings.dataDefinedProperties().property(
                    QgsPalLayerSettings.Property.Show
                ).expressionString().startswith(
                    SPATIAL_FILTER
                ):
                    settings.dataDefinedProperties().setProperty(
                        QgsPalLayerSettings.Property.Show, True
                    )
                    rule.setSettings(settings)

    except Exception as e:
        for m in e.args:
            QgsMessageLog.logMessage(m, "Extensions")


def add_mask_filter(layer):
    if not isinstance(layer, QgsVectorLayer):
        return False

    # check if a layer has already a mask filter enabled
    if layer.labeling() is None:
        return False

    try:
        expr = "%s(%d)" % (SPATIAL_FILTER, layer.crs().postgisSrid())
        prop = QgsProperty()
        prop.setExpressionString(expr)

        # simple labeling. new settings
        if isinstance(layer.labeling(), QgsVectorLayerSimpleLabeling):
            settings = QgsPalLayerSettings(layer.labeling().settings())
            settings.dataDefinedProperties().setProperty(
                QgsPalLayerSettings.Property.Show, prop
            )
            layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))

        # rules based labeling filter
        if isinstance(layer.labeling(), QgsRuleBasedLabeling):
            for rule in layer.labeling().rootRule().children():
                settings = rule.settings()
                settings.dataDefinedProperties().setProperty(
                    QgsPalLayerSettings.Property.Show, prop
                )
                rule.setSettings(settings)

    except Exception as e:
        for m in e.args:
            QgsMessageLog.logMessage(m, "Extensions")
