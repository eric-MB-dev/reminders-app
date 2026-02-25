import datetime as dt
# "dt" module contains date, time, & datetime classes

import utilities as fcn

# noinspection PyPep8Naming
import table_constants as C

from app.config import config

class ReminderItem:
    # TODO: Add "alert_schedule" to the constructor argument
    def __init__(self, when:dt.datetime, descr, flags="", notes="", repeat=""):
        if when:
            assert isinstance(when, dt.datetime),\
                f"Reminder.when must be datetime, got {type(when)}: {when}"
        if repeat:
            # ToDo: decode repetition data?
            pass

        # ToDo: Take muted/active state as an init argument

        self._when: datetime = when  # date & time
        self._descr = descr          # main reminder descr
        self._flags = flags          # "". "!" (C.IS_CRTICAL_FLAG), "A' (alerts enabled), or !A
        self._notes = notes          # optional notes (location, what to bring, etc)
        self._alert_sched = None     # TODO: Store and read back actual alert-schedule
        self._repeat_sched: str = "" # TODO: Display in table as "Daily", "Weekly", "Custom", etc.

        self._faux_date_str = ""     # Date-override Used by countdown for imminent dates
        self._countdown_str = ""     # Time remaining until the event or activity
    #end __init__

    def __eq__(self, other):
        """ Comparison operator for use in unit tests"""
        if not isinstance(other, ReminderItem):
            return False

        # Return True if all relevant fields match
        return (self._when == other._when and
                self._descr == other._descr and
                self._flags == other._flags and
                self._notes == other._notes and
                self._alert_sched == other._alert_sched and
                self._repeat_sched == other._repeat_sched)

    @property
    def is_critical(self):
        return C.IS_CRITICAL_FLAG in self._flags

    @property
    def alerts_enabled(self):
        return C.ALERTS_ENABLED_FLAG in self._flags

    @alerts_enabled.setter
    def alerts_enabled(self, value: bool):
        # Remove it first to avoid duplicates like "AA"
        self._flags = self._flags.replace(C.ALERTS_ENABLED_FLAG, "")
        if value:
            self._flags += C.ALERTS_ENABLED_FLAG
        self._order_the_flags()

    def _order_the_flags(self):
        """Normalizes the string to a predictable '!A' format."""
        # 1. Check current state via substring search
        critical = C.IS_CRITICAL_FLAG in self._flags
        alerts = C.ALERTS_ENABLED_FLAG in self._flags

        # 2. Rebuild from scratch in the 'Correct' order
        new_str = ""
        if critical: new_str += C.IS_CRITICAL_FLAG
        if alerts:   new_str += C.ALERTS_ENABLED_FLAG

        self._flags = new_str

    @property
    def alert_sched(self):
        if self._alert_sched == None:
            return ""
        # ToDO: Temporary. Replace with decoded-schedule object (or string)
        return ""

    @alert_sched.setter
    def alert_sched(self, value: str):
        self._alert_sched = value

    def toggle_critical(self):
        if self.is_critical:
            self._flags = self._flags.replace(C.IS_CRITICAL_FLAG, "")
        else:
            self._flags += C.IS_CRITICAL_FLAG
        self._order_the_flags()

    @property
    def has_notes(self):
        return bool(self._notes)

    @property
    def repeats(self):
        # ToDO: Return simplified string: "Daily", "Weekly", "Monthly", Yearly", or "Custom"
        if not self._repeat_sched:
            return ""
        return ""

    def set_repeat_sched(self, value: str):
        #TODO: Decode JSON repeat string
        self._repeat_sched = value

    @property
    def day_of_week(self):
        # Derived field, not stored in CSV
        if not self._when:
            return ""
        return self._when.date().strftime("%a")

    @property
    def descr(self):
        # Combine descr and notes for UI
        if self._notes:
            return f"{self._descr}\n{self._notes}"
        return self._descr

    @property
    def date(self):
        if not self._when:
            return ""

        if self._faux_date_str:
            return self._faux_date_str

        d = self._when.date()
        date_fmt = config.date_display_format
        return d.strftime(date_fmt).lstrip("0")

    @property
    def time(self):
        if not self._when:
            return ""

        t = self._when.time()
        if t.hour == 0 and t.minute == 0:
            time_str = ""
        else:
            # Time with no leading zero, Lowercase "am/pm". So: 6:00 am)"""
            time_fmt = config.time_display_format
            time_str = t.strftime(time_fmt).lstrip("0").lower()
        return time_str


    #TODO: Implement repeats, plus encoding & decoding for serilaization
    #  in JSON format: {"type":"weekly","interval":1,"weekday":"Mon"}
    #  where type->Display column, interval 1 = "every week".

    def to_csv_row(self):
        """Convert to a list of strings for csv writer"""
        # csv col headers defined in table_constants: [Title,Date,Time,Flag,Notes,Repeat]
        date_str, time_str = fcn.iso_date_time(self._when)
        notes_str = fcn.encode_newlines(self._notes)  # Escape NLs
        repeat_str = self._repeat_sched  # TODO: ENCODE JSON REPETITION (display value for now)
        return [self._descr, date_str, time_str, self._flags, notes_str, repeat_str]

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
            #Decode JSON repeat string
            self.set_repeat_sched(repeat)

        # ReminderItem init: when:dt.datetime, descr, flag, notes, repeat
        return cls(when, descr, flag, notes, repeat)
        
    # The value to use for sorting (date/time)
    def sort_key(self):
        # False (0) comes before True (1)
        # Put items where 'when' is None at the top
        # (when it exists, sort on the 'when' value)
        return self._when is not None, self._when

    @property
    def countdown(self):
        return self._countdown_str

    @property
    def has_time(self):
        # If the time is exactly 00:00:00, we treat it as a Date-only event
        t = self._when.time()
        return not (t.hour == 0 and t.minute == 0 and t.second == 0)

    def update_countdown(self, now):
        if not now or self._when is None:
            self._countdown_str = ""
            self._faux_date_str = ""
            return

        current_date = now.date()
        target_date = self._when.date()
        delta = target_date - current_date
        days = delta.days

        # --- Days Ahead ---
        if days > 1:
            self._countdown_str = f"in {fcn.pluralize(days, 'day')}"
            self._faux_date_str = ""  # Standard date display
            return
        elif days == 1:
            self._countdown_str = "in 1 day"
            self._faux_date_str = "TOMORROW"
            return

        # --- Past Activity/Event ---
        if days < 0:
            self._countdown_str = "Past"
            self._faux_date_str = ""
            return

        # --- TODAY (days == 0) ---
        self._faux_date_str = "TODAY"
        today_delta = self._when - now
        seconds = int(today_delta.total_seconds()) # Always a float, unless we fix it.

        # --- Calculate 15 min boundaries ---
        raw_minutes = seconds // 60  # Total minutes remaining
        #
        # SNAP to the nearest 15 (The "v1.1"
        # This ensures 58m -> 60m (1 hr) and 1hr 7m -> 1hr (1 hr)
        snapped_total = (raw_minutes // 15) * 15
        #
        # Derive hours & minutes from the snapped total
        hours = snapped_total // 60
        minutes = snapped_total % 60

        # Past-due today
        if seconds < 0 and self.has_time:
            if seconds > -3600:
                # Within the past hour
                self._countdown_str = "LATE"
            else:
                self._countdown_str = "Over"
            return
        
        # Right now
        minutes = seconds // 60
        if minutes == 0:
            self._countdown_str = "NOW"
            return

        # Later Today
        if hours >= 2:
            self._countdown_str = f"in {fcn.pluralize(hours, 'hour')}"
        elif hours == 1:
            if minutes == 0:
                self._countdown_str = "in 1 hour"
            else:
                # "in 1 hour, 15 min", "in 1 hour, 30 min", etc.
                self._countdown_str = f"in 1 hour, {minutes} min"

        elif minutes > 15:
            self._countdown_str = f"in {minutes} minutes"

        else:
            # 10m & 5m reminders
            self._countdown_str = f"in {fcn.pluralize(minutes, 'minute')}"

        return
    #end update_countdown()

#end CLASS Reminder