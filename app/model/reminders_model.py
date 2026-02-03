# view_model.py
# Part of the qt_ui package
#
# RemindersModel handles domain logic and domain-formatted rows.
# This is the DATA MODEL that the RemindersTableModel delegates to.
# It exposes reminder items, produces display rows for the table, and provides
# domain column counts and values. (It knows nothing about UI columns, button
# columns, widths, delegates, or Qt-specific behavior. The ViewModel is the
# pure data/logic layer consumed by the Qt table model.)

#import datetime as dt   # contains date, time, & datetime classes
#import utils as fcn

# noinspection PyPep8Naming
import app.table_constants as C

class RemindersModel:
    def __init__(self, data_manager=None, reminder_list=None):
        if reminder_list is not None:
            self._reminder_items = reminder_list
        elif data_manager is not None:
            self._reminder_items = data_manager.load()
        else:
            raise ValueError("Need reminder_list or data_manager")

    def items(self):
        return self._reminder_items

    def display_rows(self):
        if not self._reminder_items:
            #TODO: RETURN "No entries yet. Add some!" in an otherwise empty row
            return []
        
        return [item.to_display_row() for item in self._reminder_items]
    
    def set_flag_value(self, row, new_value):
        reminder = self._reminder_items[row]
        reminder.flag = new_value

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

#end CLASS ReminderDataModel
