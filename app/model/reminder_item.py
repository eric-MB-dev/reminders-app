import datetime as dt
# "dt" module contains date, time, & datetime classes

import utilities as fcn

# noinspection PyPep8Naming
import table_constants as C

from app.config import config

class ReminderItem:
    def __init__(self, when:dt.datetime, descr, flag="", notes="", repeat=""):
        if when:
            assert isinstance(when, dt.datetime),\
                f"Reminder.when must be datetime, got {type(when)}: {when}"
        if repeat:
            # ToDo: decode repetition data?
            pass

        # ToDo: Take muted/active state as an init argument

        self.when: datetime = when  # date & time
        self.descr = descr          # main reminder descr
        self.flag = flag            # "" or "!" (C.IS_CRTICAL_FLAG)
        self.notes = notes          # optional notes/location
        self.repeat = repeat        # optional repetition setting
        self.alerts: bool = True         # The "Opposite" of muted
        self.repeat: str = None          # e.g., "Daily", "Weekly", or Non
    #end __init__

    def __eq__(self, other):
        """ Comparison operator for use in unit tests"""
        if not isinstance(other, ReminderItem):
            return False

        # Return True if all relevant fields match
        return (self.when == other.when and
                self.descr == other.descr and
                self.flag == other.flag and
                self.notes == other.notes and
                self.repeat == other.repeat)

    @property
    def is_critical(self):
        return self.flag == C.IS_CRITICAL_FLAG

    @property
    def has_notes(self):
        return bool(self.notes)

    @property
    def day_of_week(self):
        # Derived field, not stored in CSV
        if not self.when:
            return ""
        return self.when.date().strftime("%a")

    @property
    def display_text(self):
        # combine descr and notes for UI
        if self.notes:
            return f"{self.descr}\n{self.notes}"
        return self.descr

    @property
    def date(self):
        if not self.when:
            return ""

        d = self.when.date()
        date_fmt = config.date_display_format
        return d.strftime(date_fmt)

    @property
    def time(self):
        if not self.when:
            return ""

        t = self.when.time()
        if t.hour == 0 and t.minute == 0:
            time_str = ""
        else:
            # Time with no leading zero, Lowercase "am/pm". So: 6:00 am)"""
            time_fmt = config.time_display_format
            time_str = t.strftime(time_fmt).lstrip("0").lower()
        return time_str

    def toggle_item_flag(self, index):
        item = self.reminders[index]
        item.is_critical = not item.is_critical  # Flip the actual object
        self.auto_save()  # Handle persistence immediately

    def to_display_row(self):
        #Time with no leading zero, Lowercase "am/pm". So: 6:00 am)"""
        #from app.config import config
        #date_fmt = config.date_display_format
        #time_fmt = config.time_display_format
        #date_str, time_str = fcn.fmt_date_time(self.when, date_fmt, time_fmt)
        '''
        if self.when:
            date_str = self.when.date().strftime()
            t = self.when.time()
            if t.hour == 0 and t.minute == 0:
                time_str = ""
            else:
                time_str = t.strftime(config.time_display_format).lstrip("0").lower()
        '''
        return [
            self.flag,
            self.display_text,
            self.day_of_week,
            self.date,
            self.time,
            self.repeat,
            self.countdown,
        ]
    
    #TODO: Implement repeats, plus encoding & decoding for serilaization
    #  in JSON format: {"type":"weekly","interval":1,"weekday":"Mon"}
    #  where type->Display column, interval 1 = "every week".

    def to_csv_row(self):
        """Convert to a list of strings for csv writer"""
        # csv col headers defined in table_constants: [Title,Date,Time,Flag,Notes,Repeat]
        date_str, time_str = fcn.iso_date_time(self.when)
        notes_str = fcn.encode_newlines(self.notes)  # Escape NLs
        repeat_str = self.repeat  # TODO: ENCODE REPETITION (it's the display value for now)
        return [self.descr, date_str, time_str, self.flag, notes_str, repeat_str]

    @classmethod
    def from_csv_row(cls, row):
        # Stored row from a csv file to a Reminder object
        # csv row = [Title,Date,Time,Flag,Notes,Repeat]
        descr = row[0]
        date_obj = dt.date.fromisoformat(row[1]) if row[1] else None
        time_obj = dt.time.fromisoformat(row[2]) if row[2] else None
        
        # Convert to a datetime object for sorting
        when = fcn.datetime_from_date_and_time(date_obj, time_obj)
        flag = row[3]
        notes = row[4] if len(row) > 4 else ""
        if notes:
            notes = fcn.decode_newlines(notes)     # Un-escape NLs
        repeat = row[5] if len(row) > 5 else ""
        if repeat:
            #TODO: Decode JSON repeat string
            pass

        # ReminderItem init: when:dt.datetime, descr, flag, notes, repeat
        return cls(when, descr, flag, notes, repeat)
        
    # The value to use for sorting (date/time)
    def sort_key(self):
        # False (0) comes before True (1)
        # Put items where 'when' is None at the top
        # (when it exists, sort on the 'when' value)
        return self.when is not None, self.when

    @property
    def countdown(self):
        if not self.when:
            return ""

        delta = self.when.date() - dt.date.today()
        days = delta.days

        # today_delta includes Minutes & hours
        now = dt.datetime.now()
        today_delta = self.when - now
        
        # Past
        if days < 0:
            return 'Past'

        seconds = today_delta.total_seconds()
        if seconds < 0:
            if seconds > -3600:
                # Within the past hour
                countdown = "LATE"
            else:
                countdown = "Over"
            return countdown
        
        # Right now
        minutes = seconds / 60
        if minutes == 0:
            return "NOW"
        
        # Today, or tomorrow
        # TODO: Replace DATE field with these? & return countdown = ""
        '''
        elif days == 0 :
            return "TODAY"
        elif days == 1 :
            return "TOMORROW"
        '''
        # Tomorrow
        #print(f"Delta: {delta}, delta.days: {delta.days}")
        #print(f"Today: {dt.date.today()}, Item date: {self.when.date()}")
        #print(f"Days: {days}")
        if days == 1:
            return "TOMORROW"
        
        # Today
        if days == 0:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            
            if minutes == 0:
                return "NOW"
            if hours >= 2:
                return f"in {fcn.pluralize(hours, 'hour')}"
            if hours >= 1:
                return f"in {fcn.pluralize(hours, 'hour')}, {minutes} min"
            return f"in {fcn.pluralize(minutes, 'minute')}"
        
        # Coming up
        return f"in {fcn.pluralize(days, 'day')}"
    
#end CLASS Reminder