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
#import utilities as fcn

# noinspection PyPep8Naming
import app.table_constants as C

class RemindersModel:
    def __init__(self, data_manager=None, reminder_list=None):
        self._reminder_items = []
        if reminder_list is not None:
            self._reminder_items = reminder_list
        elif data_manager is not None:
            self.data_manager = data_manager
            self._reminder_items = data_manager.load()
        else:
            raise ValueError("Need reminder_list or data_manager")

    def update_countdown_values(self, now):
        # 1. Delegate the update to the data model
        # Update every item used for countdown calculations in the model's list
        # Assuming self.reminder_list is your collection of ReminderItems
        for item in self._reminder_items:
            item.update_countdown(now)

    def __len__(self):
        """Standard Python way to support len(model)"""
        return len(self._reminder_items) if self._reminder_items else 0

    def items(self):
        return self._reminder_items

    def display_rows(self):
        if not self._reminder_items:
            #TODO: RETURN "No entries yet. Add some!" in an otherwise empty row
            return []
        return [item.to_display_row() for item in self._reminder_items]

    def sort(self):
        # Sort in date/time order. No-date items at top. Where item has date(datetime.date). time(datetime.time), or None
        self._reminder_items.sort(key=lambda r: r.sort_key())

    def add(self, reminder):
        self._reminder_items.append(reminder)
        self.sort()
        self.save()

    def update(self, row_idx, reminder):
        self._reminder_items[row_idx] = reminder
        self.sort()
        self.save()

    def delete(self, row_idx):
        del self._reminder_items[row_idx]
        self.save()

    def get_reminder(self, row_idx: int) -> ReminderItem:
        """Returns the ReminderItem at the specified index."""
        try:
            return self._reminder_items[row_idx]  # Or whatever your internal list is named
        except IndexError:
            return None  # Or handle as a Graceful Failure

    def index_of(self, item):
        """
        Returns the integer row index of a specific ReminderItem.
        Used by the View to locate a new or edited item after a sort.
        """
        try:
            return self._reminder_items.index(item)
        except ValueError:
            return -1  # Not found

    def toggle_item_flag(self, row_idx):
        reminder = self.get_reminder(row_idx)
        reminder.toggle_critical()
        self.save()  # Persist the change

    def save(self):
        # Now that you stored the manager, this works!
        self.data_manager.save(self._reminder_items)

#end CLASS ReminderDataModel
