from PySide6.QtWidgets import (QDialog, QFormLayout, QSpinBox, QComboBox,
                               QDialogButtonBox, QHBoxLayout, QVBoxLayout,
                               QGroupBox, QButtonGroup, QRadioButton, QLabel,
                               )
from PySide6.QtCore import Qt

# noinspection PyPep8Naming
import table_constants as C
from app.config import config

# Position of dialog relative to main frame
X_OFFSET = 150
Y_OFFSET = 150

class ConfigDialog(QDialog):

    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Reminders System Settings")
        self.settings = current_settings or {}

        # Extract the list of "Previews" (format labels) and create a "Label -> Format" mapping
        self.date_labels = [item[1] for item in C.COMMON_DATE_FORMATS]
        self.date_lookup = {item[1]: item[0] for item in C.COMMON_DATE_FORMATS}

        self.time_labels = [item[1] for item in C.COMMON_TIME_FORMATS]
        self.time_lookup = {item[1]: item[0] for item in C.COMMON_TIME_FORMATS}

        # Main Layout
        self.layout = QVBoxLayout(self)
        self.form = QFormLayout()

        # Date & Time format selectors
        # Horizontal Layout for the side-by-side groups
        format_layout = QHBoxLayout()

        # --- DATE FORMAT GROUP ---
        self.date_group_box = QGroupBox("Date Format")
        date_vbox = QVBoxLayout()
        self.date_btn_group = QButtonGroup(self)  # Logical grouping, not visual
        #
        for label in self.date_labels:
            fmt_val = self.date_lookup[label]
            rb = QRadioButton(label)
            rb.setProperty("raw_format", fmt_val)  # Store the format string in the widget

            # Check if this matches the current config
            if fmt_val == config.date_display_format:
                rb.setChecked(True)

            self.date_btn_group.addButton(rb)
            date_vbox.addWidget(rb)

        self.date_group_box.setLayout(date_vbox)

        # --- TIME FORMAT GROUP ---
        self.time_group_box = QGroupBox("Time Format")
        time_vbox = QVBoxLayout()
        self.time_btn_group = QButtonGroup(self)
        #
        for label in self.time_labels:
            fmt_val = self.time_lookup[label]
            rb = QRadioButton(label)
            rb.setProperty("raw_format", fmt_val)

            if fmt_val == config.time_display_format:
                rb.setChecked(True)

            self.time_btn_group.addButton(rb)
            time_vbox.addWidget(rb)

        self.time_group_box.setLayout(time_vbox)

        # Add groups to horizontal layout and then to main layout
        format_layout.addWidget(self.date_group_box)
        format_layout.addWidget(self.time_group_box)
        self.layout.addLayout(format_layout)

        # --- TOP: DATE/TIME FORMAT RADIO BUTTONS ---
        format_layout = QHBoxLayout()
        format_layout.setSpacing(20)
        format_layout.addWidget(self.date_group_box)
        format_layout.addWidget(self.time_group_box)
        self.layout.addLayout(format_layout)

        # --- MIDDLE: FONT AND #OF-LINES SELECTORS ---
        selectors_layout = QHBoxLayout()
        selectors_layout.setContentsMargins(10, 10, 10, 10)
        selectors_layout.addStretch(1) # Centers the group

        # Font Size Column
        font_vbox = QVBoxLayout()
        font_vbox.addWidget(QLabel("Font Size"))
        self.font_size_combo = QComboBox()
        font_list = [str(i) for i in range(9, 17)]
        self.font_size_combo.addItems(font_list)
        #
        # Map the current font (e.g., 11) to the correct index
        # Since 9 is at index 0, 11 is at index 2 (11 - 9 = 2)
        current_font = config.cell_font_pt_size
        self.font_size_combo.setCurrentIndex(current_font - 9)
        #
        font_vbox.addWidget(self.font_size_combo)
        selectors_layout.addLayout(font_vbox)

        selectors_layout.addSpacing(40) # Gap between font and lines

        # Line Limit Column
        lines_vbox = QVBoxLayout()
        #
        #  Center the Label
        lbl_lines = QLabel("Max #of lines per row")
        lines_vbox.addWidget(lbl_lines, alignment=Qt.AlignmentFlag.AlignCenter)
        #
        self.line_limit_combo = QComboBox()
        self.line_limit_combo.addItems(["1", "2", "3"])
        self.line_limit_combo.setCurrentIndex(config.line_limit - 1)
        #
        # Fix the Width & Center the ComboBox
        # so it doesn't stretch to the full width of the label
        self.line_limit_combo.setFixedWidth(50)
        lines_vbox.addWidget(self.line_limit_combo, alignment=Qt.AlignmentFlag.AlignLeft)

        ##selectors_layout.addStretch(1) # Centers the group
        selectors_layout.addLayout(lines_vbox)

        self.layout.addLayout(selectors_layout)

        # --- BOTTOM: BUTTONS ---
        # Standard OK/Cancel Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addLayout(self.form)
        self.layout.addWidget(self.buttons)

    def get_results(self):
        """
        Returns the dictionary of new settings.
        """

        # checkedButton() returns the QRadioButton instance that is toggled
        date_btn = self.date_btn_group.checkedButton()
        time_btn = self.time_btn_group.checkedButton()

        return {
            "font_size":   int(self.font_size_combo.currentText()),
            "line_limit":  self.line_limit_combo.currentIndex() + 1, # 0..2 => 1..3
            "date_format": date_btn.property("raw_format"),
            "time_format": time_btn.property("raw_format"),
        }
