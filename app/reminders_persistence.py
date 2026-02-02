# reminders_list_manager.py
#
# RemindersListManager is the persistence layer for reminders: it loads and
# saves Reminder items from storage (CSV or possible future backends).
# It maintains the in‑memory list, and provides add/edit/delete operations.
# It contains no UI logic and no knowledge of table columns or delegates.
# This layer is the application’s data manager, supplying the ViewModel with domain objects.

import os, csv
import datetime as dt
# "dt" module contains date, time, & datetime classes

from tkinter import messagebox, filedialog   #, simple dialogs
from reminder_item import ReminderItem

# noinspection PyPep8Naming
import app.table_constants as C

# The INTERNAL data model (separate from the storage model & the display model)
class RemindersPersistence:

    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.reminders = []
        self.load()

    def _initialize_empty_csv(self):
        with open(self.csv_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(C.CSV_COL_HEADERS)
            writer.writerow(C.INITIAL_CSV_DATA)
        return self.csv_path
    
    # Load values stored in CSV file
    # FUTURE
    #  Access curr_reminders_file from CONFIG
    #  Allow multiple reminder files (e.g. work & home) ask for name
    #  Ask for name & location, save in a selectable list, add to config dialog & class
    def load(self):
        """
        Load reminders from CSV into self.reminders.
        Parse CSV rows → list of Reminder objects
        """
        if not os.path.exists(self.csv_path):
            self._initialize_empty_csv()

        self.reminders = []
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header row
            for row in reader:
                self.reminders.append(ReminderItem.from_csv_row(row))
        return self.reminders

    # Store reminders in user's CSV file
    def save(self, reminders):
        #print(f"csv+path = {self.csv_path}")
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(C.CSV_COL_HEADERS)
            for r in reminders:
                writer.writerow(r.to_csv_row())

#end CLASS RemindersPersistence
