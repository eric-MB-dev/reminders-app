# reminder_table_model.py
#
# RemindersTableModel defines the final table structure for Qt by combining
# domain columns from the ViewModel with UI-only button columns. It owns all
# column labels, column indices, and structural constants, and provides header
# text, column counts, and cell values to the view. This layer is the sole
# authority on the table’s shape and is the bridge between domain-model data & Qt.

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont #, QIcon, QFontMetrics

from app.model.reminders_model import RemindersModel
from app.model.reminder_item import ReminderItem
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
            print("\n" + "!" * 40)
            print(f"CRASH IN: {fn.__name__}")
            traceback.print_exc()
            print("!" * 40 + "\n")
            # DO NOT RAISE. Return a safe value for Qt to digest.
            return None
    return wrapper

def v_alignment(reminder: ReminderItem):
    #if getattr(reminder, "has_notes", False):
    if reminder.has_notes:
        return Qt.AlignmentFlag.AlignTop
    return Qt.AlignmentFlag.AlignVCenter

def h_alignment(col_idx):
    col_def = C.ALL_COLS[col_idx]
    return C.ALIGN_MAP[col_def.align]

class ModelAdapter(QAbstractTableModel):
    """
    Wrapper on my view_model class for Qt to talk to.
    """
    def __init__(self, domain_model:RemindersModel):
        super().__init__()
        self._reminders_model = domain_model
        self._reminders_model._fully_initialized = True

        # Cache the font we'll need many times later
        self._bold_font = QFont()
        self._bold_font.setBold(True)

    def on_font_changed(self):
        # Trigger a call to headerData() for FontRole/DisplayRole
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, len(C.ALL_COLS) - 1)

    @_qt_guard
    def rowCount(self, parent=QModelIndex()):
        # Direct count of the row objects
        if not self._reminders_model:
            return 0  # Return an actual integer when the model isn't present, not None!
        return len(self._reminders_model)
    
    #@_qt_guard
    def columnCount(self, parent=QModelIndex()):
        return len(C.ALL_COLS)

    def delete_reminder(self, row):
        #print(f"adapter.reomove_row called")

        # Start a  'sandwich' (Parent index, start row, end row)
        # to signal the start of a structural change that affects row_count.
        # (Since we're only deleting one row, start and end are both 'row')
        self.beginRemoveRows(QModelIndex(), row, row)

        # Do the deed
        self._reminders_model.delete(row)

        # Close the 'sandwich'
        self.endRemoveRows()

    def add_reminder(self, reminder_data: dict):
        """
        Process the dictionary from the EditDialog and add a new ReminderItem.
        """
        # 1. Create the new domain object
        new_item = ReminderItem(
            when=reminder_data["when"],
            descr=reminder_data["descr"],
            notes=reminder_data["notes"],
            repeat=reminder_data["repeats"],
        )

        # 2. The 'Reset' Sandwich (Better for sorting than beginInsertRows)
        # This tells the View: "Hold your breath, the whole list is shifting."
        self.beginResetModel()
        self._reminders_model.add(new_item)
        self.endResetModel()

    @_qt_guard
    def data(self, index, role):
        if not index:
            return None
        if not index.isValid():
            return None

        # Quick Exit for roles we don't handle
        if role not in (Qt.DisplayRole, C.ALERTS_ROLE, C.REPEATS_ROLE,
                        Qt.FontRole, Qt.TextAlignmentRole):
            return None

        row_idx = index.row()
        col_idx = index.column()

        # Skip action-button columns (they're handled in the View)
        if col_idx >= C.FIRST_BTN_IDX:
            # Skip if the View is asking for TEXT (DisplayRole)
            if role == Qt.ItemDataRole.DisplayRole:
                return None

        reminder = self.get_reminder(row_idx)
        if not reminder:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            # Derive the value to display
            col_id = C.COLUMN_SCHEMA[col_idx].id
            return self._get_display_value(reminder, col_id)

        if role == C.ALERTS_ROLE:
            # Query from view: How to display the Alerts button
            value = getattr(reminder, "alerts_enabled", False)
            #print(f"ROW {row_idx} | FLAGS: '{reminder._flags}' | ALERTS: {value}")
            return value

        if role == C.REPEATS_ROLE:
            # Query from view: How to display the Repeat button
            return getattr(reminder, "repeats", False) # ToDo: Implement this

        # Styling
        if role == Qt.FontRole and getattr(reminder, "is_critical", False):
            # Bold entire row if critical
            return self._bold_font

        if role == Qt.TextAlignmentRole:
            #print(f"Row {row_idx} alignment check: {reminder.has_notes}")
            v_bit = v_alignment(reminder)
            h_bit = h_alignment(col_idx)
            return v_bit | h_bit

        return None

    # Pass-thru m,ethod
    def get_reminder(self, row: int):
        """Delegates to the domain model to fetch the actual object."""
        return self._reminders_model.get_reminder(row)

    @staticmethod
    def _get_display_value(reminder, col_id):
        if col_id == "FLAG":
            # The 'User Facing' string: Show the ! but hide (alerts-enabled) "A"
            return C.IS_CRITICAL_FLAG if reminder.is_critical else ""

        # If col_id is in UI_COL_MAP, use that value.
        # Otherwise, default to the lowercase col_id, to map
        # the Column ID to the ReminderItem attribute name.
        # e.g., If col_id is "TIME", look for reminder.time
        attr_name = C.UI_COL_MAP.get(col_id, col_id.lower())
        value = getattr(reminder, attr_name, "")
        return value

    def headerData(self, section, orientation, role=Qt.DisplayRole):  # type: ignore[attr-defined]
        # Only care about horizontal headers
        if orientation != Qt.Horizontal:  # type: ignore[attr-defined]
            return None
        
        # Qt sometimes asks for out-of-range sections; Prevent crash here
        if section < 0 or section >= len(C.ALL_COLS):
            return None

        col_def = C.ALL_COLS[section]
        if role == Qt.DisplayRole:  # type: ignore[attr-defined]
            return col_def.label
            #return C.ALL_COL_LABELS[section]

        if role == Qt.ItemDataRole.FontRole:
            font = QFont()
            font.setPointSize(config.hdr_font_pt_size)
            font.setBold(True)
            return font

        if role == Qt.TextAlignmentRole:
            return C.ALIGN_MAP[col_def.align] | Qt.AlignmentFlag.AlignVCenter

        return super().headerData(section, orientation, role)

    def toggle_flag(self, row_idx):
        # Tell the Domain Model to flip the bit
        self._reminders_model.toggle_item_flag(row_idx)

        # Define the range (from first column to last)
        left = self.index(row_idx, 0)
        right = self.index(row_idx, self.columnCount() - 1)

        # Emit with specific roles to trigger an immediate repaint
        # (Qt.EditRole forcew qn immediate refresh)
        self.dataChanged.emit(left, right, [Qt.FontRole, Qt.DisplayRole, Qt.EditRole])

    def save_to_disk(self):
        self._reminders_model.save()

#endCLASS
