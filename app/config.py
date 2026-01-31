from dataclasses import dataclass

from PySide6.QtCore import QSettings

# noinspection PyPep8Naming
import table_constants as C
import utilities as fcn

CONFIG_FILE = "config.ini"
DEFAULT_CSV_FILE = 'reminders.csv'   # Default filename

curr_csv_file = DEFAULT_CSV_FILE
# USAGE: curr_csv_path = fcn.get_app_path(curr_csv_file)
#          -- MUST be done AFTER QCoreApplication is created in main()

# Default formats (to be overridden by user settings)
date_display_format = "%d %b %Y"  # My 01 Han 202t format (used in testing). "%m/%d/%y" is 01/01/2026
time_display_format = "%I:%M %p"   # for 12‑hr time. "%H:%M" for 24‑hr time.
#window_geometry = "582x278+113+0"  # Sice & location of main window

# TODO: Add font-size selection to config dialog
cell_font_size = C.DEFAULT_CELL_FONT_SIZE
hdr_font_size = cell_font_size - 1
'''
@dataclass
class WindowPlacement:
    x: int      # Left Edge
    y: int      # Top edge
    w: int      # Width
    h: int      # Height
 '''
geom_str = C.DEFAULT_GEOM_STR

def encode_geometry(w, h, x, y):
    """width, height x(horiz) & y(vert) position of upper left corner"""
    assert all(isinstance(v, int) for v in (w, h, x, y)), \
        f"Geometry values must be ints, got: w={w}, h={h}, x={x}, y={y}"
    
    global geom_str
    #window_placement = WindowPlacement(w, h, x, y)
    geom_str = f"{w}x{h}, {x}x{y}"
    
def get_window_geom():
    return decode_geom(geom_str)

def decode_geom(s: str):
    try:
        size_part, pos_part = s.split(",")
        w_str, h_str = size_part.strip().split("x")
        x_str, y_str = pos_part.strip().split("x")
        return int(w_str), int(h_str), int(x_str), int(y_str)
    except ValueError:
        return None

def load_config():
    global date_display_format, time_display_format, geom_str

    config_path = fcn.get_app_path(CONFIG_FILE)
    settings = QSettings(str(config_path), QSettings.IniFormat)

    # New value           Config file path                      # Fallback value
    date_display_format = settings.value("display/date_format", date_display_format)
    time_display_format = settings.value("display/time_format", time_display_format)
    geom_str = settings.value("window/geometry", geom_str)
    return

def save_config():
    global date_display_format, time_display_format, geom_str

    config_path = fcn.get_app_path(CONFIG_FILE)
    settings = QSettings(str(config_path), QSettings.IniFormat)

    # Display settings
    settings.setValue("display/date_format", date_display_format)
    settings.setValue("display/time_format", time_display_format)

    # Window geometry
    settings.setValue("window/geometry", geom_str)
