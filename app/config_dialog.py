import tkinter as tk
from tkinter import ttk
import config

# Position of dialog relative to main frame
X_OFFSET = 150
Y_OFFSET = 150

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
