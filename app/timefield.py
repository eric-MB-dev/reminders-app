import tkinter as tk
from tkinter import ttk

class TimeField(ttk.Frame):
    """Hybrid time entry/chooser widget with validation and 12h→24h conversion."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.time_var = tk.StringVar(value="")
        self._build_entry()

    def _build_entry(self):
        self.time_entry = ttk.Entry(self, textvariable=self.time_var, width=10)
        self.time_entry.grid(row=0, column=0, padx=5, pady=5)
        self.time_entry.bind("<FocusIn>", self._activate_chooser)

    def _activate_chooser(self, event=None):
        self.time_entry.destroy()
        self.hour_var = tk.StringVar(value="")
        self.minute_var = tk.StringVar(value="")
        self.am_pm_var = tk.StringVar(value="")

        self.hour_spin = ttk.Spinbox(self, values=[f"{h:02d}" for h in range(1,13)],
                                     textvariable=self.hour_var, width=3, wrap=True)
        self.hour_spin.grid(row=0, column=0, padx=(5,2), pady=5)

        self.minute_spin = ttk.Spinbox(self, values=[f"{m:02d}" for m in range(0,60)],
                                       textvariable=self.minute_var, width=3, wrap=True)
        self.minute_spin.grid(row=0, column=1, padx=(2,2), pady=5)

        self.ampm_combo = ttk.Combobox(self, textvariable=self.am_pm_var,
                                       values=["AM","PM"], width=3, state="readonly")
        self.ampm_combo.grid(row=0, column=2, padx=(2,5), pady=5)

        self.hour_spin.bind("<FocusOut>", self._validate)
        self.minute_spin.bind("<FocusOut>", self._validate)
        self.ampm_combo.bind("<<ComboboxSelected>>", self._validate)

    def _validate(self, event=None):
        h, m, ap = self.hour_var.get(), self.minute_var.get(), self.am_pm_var.get()
        if not h and not m and not ap:
            self.hour_spin.destroy()
            self.minute_spin.destroy()
            self.ampm_combo.destroy()
            self.time_var.set("")
            self._build_entry()
        else:
            if h.isdigit():
                self.hour_var.set(f"{int(h):02d}")
            if m.isdigit():
                self.minute_var.set(f"{int(m):02d}")

    def get_time_string(self):
        if hasattr(self, "hour_var"):
            h, m, ap = self.hour_var.get(), self.minute_var.get(), self.am_pm_var.get()
            if h and m and ap:
                return f"{h}:{m} {ap}"
            return ""
        return self.time_var.get()

    def get_time_24h(self):
        t = self.get_time_string()
        if not t:
            return ""
        try:
            parts = t.strip().split()
            hm = parts[0]
            h, m = hm.split(":")
            h, m = int(h), int(m)
            if len(parts) == 2:
                ap = parts[1].upper()
                if ap == "PM" and h != 12:
                    h += 12
                if ap == "AM" and h == 12:
                    h = 0
            return f"{h:02d}:{m:02d}"
        except ValueError:
            return t

    def set_time(self, time_str):
        """Accepts 'HH:MM' (24h) or 'HH:MM AM/PM' and populates the widget."""
        if not time_str:
            self.time_var.set("")
            return

        try:
            parts = time_str.strip().split()
            hm = parts[0]
            h, m = hm.split(":")
            h, m = int(h), int(m)
            am_pm = None
            if len(parts) == 2:
                am_pm = parts[1].upper()
            else:
                # convert from 24h to AM/PM
                am_pm = "AM"
                if h == 0:
                    h = 12
                elif h == 12:
                    am_pm = "PM"
                elif h > 12:
                    h -= 12
                    am_pm = "PM"

            # force chooser mode
            self._activate_chooser()
            self.hour_var.set(f"{h:02d}")
            self.minute_var.set(f"{m:02d}")
            self.am_pm_var.set(am_pm)
        except ValueError:
            # fallback: just show raw string in entry
            self.time_var.set(time_str)
            if not hasattr(self, "time_entry"):
                self._build_entry()
