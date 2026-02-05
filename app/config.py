
from PySide6.QtCore import QSettings

# noinspection PyPep8Naming
import table_constants as C
import utilities as fcn

CONFIG_FILE = "config.ini"
DEFAULT_CSV_FILE = 'reminders.csv'   # Default filename

class AppConfig:
    def __init__(self):
        self.config_path = fcn.get_app_path(CONFIG_FILE)

        self.curr_csv_file = DEFAULT_CSV_FILE
        # USAGE: curr_csv_path = fcn.get_app_path(curr_csv_file)
        #          -- MUST be done AFTER QCoreApplication is created in main()

        # Default formats (to be overridden by user settings)
        self.date_display_format = "%d %b %Y"  # My 01 Han 202t format (used in testing). "%m/%d/%y" is 01/01/2026
        self.time_display_format = "%I:%M %p"   # for 12‑hr time. "%H:%M" for 24‑hr time.
        #window_geometry = "582x278+113+0"  # Sice & location of main window

        # TODO: Add font-size selection to config dialog
        self.cell_font_size = C.DEFAULT_CELL_FONT_SIZE
        self.hdr_font_size = self.cell_font_size - 1
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