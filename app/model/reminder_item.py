import datetime as dt
# "dt" module contains date, time, & datetime classes

import utilities as fcn

class ReminderItem:
    def __init__(self, when:dt.datetime, text, flag="", repeat="", notes=""):
        self.when = when          # date & time
        self.text = text          # main reminder text
        self.flag = flag          # "!" (important) or ""
        self.repeat = repeat      # optional repetition setting
        self.notes = notes        # optional notes/location
        
        if when:
            assert isinstance(when, dt.datetime), f"Reminder.when must be datetime, got {type(when)}: {when}"
    
    @property
    def day_of_week(self):
        # Derived field, not stored in CSV
        if self.when:
            return self.when.date().strftime("%a")
        return ""
    
    @property
    def display_text(self):
        # combine text and notes for UI
        if self.notes:
            return f"{self.text}\n{self.notes}"
        return self.text
    
    def to_display_row(self):
        """Time with no leading zero, Lowercase "am/pm". So: 6:00 am)"""
        import config
        date_str = ""
        time_str = ""
        if self.when:
            date_str = self.when.date().strftime(config.date_display_format)
            t = self.when.time()
            if t.hour == 0 and t.minute == 0:
                time_str = ""
            else:
                time_str = t.strftime(config.time_display_format).lstrip("0").lower()
        return [
            self.flag,
            self.display_text,
            self.day_of_week,
            date_str,
            time_str,
            self.countdown()
        ]

    #TODO: Implement repeats, plus encoding & decoding for serilaization
    #  in JSON format: {"type":"weekly","interval":1,"weekday":"Mon"}
    #  where type->Display column, interval 1 = "every week".

    def to_csv_row(self):
        """Convert to a list of strings for csv writer"""
        # csv col headers defined in table_constants: [Title,Date,Time,Flag,Notes,Repeat]
        notes = fcn.encode_newlines(self.notes)  # Escape NLs
        repeat = ""
        return [self.text, self.when.date.isoformat(), self.when.time.isoformat(),
                self.flag, self.notes, self.repeat]

    @classmethod
    def from_csv_row(cls, row):
        # Stored row from a csv file to a Reminder object
        # csv row = [Title,Date,Time,Repeat,Notes]
        text = row[0]
        date_obj = dt.date.fromisoformat(row[1]) if row[1] else None
        time_obj = dt.time.fromisoformat(row[2]) if row[2] else None
        
        # Convert to a datetime object for sorting
        when = fcn.datetime_from_date_and_time(date_obj, time_obj)
        
        # when = dt.datetime.combine(date_obj, time_obj)
        repeat = row[3]  # TODO: REVERSE 3 & 4
        notes = row[4] if len(row) > 4 else ""
        if notes:
            notes = fcn.decode_newlines(notes)     # Un-escape NLs
        # CSV row = [when:dt.datetime, text, repeat, notes]
        return cls(when, text, repeat, notes)
        
    # The value to use for sorting (date/time)
    def sort_key(self):
        return self.when

    def countdown(self):
        if not self.when:
            return ""
        
        now = dt.datetime.now()
        delta = self.when - now
        
        # Past
        days = delta.days
        if days < 0:
            return 'Past'

        seconds = delta.total_seconds()
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
        # TODO 1/2: Replace DATE field with these
        '''
        elif days == 0 :
            return "TODAY"
        elif days == 1 :
            return "TOMORROW"
        '''
        # Tomorrow
        if days == 1:
            # TODO 2/2: Change this to an empty string
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