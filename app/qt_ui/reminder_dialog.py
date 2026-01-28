import tkinter as tk
from tkinter import ttk
import datetime
from tkcalendar import DateEntry

from app import config
from app.timefield import TimeField
import utils as fcn  # for getDay()

# Position of dialog relative to main frame
X_OFFSET = 150
Y_OFFSET = 150

class ReminderDialog(tk.Toplevel):
    '''
    Dual-purpose dialog for adding and editing reminders.
    This dialog manages name, date, day-of-week, and time fields.
    Configuration parameters such as date/time display formats are
    provided by the main application (defaults now, user-selected
    .ini values eventually).

    Args:
        master (tk.Widget): Parent window.
        reminder (Reminder, optional): Existing reminder to edit.
        on_save (callable, optional): Callback invoked with reminder data.
        date_format (str): Format string for date display.
        time_format (str): Format string for time display.
    '''
    def __init__(self, master, reminder=None, on_save=None,
                 date_format=config.date_display_format,
                 time_format=config.time_display_format):
        super().__init__(master)

        self.on_save = on_save
        self.reminder = reminder
        self.date_format = date_format
        self.time_format = time_format

        self.title("Edit Reminder" if reminder else "New Reminder")
        self.geometry("320x150+300+200")
        # Position relative to parent
        px = master.winfo_rootx()
        py = master.winfo_rooty()
        self.geometry(f"+{px + X_OFFSET}+{py + Y_OFFSET}")
        self.resizable(True, False)

        # Vars used across methods
        self.name_var = tk.StringVar()
        self.day_var = tk.StringVar()
        self.date_var = tk.StringVar()  # used for display if you want a textvariable somewhere

        self.build_ui()
        self.grab_set()
        self.item_name_entry.focus_force()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Prepopulate after wx_ui exist
        self._populate_initial_values()

    def _populate_initial_values(self):
        if self.reminder:
            self.name_var.set(self.reminder.name or "")
            if self.reminder.date:
                self.date_entry.set_date(self.reminder.date)
            if self.reminder.time:
                self.time_field.set_time_24h(self.reminder.time)  # add helper if needed
        else:
            # Default to today for new reminders
            self.date_entry.set_date(datetime.date.today())

        # Sync day with current date
        self.update_day()

    def build_ui(self):
        # Name
        tk.Label(self, text="Item:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.item_name_entry = tk.Entry(self, textvariable=self.name_var)
        self.item_name_entry.grid(row=0, column=1, columnspan=3, sticky="ew", padx=10, pady=5)

        # Headings
        tk.Label(self, text="Day").grid(row=1, column=1, sticky="w", padx=10, pady=(5, 0))
        tk.Label(self, text="Date").grid(row=1, column=2, sticky="w", padx=10, pady=(5, 0))
        tk.Label(self, text="Time").grid(row=1, column=3, sticky="w", padx=10, pady=(5, 0))

        # Day combobox
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.day_combo = ttk.Combobox(self, textvariable=self.day_var,
                                      values=days, width=12, state="readonly")
        self.day_combo.grid(row=2, column=1, padx=10, pady=(0, 5))
        self.day_combo.bind("<<ComboboxSelected>>", self.update_date_from_day)

        # DateEntry (no StringVar needed; use get_date/set_date APIs)
        self.date_entry = DateEntry(self, width=16)
        self.date_entry.grid(row=2, column=2, sticky="w", padx=10, pady=(0, 5))
        self.date_entry.bind("<<DateEntrySelected>>", self.update_day)

        # Time field
        self.time_field = TimeField(self)
        self.time_field.grid(row=2, column=3, sticky="w", padx=10, pady=5)

        # Save
        tk.Button(self, text="Save", command=self.save).grid(row=4, column=1, columnspan=2, pady=10)

        # Stretch
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

    def update_day(self, event=None):
        try:
            chosen_date = self.date_entry.get_date()  # datetime.date
            weekday_name = fcn.getDay(chosen_date)
            self.day_var.set(weekday_name)
            # Also reflect in combobox selection index:
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            self.day_combo.current(days.index(weekday_name))
            # If you still want a textual date string somewhere:
            self.date_var.set(chosen_date.strftime(self.date_format))
        except Exception:
            self.day_var.set("")
            self.date_var.set("")

    def update_date_from_day(self, event=None):
        selected_day = self.day_var.get()
        if not selected_day:
            return
        today = datetime.date.today()
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        target_weekday = days.index(selected_day)
        days_ahead = (target_weekday - today.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        next_date = today + datetime.timedelta(days=days_ahead)
        self.date_entry.set_date(next_date)
        self.update_day()  # keep everything in sync

    def save(self):
        name = self.name_var.get().strip()
        date = self.date_entry.get_date()
        try:
            time = self.time_field.get_time_24h()
        except ValueError:
            time = None

        result = {
            "name": name,
            "day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].index(self.day_var.get())
            if self.day_var.get() else None,
            "date": date,
            "time": time,
        }
        if self.on_save:
            self.on_save(result)
        self.on_close()

    def on_close(self):
        geom = self.geometry()
        #print("Reminder dialog geometry:", geom)
        self.destroy()
