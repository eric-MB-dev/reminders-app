from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QLabel,
                               QLineEdit, QTextEdit, QComboBox, QDateEdit,
                               QTimeEdit, QDialogButtonBox)
from PySide6.QtCore import Qt, QDate, QTime, QSize
import datetime

# noinspection PyPep8Naming
import app.table_constants as C
from app.config import config

class ReminderDialog(QDialog):
    def __init__(self, parent=None, reminder=None):
        super().__init__(parent)
        self.reminder = reminder
        self.setWindowTitle("Edit Reminder" if reminder else "New Reminder")

        # 1. Main Layouts
        self.main_layout = QVBoxLayout(self)
        self.grid = QGridLayout()

        # Field height & width
        base_height = 70
        scaled_height = int(base_height * config.scale_factor)
        descr_def = C.ALL_COLS[C.DESCR_IDX]
        field_width = descr_def.max_w
        scaled_width = int(field_width * config.scale_factor)

        # 2. Description (Single line, focused by default)
        self.main_layout.addWidget(QLabel("Item:"))
        self.descr_edit = QLineEdit()
        self.descr_edit.setPlaceholderText("Thing to do or place to be")
        self.descr_edit.setFixedWidth(scaled_width)
        self.main_layout.addWidget(self.descr_edit)

        # 3. Notes (Multi-line, 3 lines high, word wrap)
        self.main_layout.addWidget(QLabel("Notes:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setTabChangesFocus(True)
        self.notes_edit.setAcceptRichText(False)
        self.notes_edit.setPlaceholderText("Optional details...")
        self.notes_edit.setFixedHeight(scaled_height)
        self.notes_edit.setFixedWidth(scaled_width)
        self.main_layout.addWidget(self.notes_edit)

        # 4. Day / Date / Time Grid
        self.grid.addWidget(QLabel("Day"), 0, 0)
        self.grid.addWidget(QLabel("Date"), 0, 1)
        self.grid.addWidget(QLabel("Time"), 0, 2)

        # Day Selector
        self.days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.day_combo = QComboBox()
        self.day_combo.addItems(self.days)
        self.grid.addWidget(self.day_combo, 1, 0)

        # Date Picker
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDisplayFormat(config.date_display_format)
        self.grid.addWidget(self.date_edit, 1, 1)

        # Time Picker
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat(config.time_display_format)
        self.grid.addWidget(self.time_edit, 1, 2)

        self.main_layout.addLayout(self.grid)

        # 5. Dialog Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

        # 6. Signals for Auto-Sync
        self.date_edit.dateChanged.connect(self.sync_day_from_date)
        self.day_combo.currentIndexChanged.connect(self.sync_date_from_day)

        self._repeats_json = ""  # Placeholder for item-repeats schedule

        # 7. Pre-populate
        self._populate_initial_values()
        self.descr_edit.setFocus()

    def _populate_initial_values(self):
        if self.reminder:
            # Note: access private members or use your ReminderItem properties
            self.descr_edit.setText(self.reminder._descr)
            self.notes_edit.setPlainText(self.reminder._notes)

            if self.reminder._when:
                dt = self.reminder._when
                self.date_edit.setDate(QDate(dt.year, dt.month, dt.day))
                self.time_edit.setTime(QTime(dt.hour, dt.minute))
        else:
            self.date_edit.setDate(QDate.currentDate())
            # Default new time to top of next hour? Or just current time
            self.time_edit.setTime(QTime.currentTime())

        self.sync_day_from_date()

    def sync_day_from_date(self, qdate=None):
        """Updates Day dropdown when Date changes."""
        if qdate is None: qdate = self.date_edit.date()
        # QDate dayOfWeek: 1 (Mon) to 7 (Sun)
        self.day_combo.setCurrentIndex(qdate.dayOfWeek() - 1)

    def sync_date_from_day(self, index):
        """Logic from your old update_date_from_day."""
        today = QDate.currentDate()
        target_day = index + 1  # Qt Mon=1

        days_ahead = (target_day - today.dayOfWeek() + 7) % 7
        if days_ahead == 0: days_ahead = 7

        self.date_edit.setDate(today.addDays(days_ahead))

    def get_results(self):
        """Extracts values into a dict for the ReminderItem constructor."""
        qdate = self.date_edit.date()
        qtime = self.time_edit.time()

        # Combine into python datetime
        combined_dt = datetime.datetime(
            qdate.year(), qdate.month(), qdate.day(),
            qtime.hour(), qtime.minute()
        )

        return {
            "descr": self.descr_edit.text(),
            "notes": self.notes_edit.toPlainText(),
            "when": combined_dt,
            "repeats": getattr(self, "_repeats_json", "")  # Placeholder for now
        }
