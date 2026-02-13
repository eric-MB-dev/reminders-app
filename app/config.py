
from PySide6.QtCore import QSettings, QObject, Signal

# noinspection PyPep8Naming
import table_constants as C
import utilities as fcn

CONFIG_FILE = "config.ini"
DEFAULT_CSV_FILE = 'reminders.csv'   # Default filename

class AppConfig(QObject):
    """
    Singleton configuration class.
    USAGE:
    from app.config import config
    """
    # Class-level signal definition
    font_changed = Signal()

    def __init__(self):
        # Required for QObject signals to work
        super().__init__()

        self.config_path = fcn.get_app_file_path(CONFIG_FILE)

        self.curr_csv_file = DEFAULT_CSV_FILE
        # USAGE: curr_csv_path = fcn.get_app_path(curr_csv_file)
        #          -- MUST be done AFTER QCoreApplication is created in main()

        # Default formats (to be overridden by user settings)
        self.date_display_format = "%d %b %Y"  # My 01 Han 202t format (used in testing). "%m/%d/%y" is 01/01/2026
        self.time_display_format = "%I:%M %p"   # for 12‑hr time. "%H:%M" for 24‑hr time.

        self._cell_font_pt_size = C.DEFAULT_CELL_FONT_SIZE
        self._hdr_font_pt_size = C.DEFAULT_CELL_FONT_SIZE - 1

        '''
        from dataclasses import dataclass
        @dataclass
        class WindowPlacement:
            x: int      # Left Edge
            y: int      # Top edge
            w: int      # Width
            h: int      # Height
         '''
        self._geom_str = C.DEFAULT_GEOM_STR

    @property
    def cell_font_pt_size(self):
        return self._cell_font_pt_size

    @cell_font_pt_size.setter
    def cell_font_pt_size(self, value):
        if self._cell_font_pt_size != value:
            self._cell_font_pt_size = value
            self._hdr_font_pt_size = self._cell_font_pt_size - 1
            self.font_changed.emit()

    @property
    def hdr_font_pt_size(self):
        return self._hdr_font_pt_size

    @property
    def window_geom(self):
        return self.decode_geom(self._geom_str)

    @window_geom.setter
    def window_geom(self, values):
        """Property Setter: Expects a tuple (w, h, x, y)"""
        self.encode_geometry(values)

    def encode_geometry(self, values):
        """width, height x(horiz) & y(vert) position of upper left corner"""
        w, h, x, y = values
        assert all(isinstance(v, int) for v in (w, h, x, y)), \
            f"Geometry values must be ints, got: w={w}, h={h}, x={x}, y={y}"
        self._geom_str = f"{w}x{h}, {x}x{y}"

    def decode_geom(self, s: str):
        try:
            size_part, pos_part = s.split(",")
            w_str, h_str = size_part.strip().split("x")
            x_str, y_str = pos_part.strip().split("x")
            return int(w_str), int(h_str), int(x_str), int(y_str)
        except ValueError:
            return None

    def load_config(self):
        settings = QSettings(str(self.config_path), QSettings.IniFormat)

        # New value                # Config file path                    # Fallback value
        self.date_display_format = settings.value("display/date_format", self.date_display_format)
        self.time_display_format = settings.value("display/time_format", self.time_display_format)
        self._geom_str = settings.value("window/geometry", self._geom_str)
        return

    def save_config(self):
        settings = QSettings(str(self.config_path), QSettings.IniFormat)

        # Display settings
        settings.setValue("display/date_format", self.date_display_format)
        settings.setValue("display/time_format", self.time_display_format)

        # Window geometry
        settings.setValue("window/geometry", self._geom_str)

# Create one instance of the class named 'config', so all previous importscalls
# of and to this script require no change!
config = AppConfig()