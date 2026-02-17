from PySide6.QtWidgets import (QDialog, QFormLayout, QSpinBox, QComboBox,
                               QDialogButtonBox, QVBoxLayout, QLabel)
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

        # Main Layout
        self.layout = QVBoxLayout(self)
        self.form = QFormLayout()

        # TODO: Add the ported Tkinter fields here

        # Font Size Selector (9-16)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(9, 16)
        initial_size = config.cell_font_pt_size
        self.font_size_spin.setValue(self.settings.get("font_size", initial_size))
        self.form.addRow("UI Font Size:", self.font_size_spin)

        # Line Limit Selector (1, 2, or 3)
        # TODO: Get current from config. Set it to default limit during init. Replace when read in.
        self.line_limit_combo = QComboBox()
        self.line_limit_combo.addItems(["1 Line", "2 Lines", "3 Lines"])
        # Map 1,2,3 to index 0,1,2
        current_limit = self.settings.get("line_limit", 2)        # Range 1..3 TODO: MAGIC NMBER
        self.line_limit_combo.setCurrentIndex(current_limit - 1)  # Range 0..2
        self.form.addRow("Max Lines per Row:", self.line_limit_combo)

        # 3. Standard OK/Cancel Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addLayout(self.form)
        self.layout.addWidget(self.buttons)

    def get_results(self):
        """Returns the dictionary of new settings."""
        return {
            "font_size": self.font_size_spin.value(),
            "line_limit": self.line_limit_combo.currentIndex() + 1
        }

'''
class ConfigDialog(tk.Toplevel):
    # -----------------------------------------
    # Built‑in format definitions
    # -----------------------------------------
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

    # -----------------------------------------
    # Helper: build labels & lookup table
    # -----------------------------------------
    @staticmethod
    def build_options(pairs):
        labels = []
        lookup = {}
        for fmt, example in pairs:
            label = f"{fmt}   ({example})"
            labels.append(label)
            lookup[label] = fmt
        return labels, lookup

    # -----------------------------------------
    # Constructor
    # -----------------------------------------
    def __init__(self, parent, on_save):
        super().__init__(parent)

        # Position relative to parent
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        self.geometry(f"+{px + X_OFFSET}+{py + Y_OFFSET}")

        self.title("Settings")
        self.resizable(False, False)
        self.on_save = on_save
        self.values = {}

        # Build dropdown options
        self.date_labels, self.date_lookup = self.build_options(self.COMMON_DATE_FORMATS)
        self.time_labels, self.time_lookup = self.build_options(self.COMMON_TIME_FORMATS)

        # Determine which label matches current config values
        def label_for(fmt, lookup):
            for label, raw in lookup.items():
                if raw == fmt:
                    return label
            return list(lookup.keys())[0]

        # Build fields
        fields = [
            {
                "name": "date_format",
                "label": "Date Format",
                "value": label_for(config.date_display_format, self.date_lookup),
                "options": self.date_labels,
            },
            {
                "name": "time_format",
                "label": "Time Format",
                "value": label_for(config.time_display_format, self.time_lookup),
                "options": self.time_labels,
            },
        ]

        # -------------------------------------------------
        # Side‑by‑side radio groups for date & time formats
        # -------------------------------------------------
        # Variables
        self.date_var = tk.StringVar(value=label_for(config.date_display_format, self.date_lookup))
        self.time_var = tk.StringVar(value=label_for(config.time_display_format, self.time_lookup))

        # Frames
        date_frame = ttk.LabelFrame(self, text="Date Format")
        time_frame = ttk.LabelFrame(self, text="Time Format")

        date_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nw")
        ttk.Label(self, text=" ").grid(row=0, column=1)  # narrow separator
        time_frame.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="nw")

        # Date radio buttons
        for label in self.date_labels:
            ttk.Radiobutton(date_frame, text=label, variable=self.date_var, value=label).pack(anchor="w")

        # Time radio buttons
        for label in self.time_labels:
            ttk.Radiobutton(time_frame, text=label, variable=self.time_var, value=label).pack(anchor="w")

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Save", command=self.save).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="right", padx=10)

        self.grab_set() # Makes the dialog MODAL (nothing runs until it closes)

    # -----------------------------------------
    # Save handler
    # -----------------------------------------
    def save(self):
        result = {
            "date_format": self.date_lookup[self.date_var.get()],
            "time_format": self.time_lookup[self.time_var.get()],
        }
        self.on_save(result)
        self.destroy()
'''