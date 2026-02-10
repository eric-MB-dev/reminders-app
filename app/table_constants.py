# ==========================================================
# Shared constants used by reminders_window and _table model
# USAGE:
# noinspection PyPep8Naming
# import app.table_constants as C
# ===========================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QStyle

from dataclasses import dataclass
from typing import List, Optional

APP_NAME = "Reminder System"

DEFAULT_CELL_FONT_SIZE = 11  # Header font set to one less in config

DEFAULT_GEOM_STR = "582x278, 450x0"  # Initial size (wxh) and position (x,y)
INITIAL_DISPLAY_DATA = ["!", "No entries yet. Add some!", "", "", "", ""]

CSV_COL_HEADERS =  ["Title", "Date", "Time", "Flag", "Notes", "Repeat"]
INITIAL_CSV_DATA = ["No entries yet. Add some!", "", "", "!", "", ""]
"""
def get_btn_icon(col_idx):
    C.DEL_COL: QIcon(":/icons/delete.png")
    C.EDIT_COL: QIcon(":/icons/edit.png")
    C.ALERT_COL: QIcon(":/icons/alert.png")
    C.NEXT_COL: QIcon(":/icons/next.png")
    
    # Fetch the icon using the global app style
    style = QApplication.style()
    if style:
        # We verified this specific Enum path works for your setup
        return app_style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
    return QIcon()
"""

############################
###  COLUMN DEFINITIONS  ###
############################

@dataclass
class ColDef:
    id: str           # Internal ID (e.g., "DESCR")
    label: str        # Header text
    align: str        # "Left", "Ctr", etc.
    min_w: int
    max_w: int
    icon: str = None      # Icon ID for buttons
    visible: bool = True  # Default to visible

# --- Schema Definitions (all display columns) ---
# USABE:  col_def = C.ALL_COLS[col#]
_COLUMN_SCHEMA = [
    # Data Columns
    #      ID       Label        Align   Min   Max
    ColDef("FLAG",  "!",         "Ctr",    8,   8),
    ColDef("DESCR", "Item",      "Left", 200, 360),
    ColDef("DAY",   "Day",       "Ctr",   40,  40),
    ColDef("DATE",  "Date",      "Ctr",   90,  90),
    ColDef("TIME",  "Time",      "Ctr",   72,  72),
    # Hide repeat column to shrink the window without breaking logic
    ColDef("REPEAT",    "Repeat",    "Ctr",   66,  66), #, visible=False),
    ColDef("COUNTDOWN", "Countdown", "Left", 120, 120),

    # Action-button Columns
    ColDef("EDIT",  "Edit",      "Ctr",   35,  35, icon="fa5s.pencil-alt"),
    ColDef("ALERT", "Alerts",    "Ctr",   42,  42, icon="mdi.bell-off"),
    ColDef("NEXT",  "Next",      "Ctr",   40,  40, icon="ei.repeat"),
    ColDef("DEL",   "Del",       "Ctr",   35,  35, icon="fa5s.trash"),
]
"""
Candidate buttons
    [ ] fa5s.trash
        qta.icon('fa5s.trash', scale_factor=1.2) to fill more button space without making button larger
    [ ] Other icons:
        fa5s.pencil-alt (std), fa5s.pencil, msc.pencil, n.pencil-fill
        fa5s.bell, fa6s.bell / mdi.bell-off, mdi.bell-off-outline, mdi.mdi6.bell-off, mdi6.bell-off-outline
        ei.repeat, ei.repeat-alt
"""
ICON_MAP = {
    "EDIT":  {"icon": "fa5s.pencil-alt", "color": "forestgreen"},           # "#FFD700"}, # Gold
    "ALERT": {"icon": "fa5s.bell",       "off_icon": "mdi.bell-off", "color": "#FFBF00"}, # Amber
    "NEXT":  {"icon": "ei.repeat",       "color": "dodgerblue"},
    "DEL":   {"icon": "fa5s.trash",      "color": "#8b0000"}, # Deep Red
}

# Map alignment-designation to UI marker
ALIGN_MAP = {
    "Ctr":  Qt.AlignmentFlag.AlignCenter,
    "Left": Qt.AlignmentFlag.AlignLeft,
    "Right": Qt.AlignmentFlag.AlignRight
}

# Domain constants
IS_CRITICAL_FLAG = "!"

# --- The Active Set (The "Source of Truth" for the View) ---
# This list only contains columns where visible=True
ALL_COLS: List[ColDef] = [c for c in _COLUMN_SCHEMA if c.visible]

# --- Dynamic Index Mapping ---
# This automatically creates C.DESCR_IDX, C.TIME_IDX, etc.
# based on their POSITION in the active ALL_COLS list.
for i, col in enumerate(ALL_COLS):
    globals()[f"{col.id}_IDX"] = i

# --- The Data-Columns Boundary ---
# Find the index of the first button to know where the data ends
# (Assumes "EDIT" is your first button column)
FIRST_BTN_IDX = EDIT_IDX

'''
# --- 4. Convenience Logic ---
def get_align(idx: int):
    """Returns Qt alignment flag based on our string definitions."""
    from PyQt6.QtCore import Qt
    align_str = ALL_COLS[idx].align
    if align_str == "Left": return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    if align_str == "Ctr":  return Qt.AlignmentFlag.AlignCenter
    return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
'''

# Cache of action-button icons so they can be directly accessed,
# rather than re-loaded 60 times a second when paint() methods run.
_ICON_CACHE = {}

def get_btn_icon(col_id: str) -> QIcon:
    if col_id not in _ICON_CACHE:
        # Map the Schema ID to the resource path
        path_map = {
            "EDIT":  ":/icons/edit.png",
            "ALERT": ":/icons/alert.png",
            "NEXT":  ":/icons/next.png",
            "DEL":   ":/icons/delete.png",
        }
        path = path_map.get(col_id)
        _ICON_CACHE[col_id] = QIcon(path) if path else QIcon()
    return _ICON_CACHE[col_id]