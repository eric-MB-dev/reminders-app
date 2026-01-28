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

import config

# REVISED STORAGE model: Storing notes, but not the alert schedule.
#OLD_CSV_COL_HEADERS = ["Item", "Date", "Time", "Dys Bef", "Hrs Bef", "Mins Bef"]
CSV_COL_HEADERS = ["Item", "Date", "Time", "Notes"]  # ToDo: + , "Repeat"

# The INTERNAL data model (separate from the storage model & the display model)
class RemindersPersistence:
    # TODO: Should we pass cvs_path as a constructor arg?
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.reminders = []
        self.load_reminders()
        
    def sort(self):
        # Sort in date/time order. No-date items at top. Where item has date(datetime.date). time(datetime.time), or None
        self.reminders.sort(key=lambda r: r.sort_key())

    def add(self, reminder):
        self.reminders.append(reminder)
        self.sort()

    def remove(self, reminder):
        self.reminders.remove(reminder)

    def find_by_id(self, reminder_id):
        """Optional: lookup helper if we add IDs later."""
        pass
    
    def initialize_items_file(self):
        # Ask user to select a folder
        folder_path = filedialog.askdirectory(title="Choose a folder for the reminder file")
        if not folder_path:
            messagebox.showinfo("No Folder Selected", "File creation was canceled.")
            return None
        
        # Create the full file path
        # FUTURE
        #   Allow user to choose csv filename
        self.csv_path  = os.path.join(folder_path, config.DEFAULT_CSV_FILE)
        
        # Create the items file
        with open(self.csv_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(CSV_COL_HEADERS)
        
        return self.csv_path
    
    # Load values stored in CSV file
    # FUTURE
    #  Access curr_reminders_file from CONFIG
    #  Allow multiple reminder files (e.g. work & home) ask for name
    #  Ask for name & location, save in a selectable list, add to config dialog & class
    #TODO: Merge with my original load_items routine below
    def load_reminders(self):
        """
        Load reminders from CSV into self.reminders.
        Parse CSV rows → list of Reminder objects
        """
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header row
            for row in reader:
                self.reminders.append(ReminderItem.from_csv_row(row))
        return self.reminders
    def load_items(self):
        if not os.path.exists(self.csv_path):
            if messagebox.askyesno(
                    "File Not Found", f"{self.csv_path} not found"
                    + "Would you like to create it?"):
                self.initialize_items_file()  # Returns path, but not used
            return []
            #TODO: Special display when reminder-list is empty
        
        with open(self.csv_path, newline="") as file:
            '''
            Tell PyCharm to shut up. We're expecting dates, times, ints in the file.
            idate: datetime.date | None
            itime: datetime.time | None
            days_bef: str
            hrs_bef: str
            mins_bef: str
            '''
            reader = csv.reader(file)
            next(reader)  # skip header
            for row in reader:
                try:
                    item_date, item_time, title, notes = row
                    idatetime = None
                    if item_date:
                        idatetime = dt.date.fromisoformat(item_date)
                    if item_time:
                        idatetime = dt.datetime.fromisoformat(item_time)
                    self.reminders.append(ReminderItem(idatetime, title, notes))
                except ValueError:
                    print(f"Skipping malformed row: {row}")
        return self.reminders
    
    # Store reminders in user's CSV file
    # FUTURE
    #   Access curr_reminders_file from CONFIG
    # TODO: Merge with my original save_items routine below
    def save(self):
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for r in self.reminders:
                writer.writerow(r.to_csv_row())
    def save_items(self):
        with open(self.csv_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(CSV_COL_HEADERS)
            for i in self.reminders:
                idate = ""
                itime = ""
                if i.date:
                    idate = i.date.isoformat()
                if i.time:
                    itime = i.time.strftime("%H:%M") if i.time else ""
                writer.writerow([idate, itime, i.text, i.notes])
                
#end CLASS RemindersManager
