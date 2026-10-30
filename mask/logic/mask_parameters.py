import base64
import json

from qgis.core import QgsGeometry, QgsMessageLog, QgsProject


class MaskParameters:
    SERIAL_VERSION = 2

    def __init__(self):
        self.do_buffer = False
        self.buffer_units = 1
        self.buffer_segments = 5
        self.do_simplify = True
        self.simplify_tolerance = 1.0
        self.do_save_as = False
        self.file_path = None
        self.file_format = None
        self.style = None
        self.polygon_mask_method = 2
        self.line_mask_method = 0
        self.limited_layers_obsolete = []
        self.orig_geometry = []
        self.geometry = None
        self.do_atlas_interaction = True

    def forSettings(self):
        settings = MaskParameters()
        settings.do_buffer = self.do_buffer
        settings.buffer_units = self.buffer_units
        settings.buffer_segments = self.buffer_segments
        settings.do_simplify = self.do_simplify
        settings.simplify_tolerance = self.simplify_tolerance
        settings.do_save_as = self.do_save_as
        settings.file_path = self.file_path
        settings.file_format = self.file_format
        settings.style = self.style
        settings.polygon_mask_method = self.polygon_mask_method
        settings.line_mask_method = self.line_mask_method
        settings.limited_layers_obsolete = self.limited_layers_obsolete
        settings.orig_geometry = []
        settings.geometry = None
        settings.do_atlas_interaction = self.do_atlas_interaction
        return settings

    @staticmethod
    def _style_to_serializable(style):
        if style is None:
            return None
        if isinstance(style, str):
            return style
        if isinstance(style, (bytes, bytearray)):
            return style.decode("utf-8", errors="replace")
        if hasattr(style, "toUtf8"):
            return bytes(style.toUtf8()).decode("utf-8", errors="replace")
        return str(style)

    @staticmethod
    def _json_default(value):
        # S'assure que les objets non-JSONables sont convertibles
        if value is None or isinstance(value, (str, int, float, bool, list, dict)):
            return value
        if hasattr(value, "toUtf8"):
            return bytes(value.toUtf8()).decode("utf-8", errors="replace")
        return str(value)

    @staticmethod
    def _geom_to_b64(geom):
        if geom is None:
            return None
        return base64.b64encode(geom.asWkb()).decode("ascii")

    @staticmethod
    def _geom_from_b64(data):
        if data is None:
            return None
        geom = QgsGeometry()
        geom.fromWkb(base64.b64decode(data))
        return geom

    def serialize(self, with_style=True):
        payload = {
            "version": self.SERIAL_VERSION,
            "do_buffer": self.do_buffer,
            "buffer_units": self.buffer_units,
            "buffer_segments": self.buffer_segments,
            "do_simplify": self.do_simplify,
            "simplify_tolerance": self.simplify_tolerance,
            "do_save_as": self.do_save_as,
            "file_path": self.file_path,
            "file_format": self.file_format,
            "limited_layers_obsolete": self.limited_layers_obsolete,
            "style": self._style_to_serializable(self.style) if with_style else None,
            "polygon_mask_method": self.polygon_mask_method,
            "line_mask_method": self.line_mask_method,
            "orig_geometry": [self._geom_to_b64(g) for g in (self.orig_geometry or [])],
            "geometry": self._geom_to_b64(self.geometry),
            "do_atlas_interaction": self.do_atlas_interaction,
        }

        return json.dumps(
            payload,
            default=self._json_default,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

    def _apply_payload(self, payload):
        QgsMessageLog.logMessage("_apply_payload", "Extensions")

        self.do_buffer = payload.get("do_buffer", False)
        self.buffer_units = payload.get("buffer_units", 1)
        self.buffer_segments = payload.get("buffer_segments", 5)
        self.do_simplify = payload.get("do_simplify", True)
        self.simplify_tolerance = payload.get("simplify_tolerance", 1.0)
        self.do_save_as = payload.get("do_save_as", False)
        self.file_path = payload.get("file_path")
        self.file_format = payload.get("file_format")
        self.limited_layers_obsolete = payload.get("limited_layers_obsolete", [])
        self.style = payload.get("style")
        self.polygon_mask_method = payload.get("polygon_mask_method", 2)
        self.line_mask_method = payload.get("line_mask_method", 0)
        self.do_atlas_interaction = payload.get("do_atlas_interaction", True)

        self.orig_geometry = []
        for g in payload.get("orig_geometry", []):
            geom = self._geom_from_b64(g)
            if geom is not None:
                self.orig_geometry.append(geom)

        self.geometry = self._geom_from_b64(payload.get("geometry"))

    def unserialize(self, st):
        if st is None:
            raise ValueError("No parameters to unserialize")

        if isinstance(st, str):
            st = st.encode("utf-8")
        elif hasattr(st, "toByteArray"):
            st = st.toByteArray()
        elif not isinstance(st, (bytes, bytearray)):
            st = str(st).encode("utf-8")

        try:
            payload = json.loads(bytes(st).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("JSON payload invalid")

            if payload.get("version") is None:
                raise ValueError("Incompatible parameters")

            self._apply_payload(payload)

        except Exception as e:
            QgsMessageLog.logMessage(f"Mask error when unserialize - {e}", "Extensions")
            raise e

    def have_same_layer_options(self, other):
        """Returns true if the other parameters have the same layer options
        (file path, file format) than self
        """
        if not self.do_save_as:
            return not other.do_save_as
        else:
            if not other.do_save_as:
                return False
            else:
                return (
                    self.file_path == other.file_path
                    and self.file_format == other.file_format
                )

    def save_to_project(self):
        serialized = self.serialize()
        encoded = base64.b64encode(serialized).decode("ascii")

        QgsProject.instance().writeEntry("Mask", "parameters", encoded)
        return True

    def load_from_project(self):
        st, ok = QgsProject.instance().readEntry("Mask", "parameters")
        if not ok or st == "":
            return False

        self.unserialize(base64.b64decode(st))
