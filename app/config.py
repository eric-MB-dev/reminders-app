from configobj import ConfigObj
import os
from dataclasses import dataclass

import table_constants as C

#TODO: When and if config grows larger / more complicated:
#  [ ] - models/config.py → the Config object
#  [ ] - storage/config_storage.py → load/save
#  [X] - wx_ui/config_dialog.py → the dialog.

CONFIG_FILE = f"../App.ini"
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))     # Current script location
CONFIG_PATH = os.path.join(CONFIG_DIR, CONFIG_FILE)

BASE_DIR = os.path.dirname(CONFIG_DIR)
DEFAULT_CSV_FILE = 'reminders.csv'   # Default filename & location (script-dir/data)
DEFAULT_CSV_DIR = os.path.join(BASE_DIR, "data")
DEFAULT_CSV_PATH = os.path.join(DEFAULT_CSV_DIR, DEFAULT_CSV_FILE)

curr_csv_file = DEFAULT_CSV_FILE
curr_csv_dir = DEFAULT_CSV_DIR
curr_csv_path = DEFAULT_CSV_PATH

# Default formats (to be overridden by user settings)
date_display_format = "%d %b %Y"  # My 01 Han 202t format (used in testing). "%m/%d/%y" is 01/01/2026
time_display_format = "%I:%M %p"   # for 12‑hr time. "%H:%M" for 24‑hr time.
#window_geometry = "582x278+113+0"  # Sice & location of main window

# TODO: Add font-size selection to config dialog
cell_font_size = C.DEFAULT_CELL_FONT_SIZE
hdr_font_size = cell_font_size - 1

@dataclass
class WindowPlacement:
    x: int      # Left Edge
    y: int      # Top edge
    w: int      # Width
    h: int      # Height
    
#window_placement: WindowPlacement | None = None
#window_placement = WindowPlacement(256, 200, 1180, 0)
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

    if os.path.exists(CONFIG_FILE):
        cfg = ConfigObj(CONFIG_FILE)
        if "display" in cfg:                         # Defaults if not found--v
            date_display_format = cfg["display"].get("date_format", date_display_format)
            time_display_format = cfg["display"].get("time_format", time_display_format)
            geom_str = cfg["window"].get("geometry", geom_str)
                
def save_config():
    global date_display_format, time_display_format, window_placement
    #print(f"On entry: {window_geometry}")
    cfg = ConfigObj(CONFIG_FILE)
    if "display" not in cfg:
        cfg["display"] = {}
    if "window" not in cfg:
        cfg["window"] = {}
    
    cfg["display"]["date_format"] = date_display_format
    cfg["display"]["time_format"] = time_display_format
    cfg["window"]["geometry"] = geom_str

    # Write and verify
    try:
        cfg.write()
        #print(f"[save_config] Written to {os.path.abspath(CONFIG_FILE)}")
    except Exception as e:
        print(f"[save_config] Write failed: {e}")
