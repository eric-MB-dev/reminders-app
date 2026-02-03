# ==========================================================
# Shared constants used by reminders_window and _table model
# USAGE:
# noinspection PyPep8Naming
# import app.table_constants as C
#
# Reference:
#   C.COLUMN_LABELS
#   C.COLUMN_WIDTHS
#   C.DESCR_COL
#   C.EDIT_COL
#   C.ALL_COLUMNS
# ===========================================================

APP_NAME = "Reminders"
# Data Columns
# (Labels have leading spaces to simulate centering in fixed-width columns)
VM_COLUMN_LABELS  = ["! !", "Item", "Day", "Date", "Time", "Repeat", "Countdown"]
VM_COL_ALIGNMENTS = ["Ctr", "Left", "Ctr", "Ctr",   "Ctr",  "Ctr",  "Left" ]
VM_COL_MIN_WIDTHS = [  8,    200,     40,    90,      72,     90,     120 ]
VM_COL_MAX_WIDTHS = [  8,    360,     80,   180,     148,     90,     180 ]   # Allow for bold text
# Column Numbers:      0       1       2      3        4       5        6
# Data columns:
#DESCR_COL = 0; DAY_COL = 1; DATE_COL = 2; TIME_COL = 3; COUNTDOWN_COL = 4

#MIN_DESCR_WIDTH = 160
#MAX_DESCR_WIDTH = 360

# Button columns
UI_BUTTON_COLUMNS = 4
UI_BUTTON_LABELS      = ["Edit", "Alerts", "Next", " Del"]
UI_BUTTON_ALIGNMENTS = ["Ctr", "Ctr", "Ctr", " Ctr"]
UI_BUTTON_COL_WIDTHS = [35, 42, 35, 35]

NUM_DATA_COLS = len(VM_COLUMN_LABELS)
NUM_BUTTON_COLS = len(UI_BUTTON_LABELS)

#EDIT_COL = 5; ALERT_COL = 6; NEXT_COL = 7; DEL_COL = 8

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

# Derived values *** MAY NOT BE NEEDED ***
#INIT_DESCR_WIDTH = VM_COL_MIN_WIDTHS[DESCR_COL]
#TOTAL_OTHER_COLS = sum(VM_COL_MIN_WIDTHS) - INIT_DESCR_WIDTH

DEFAULT_CELL_FONT_SIZE = 11  # Header font set to one less in config

DEFAULT_GEOM_STR = "582x278, 450x0"  # Initial size (wxh) and position (x,y)
INITIAL_DISPLAY_DATA = ["!", "No entries yet. Add some!", "", "", "", ""]

CSV_COL_HEADERS =  ["Title", "Date", "Time", "Flag", "Notes", "Repeat"]
INITIAL_CSV_DATA = ["No entries yet. Add some!", "", "", "!", "", ""]
