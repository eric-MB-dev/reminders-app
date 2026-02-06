# ==========================================================
# Shared constants used by reminders_window and _table model
# USAGE:
# noinspection PyPep8Naming
# import app.table_constants as C
# ===========================================================

APP_NAME = "Reminders"

DEFAULT_CELL_FONT_SIZE = 11  # Header font set to one less in config

DEFAULT_GEOM_STR = "582x278, 450x0"  # Initial size (wxh) and position (x,y)
INITIAL_DISPLAY_DATA = ["!", "No entries yet. Add some!", "", "", "", ""]

CSV_COL_HEADERS =  ["Title", "Date", "Time", "Flag", "Notes", "Repeat"]
INITIAL_CSV_DATA = ["No entries yet. Add some!", "", "", "!", "", ""]

###################
# OLD DEFINITIONS #
###################
# Data Columns
# (Labels have leading spaces to simulate centering in fixed-width columns)
VM_COLUMN_LABELS  = ["! !", "Item", "Day", "Date", "Time", "Repeat", "Countdown"]
VM_COL_ALIGNMENTS = ["Ctr", "Left", "Ctr", "Ctr",   "Ctr",  "Ctr",  "Left" ]
VM_COL_MIN_WIDTHS = [  8,    200,     40,    90,      72,     66,     120 ]
VM_COL_MAX_WIDTHS = [  8,    360,     80,   180,     148,     66,     180 ]   # Allow for bold text
# Column Numbers:      0       1       2      3        4       5        6

# Button columns
UI_BUTTON_COLUMNS = 4
UI_BUTTON_LABELS      = ["Edit", "Alerts", "Next", " Del"]
UI_BUTTON_ALIGNMENTS = ["Ctr", "Ctr", "Ctr", " Ctr"]
UI_BUTTON_COL_WIDTHS = [35, 42, 35, 35]

NUM_DATA_COLS = len(VM_COLUMN_LABELS)
NUM_BUTTON_COLS = len(UI_BUTTON_LABELS)

ALL_COL_LABELS = VM_COLUMN_LABELS + UI_BUTTON_LABELS
ALL_COL_MIN_WIDTHS = VM_COL_MIN_WIDTHS + UI_BUTTON_COL_WIDTHS
ALL_COL_MAX_WIDTHS = VM_COL_MAX_WIDTHS + UI_BUTTON_COL_WIDTHS
ALL_COL_ALIGNMENTS = VM_COL_ALIGNMENTS + UI_BUTTON_ALIGNMENTS
COLUMN_INDICES = {
    "FLAG": 0,
    "DESCR": 1,
    "DAY": 2,
    "DATE": 3,
    "TIME": 4,
    "REPEAT": 5,
    "COUNTDOWN": 6,
    "EDIT": 7,
    "ALERT": 8,
    "NEXT": 9,
    "DEL": 10,
}
DESCR_COL = COLUMN_INDICES["DESCR"]
REPEAT_COL = COLUMN_INDICES["REPEAT"]
COUNTDOWN_COL = COLUMN_INDICES["COUNTDOWN"]

# Range of button columns (inclusive) *** MAY NOT BE NEEDED ***
IS_CRITICAL_FLAG = "!"
FLAG_COL = COLUMN_INDICES["FLAG"]
FIRST_BTN_COL = EDIT_COL = COLUMN_INDICES["EDIT"]
ALERT_COL = COLUMN_INDICES["ALERT"]
NEXT_COL  = COLUMN_INDICES["NEXT"]
LAST_COL  = DEL_COL = COLUMN_INDICES["DEL"]
UI_BUTTON_RANGE = range(FIRST_BTN_COL, LAST_COL + 1)

############################
###  COLUMN DEFINITIONS  ###
############################
from dataclasses import dataclass
from typing import List

@dataclass
class ColDef:
    id: str  # Internal ID (e.g., "DESCR")
    label: str  # Header text
    align: str  # "Left", "Ctr", "Right"
    min_w: int
    max_w: int
    visible: bool = True  # Default to visible

# --- 1. Master Definitions (The "Kitchen Sink") ---
_MASTER_COLS = [
    # Data Columns
    ColDef("FLAG", "! !", "Ctr", 8, 8),
    ColDef("DESCR", "Item", "Left", 200, 360),
    ColDef("DAY", "Day", "Ctr", 40, 80),
    ColDef("DATE", "Date", "Ctr", 90, 180),
    ColDef("TIME", "Time", "Ctr", 72, 148),
    # Hide repeat column to shrink the window without breaking logic
    ColDef("REPEAT", "Repeat", "Ctr", 66, 66), #, visible=False),
    ColDef("COUNTDOWN", "Count", "Left", 120, 180),

    # Action Columns
    ColDef("EDIT", "Edit", "Ctr", 30, 30),
    ColDef("ALERT", "Alerts", "Ctr", 42, 42),
    ColDef("NEXT", "Nxt", "Ctr",35, 35),
    ColDef("DEL", "Del", "Ctr", 35, 35),
]

# --- 2. The Active Set (The "Source of Truth" for the View) ---
# This list only contains columns where visible=True
ALL_COLS: List[ColDef] = [c for c in _MASTER_COLS if c.visible]

# --- 3. Dynamic Index Mapping ---
# This automatically creates C.DESCR_IDX, C.TIME_IDX, etc.
# based on their POSITION in the active ALL_COLS list.
for i, col in enumerate(ALL_COLS):
    globals()[f"{col.id}_IDX"] = i

# --- 4. Convenience Logic ---
def get_align(idx: int):
    """Returns Qt alignment flag based on our string definitions."""
    from PyQt6.QtCore import Qt
    align_str = ALL_COLS[idx].align
    if align_str == "Left": return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    if align_str == "Ctr":  return Qt.AlignmentFlag.AlignCenter
    return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
