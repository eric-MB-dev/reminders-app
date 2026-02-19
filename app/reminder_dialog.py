from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QLabel,
                               QLineEdit, QTextEdit, QComboBox, QStyle,
                               QDialogButtonBox, QCalendarWidget,
                               QToolButton, QHBoxLayout, QMenu,
                               )
from PySide6.QtCore import Qt, QDate, QTime, QSize
from PySide6.QtGui import QIcon

import datetime as dt

# noinspection PyPep8Naming
import app.table_constants as C
from app.config import config

class ReminderDialog(QDialog):

    def __init__(self, parent=None, reminder=None):
        super().__init__(parent)
        self.reminder = reminder
        self.setWindowTitle("Edit Reminder" if reminder else "New Reminder")

        # Set user's desired font size
        # Apply the current font scaling from your singleton
        dialog_font = self.font()
        dialog_font.setPointSize(config.cell_font_pt_size)
        self.setFont(dialog_font)

        # Main Layouts
        self.main_layout = QVBoxLayout(self)
        self.grid = QGridLayout()

        # Field height & width
        base_height = 70
        scaled_height = int(base_height * config.scale_factor)
        descr_def = C.ALL_COLS[C.DESCR_IDX]
        field_width = descr_def.max_w
        scaled_width = int(field_width * config.scale_factor)

        # Description (Single line, focused by default)
        self.main_layout.addWidget(QLabel("Item:"))
        self.descr_edit = QLineEdit()
        self.descr_edit.setPlaceholderText("Thing to do or place to be")
        self.descr_edit.setFixedWidth(scaled_width)
        self.main_layout.addWidget(self.descr_edit)

        # Notes (Multi-line, 3 lines high, word wrap)
        self.main_layout.addWidget(QLabel("Notes:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setTabChangesFocus(True)
        self.notes_edit.setAcceptRichText(False)
        self.notes_edit.setPlaceholderText("Optional details...")
        self.notes_edit.setFixedHeight(scaled_height)
        self.notes_edit.setFixedWidth(scaled_width)
        self.main_layout.addWidget(self.notes_edit)

        # Day / Date / Time Grid
        self.grid.addWidget(QLabel("Day"), 0, 0)
        self.grid.addWidget(QLabel("Date"), 0, 1)
        self.grid.addWidget(QLabel("Time"), 0, 2)

        # Day Selector
        self.days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.day_combo = QComboBox()
        self.day_combo.addItems(self.days)
        self.day_combo.setEditable(False)
        self.grid.addWidget(self.day_combo, 1, 0)

        # Date and Time popup-launching icons
        icon_date = self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        icon_time = self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight)

        # --- DATE FIELD & CALENDAR-SELECTOR BUTTON ---
        self.date_container = self.build_date_picker()
        self.grid.addLayout(self.date_container, 1, 1)

        # Time Picker
        self.time_container = self.build_time_picker()
        self.grid.addLayout(self.time_container, 1, 2)

        self.main_layout.addLayout(self.grid)

        # 5. Dialog Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

        # 6. Signals for Auto-Sync
        self.date_edit.editingFinished.connect(self.sync_day_from_date)
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
                when = self.reminder._when
                date_str = when.strftime(config.date_display_format)
                self.date_edit.setText(date_str)

                time = when.strftime(config.time_display_format)
                self.time_edit.setText(time_str)
        else:
            date_str = dt.datetime.now().strftime(config.date_display_format)
            self.date_edit.setText(date_str)

            # Default new time to top of next hour
            self.time_edit.setText("")

        self.sync_day_from_date()

    def sync_day_from_date(self, qdate=None):
        """Updates Day dropdown when Date changes."""
        date_str = self.date_edit.text().strip()
        if not date_str:
            return  # Handle 'Placeholder' (blank) dates gracefully
        try:
            # 1. Parse the string using the user's configured format
            py_date = dt.datetime.strptime(date_str, config.date_display_format)

            # 2. Map Python weekday to the QDate dayofWeek dropdown index
            #    = 0 (Mon) to 7 (Sun))
            self.day_combo.setCurrentIndex(py_date.weekday())
        except ValueError:
            # User typed something invalid; we just ignore the day-sync
            pass


    def sync_date_from_day(self, index):
        """
        Calculate the next upcoming date based on the Day selection.
        """

        # Qt/ISO   1      2      3      4      5      6      7
        # days: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        # Get Today's ISO index (1-7)
        today = QDate.currentDate()
        today_iso_idx = today.dayOfWeek()

        # Map ComboBox (0-6) to Qt ISO (1-7)
        target_iso_idx = index + 1

        # Calculate jump
        days_ahead = (target_iso_idx - today_iso_idx + 7) % 7
        if days_ahead == 0:
            next_qdate = today
        else:
            # Use Qt's addDays to avoid timedelta conflicts
            next_qdate = today.addDays(days_ahead)

        # Convert to Python date for strftime display
        py_date = dt.date(next_qdate.year(), next_qdate.month(), next_qdate.day())
        self.date_edit.setText(py_date.strftime(config.date_display_format))

    '''
    def build_time_menu(self):
        menu = QMenu(self)
        for hour in range(9, 20):  # 9 AM to 7 PM
            h_str = f"{hour if hour <= 12 else hour - 12}"
            ampm = "AM" if hour < 12 else "PM"

            # Submenu for the :00, :15, :30, :45 increments
            hour_menu = menu.addMenu(f"{h_str} {ampm}")
            for mins in ["00", "15", "30", "45"]:
                time_str = f"{h_str}:{mins} {ampm}"
                action = hour_menu.addAction(time_str)
                # When clicked, just shove the string into the QLineEdit
                action.triggered.connect(lambda _, t=time_str: self.time_edit.setText(t))
        return menu
    '''

    def get_results(self):
        date_str = self.date_edit.text().strip()
        time_str = self.time_edit.text().strip()

        # If no date, 'when' is None (Placeholder Event)
        if not date_str:
            when = None
        else:
            # We know this is valid because accept() passed
            parsed_date = dt.datetime.strptime(date_str, config.date_display_format).date()

            if not time_str:
                # Date exists, but no time (Default to Midnight)
                when = dt.datetime.combine(parsed_date, dt.time.min)
            else:
                # Both exist
                parsed_time = dt.datetime.strptime(time_str, config.time_display_format).time()
                when = dt.datetime.combine(parsed_date, parsed_time)

        return {
            "descr": self.descr_edit.text().strip(),
            "notes": self.notes_edit.toPlainText().strip(),
            "when": when,
            "repeats": getattr(self, "_repeats_json", "")
        }

    from PySide6.QtWidgets import QMessageBox

    def accept(self):
        """Validate data when use presses the OK button."""
        date_str = self.date_edit.text().strip()
        time_str = self.time_edit.text().strip()

        # 1. Validate Date (if not blank)
        if date_str:
            try:
                dt.datetime.strptime(date_str, config.date_display_format)
            except ValueError:
                QMessageBox.warning(self, "Invalid Date",
                                    f"Date does not match format:\n{config.date_display_format}")
                self.date_edit.setFocus()
                return  # Stops the dialog from closing

        # 2. Validate Time (if not blank)
        if time_str:
            try:
                dt.datetime.strptime(time_str, config.time_display_format)
            except ValueError:
                QMessageBox.warning(self, "Invalid Time",
                                    f"Time does not match format:\n{config.time_display_format}")
                self.time_edit.setFocus()
                return

        # If we got here, everything is valid (or blank)
        super().accept()

    def build_date_picker(self):
        date_container = QHBoxLayout()
        date_container.setSpacing(2) # Keep icon snug to the field

        # Text Field
        self.date_edit = QLineEdit()
        date_str = dt.date.today().strftime(config.date_display_format)
        self.date_edit.setText(date_str)

        # Clickable Icon (QToolButton)
        self.cal_btn = QToolButton()
        # Standard "Grid" or "Calendar" style icon
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        self.cal_btn.setIcon(icon)
        self.cal_btn.clicked.connect(self.show_calendar_popup)

        # Add to UI
        date_container.addWidget(self.date_edit)
        date_container.addWidget(self.cal_btn)

        return date_container

    def show_calendar_popup(self):
        print("Calendar Icon Triggered")

        # Create a temporary, floating calendar
        # Attach it to the main dialog so it isn't garbage collected immediately
        self.cal_popup = QCalendarWidget(self)
        self.cal_popup.setWindowFlags(Qt.WindowType.Popup)

        # -- FONT SIZE ---
        # Apply the user's configured font size to the entire widget
        cal_font = self.cal_popup.font()
        cal_font.setPointSize(config.cell_font_pt_size)
        self.cal_popup.setFont(cal_font)

        # Force the internal table to resize to the new font
        # so numbers don't look cramped inside the cells
        self.cal_popup.updateGeometry()

        # --- ACTION ---
        # Pre-select the date currently in the box (if valid)
        current_text = self.date_edit.text().strip()
        try:
            parsed_dt = dt.datetime.strptime(current_text, config.date_display_format)
            self.cal_popup.setSelectedDate(QDate(parsed_dt.year, parsed_dt.month, parsed_dt.day))
        except ValueError:
            self.cal_popup.setSelectedDate(QDate.currentDate())

        # Position it right under the date field so it doesn't float randomly
        # mapToGlobal translates the local widget coordinates to screen coordinates
        global_pos = self.date_edit.mapToGlobal(self.date_edit.rect().bottomLeft())
        self.cal_popup.move(global_pos)

        # Internal handler to update the fields when a date is picked
        def on_date_picked(qdate):
            py_date = dt.date(qdate.year(), qdate.month(), qdate.day())
            self.date_edit.setText(py_date.strftime(config.date_display_format))

            # Sync the Day ComboBox (Qt 1-7 to Index 0-6)
            self.day_combo.setCurrentIndex(qdate.dayOfWeek() - 1)
            self.cal_popup.close()

        # clicked emits the QDate that was selected
        self.cal_popup.clicked.connect(on_date_picked)
        self.cal_popup.show()


    # --- BUILD TIME PICKER ---
    def build_time_picker(self):
        # Create the horizontal container
        time_container = QHBoxLayout()
        time_container.setSpacing(2)

        # Text Field (Placeholder only, no default)
        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText("") # Field starts empty
        time_container.addWidget(self.time_edit)

        # Clock Button and Menu
        self.time_btn = QToolButton()
        self.time_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight))

        time_menu = QMenu(self)
        time_menu.setFont(self.font())

        # --- DEFAULT TIME (next hour) ---
        now = dt.datetime.now()
        next_hour_dt = (now + dt.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

        # Format based on user's .ini setting (e.g. "2:00 PM" or "14:00")
        default_time_str = next_hour_dt.strftime(config.time_display_format)

        # Format just the "Hour Label" for the menu (e.g. "2 PM" or "14:00")
        # We'll use this to identify the submenu
        default_hour_label = next_hour_dt.strftime("%I %p" if "p" in config.time_display_format.lower() else "%H:00")

        # --- CHOICES MENU ---
        # Build 9 AM to 7 PM using the config format
        for h in range(9, 20):
            # Create a temp time object for the top-level hour label
            temp_hour = dt.time(h, 0)
            # Label matches config style (12h vs 24h)
            hour_label = temp_hour.strftime("%I %p" if "p" in config.time_display_format.lower() else "%H:00")

            hour_sub = time_menu.addMenu(hour_label)

            # Highlight the 'Next Hour' submenu
            if hour_label == default_hour_label:
                hour_sub.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward))

            for m in [0, 15, 30, 45]:
                temp_time = dt.time(h, m)
                # This string matches the user's .ini format exactly
                time_str = temp_time.strftime(config.time_display_format)

                action = hour_sub.addAction(time_str)
                action.triggered.connect(lambda _, t=time_str: self.time_edit.setText(t))

        self.time_btn.setMenu(time_menu)
        self.time_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        time_container.addWidget(self.time_btn)

        return time_container

#endClass ReminderDialog