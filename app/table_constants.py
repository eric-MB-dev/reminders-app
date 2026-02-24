# ==========================================================
# Shared constants used by reminders_window and _table model
# USAGE:
# noinspection PyPep8Naming
# import app.table_constants as C
# ===========================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
#from PySide6.QtWidgets import QApplication, QStyle

from dataclasses import dataclass
from typing import List, Optional

APP_NAME = "Reminder System"

ALERT_SCHEDULE = ({30,'days'}, {14,'days'}, {7,'days'}, {3,'days'}, {1,'days'},
                  {4, 'hrs'}, {2, 'hrs'}, {1, 'hrs'}, {30, 'min'}, {15, 'min'}, {10, 'min'}, {5, 'min'})

DEFAULT_CELL_FONT_SIZE = 10  # Header font set to one less in config

DEFAULT_GEOM_STR = "582x278, 450x0"  # Initial size (wxh) and position (x,y)
INITIAL_DISPLAY_DATA = ["!", "No entries yet. Add some!", "", "", "", ""]

CSV_COL_HEADERS =  ["Title", "Date", "Time", "Flag", "Notes", "Repeat"]
INITIAL_CSV_DATA = ["No entries yet. Add some!", "", "", "!", "", ""]

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
COLUMN_SCHEMA = [
    # Data Columns
    #      ID       Label        Align   Min   Max   {Visible}
    ColDef("FLAG",  "!",         "Ctr",    8,   8),
    ColDef("DESCR", "Item",      "Left", 200, 360),
    ColDef("DAY",   "Day",       "Ctr",   40,  40),
    ColDef("DATE",  "Date",      "Ctr",  100, 100),
    ColDef("TIME",  "Time",      "Ctr",  100, 100),
    # Hide repeat column to shrink the window without breaking logic
    ColDef("REPEATS", "Repeats",  "Ctr",   66,  66), #, visible=False),
    ColDef("COUNTDOWN", "Countdown", "Left", 116, 116),

    # Action-button Columns
    ColDef("EDIT",   "Edit",     "Ctr",  34,  34, icon="fa5s.pencil-alt"),
    ColDef("ALERTS", "Alrt",     "Ctr",  34,  34, icon="mdi.bell-off"),
    ColDef("NEXT",   "Nxt",      "Ctr",  34,  34, icon="ei.repeat"),
    ColDef("DEL",    "Del",      "Ctr",  34,  34, icon="fa5s.trash"),
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
    "EDIT":   {"icon": "fa5s.pencil-alt", "color": "forestgreen"},           # "#FFD700"}, # Gold
    "ALERTS": {"icon": "fa5s.bell",       "off_icon": "mdi.bell-off", "color": "#FFBF00"}, # Amber
    "NEXT":   {"icon": "ei.repeat",       "color": "dodgerblue"},
    "DEL":    {"icon": "fa5s.trash",      "color": "#8b0000"}, # Deep Red
}

# Map horizontal-alignment-designation to UI marker
ALIGN_MAP = {
    "Ctr":  Qt.AlignmentFlag.AlignHCenter,
    "Left": Qt.AlignmentFlag.AlignLeft,
    "Right": Qt.AlignmentFlag.AlignRight
}

# Map UI column names to ReminderItem attributes
UI_COL_MAP = {
    "DAY": "day_of_week",
    "ALERTS": "alerts_enabled",
}

# --- The Active Set (The "Source of Truth" for the View) ---
# This list only contains columns where visible=True
ALL_COLS: List[ColDef] = [c for c in COLUMN_SCHEMA if c.visible]

# --- Dynamic Index Mapping ---
# This automatically creates C.DESCR_IDX, C.TIME_IDX, etc.
# based on their POSITION in the active ALL_COLS list.
for i, col in enumerate(ALL_COLS):
    globals()[f"{col.id}_IDX"] = i

# --- The Data-Columns Boundary ---
# Find the index of the first button to know where the data ends
# (Assumes "EDIT" is your first button column)
FIRST_BTN_IDX = EDIT_IDX

# CSV storage flags
IS_CRITICAL_FLAG = "!"
ALERTS_ENABLED_FLAG = "A"

# --- Custom Data Roles ---
# ("User Roles" start at 32 in Qt. Each additional "role" is one more.
ALERTS_ROLE = Qt.ItemDataRole.UserRole      # Boolean: Are Alerts enabled?
REPEATS_ROLE = Qt.ItemDataRole.UserRole + 1  # Boolean: Does it repeat?

# -----------------------------
# File names
# -----------------------------
INI_FILENAME = "reminders.ini"
DEFAULT_CSV_FILENAME = "reminders.csv"

# -----------------------------
# Configuration options
# -----------------------------

COMMON_DATE_FORMATS = [
    ("%m/%d/%y", "12/31/25"),
    ("%Y-%m-%d", "2025-12-31"),
    ("%b %d, %Y", "Dec 31, 2025"),
    ("%d %b %Y", "31 Dec 2025"),
]

COMMON_TIME_FORMATS = [
    ("%I:%M %p", "03:45 PM"),
    ("%H:%M", "15:45"),
    ("%I:%M:%S %p", "03:45:12 PM"),
    ("%H:%M:%S", "15:45:12"),
]
