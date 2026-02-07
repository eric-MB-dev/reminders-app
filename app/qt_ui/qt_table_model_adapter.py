# reminder_table_model.py
#
# RemindersTableModel defines the final table structure for Qt by combining
# domain columns from the ViewModel with UI-only button columns. It owns all
# column labels, column indices, and structural constants, and provides header
# text, column counts, and cell values to the view. This layer is the sole
# authority on the table’s shape and is the bridge between domain-model data & Qt.

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont, QIcon # QFontMetrics,

from app.model.reminders_model import RemindersModel
from app.config import config

# noinspection PyPep8Naming
import table_constants as C

# Catch undefined elements that PyCharm SHOULD catch, but doesn't
# and that create internal Qt exceptions that kill the app
import traceback
def _qt_guard(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            print("\n=== Qt swallowed an exception ===")
            traceback.print_exc()
            print("=== End swallowed exception ===\n")
            raise
    return wrapper

class QtTableModelAdapter(QAbstractTableModel):
    """
    Wrapper on my view_model class for Qt to talk to.
    """
    def __init__(self, domain_model:RemindersModel):
        super().__init__()
        self.reminders_model = domain_model

        # Entry data
        self._data_rows = []
        self._is_critical = []
        self._has_note = [ ]
        
        # Load rows from the domain model to derive UI state
        self.load_rows()
        self.reminders_model._fully_initialized = True

    def on_font_changed(self):
        # Trigger a call to headerData() for FontRole/DisplayRole
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, len(C.ALL_COLS) - 1)

    def is_critical(self, row):
        return self._is_critical[row]

    def has_note(self, row):
        return self._has_note[row]

    @_qt_guard
    def rowCount(self, parent=QModelIndex()):
        return len(self.reminders_model.display_rows())
    
    #@_qt_guard
    def columnCount(self, parent=QModelIndex()):
        return len(C.ALL_COL_LABELS)
    
    def load_rows(self):
        self._data_rows = self.reminders_model.display_rows()
        self._is_critical = [
            (row[C.FLAG_COL] == C.IS_CRITICAL_FLAG) for row in self._data_rows
        ]
        self._has_note = [
            ("\n" in row[C.DESCR_COL]) for row in self._data_rows
        ]

    @_qt_guard
    def v_alignment_for(self, row, col):
        return (
            Qt.AlignmentFlag.AlignTop
            if self.has_note(row)
            else Qt.AlignmentFlag.AlignVCenter
        )

    @_qt_guard
    def h_alignment_for(self, row, col):
        return (
            Qt.AlignmentFlag.AlignHCenter
            if C.ALL_COL_ALIGNMENTS[col] == "Ctr"
            else Qt.AlignmentFlag.AlignLeft
        )

    @_qt_guard
    def data(self, index, role):
        row = index.row()
        col = index.column()
        
        # --- Data columns ---
        if col < C.NUM_DATA_COLS:
            
            # Bold entire row if critical
            if role == Qt.FontRole and self._is_critical[row]:
                f = QFont()
                f.setBold(True)
                return f
            
            # Display raw value from cached rows
            if role == Qt.DisplayRole:
                row_data = self._data_rows[row]
                value = row_data[col]
                #print(f"ROW DATA: row={index.row()}, col={index.column()}, value={value!r}")
                return value
            
            if role == Qt.TextAlignmentRole:
                vert_align = self.v_alignment_for(row, col)
                horiz_align = self.h_alignment_for(row, col)
                return vert_align | horiz_align

            return None
        
        # --- Button columns ---
        if role == Qt.DisplayRole:
            #print(f"BUTTON DATA: row={index.row()}, col={index.column()}, value=Empty String")
            return ""  # placeholder for delegates
        
        if role == Qt.DecorationRole:
            return self._icon_for_button_column(col)
        
        return None
    
    @_qt_guard
    def _icon_for_button_column(self, col):
        if col == C.DEL_COL:
            return QIcon(":/icons/delete.png")
        if col == C.EDIT_COL:
            return QIcon(":/icons/edit.png")
        if col == C.ALERT_COL:
            return QIcon(":/icons/alert.png")
        if col == C.NEXT_COL:
            return QIcon(":/icons/next.png")
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):  # type: ignore[attr-defined]
        # Only care about horizontal headers
        if orientation != Qt.Horizontal:  # type: ignore[attr-defined]
            return None
        
        # Qt sometimes asks for out-of-range sections; Prevent crash here
        if section < 0 or section >= len(C.ALL_COL_LABELS):
            return None
        
        if role == Qt.DisplayRole:  # type: ignore[attr-defined]
            return C.ALL_COLS[section].label
            #return C.ALL_COL_LABELS[section]

        if role == Qt.ItemDataRole.FontRole:
            font = QFont()
            font.setPointSize(config.hdr_font_pt_size)
            font.setBold(True)
            return font

        if role == Qt.TextAlignmentRole:  # type: ignore[attr-defined]
            if C.ALL_COL_ALIGNMENTS[section] == "Ctr":
                return Qt.AlignmentFlag.AlignCenter
            else:
                return Qt.AlignmentFlag.AlignLeft
            
        return super().headerData(section, orientation, role)

    def toggle_flag(self, row):
        # Flip the UI state
        self._is_critical[row] = not self._is_critical[row]
    
        # Update the data model so persistence stays correct
        new_value = "!" if self._is_critical[row] else ""
        self.reminders_model.set_flag_value(row, new_value)
        
        self.load_rows()  # refresh cached rows & _is_critical
    
        # Notify the view that the entire row's font changed
        left = self.index(row, 0)
        right = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(left, right, [Qt.FontRole, Qt.DisplayRole, Qt.EditRole])
            # The "EditRole" signal tells the cell to repaint immediately

#endCLASS