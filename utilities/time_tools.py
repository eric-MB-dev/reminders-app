import datetime as dt

# Formatting helper, used in Main.setup_display, to get truncated time
def get_now_in_mins():
    return dt.datetime.now().replace(second=0, microsecond=0)

def iso_date_time(datetime_obj):
    """
    Return iso-format date & time strings from a datetime object.
    """
    date_str = ""
    time_str = ""
    if datetime_obj:
        date_str = datetime_obj.date().isoformat()

        t: dt.time = datetime_obj.time()
        if t.hour == 0 and t.minute == 0:
            time_str = ""
        else:
            time_str = t.isoformat(timespec='minutes')

    return date_str, time_str

def fmt_date_time(datetime_obj, date_format, time_format):
    """
    Return date & time strings in the designated formats from a datetime object.
    """
    date_str = ""
    time_str = ""
    if datetime_obj:
        d: dt.date = datetime_obj.date()
        if date_format:
            date_str = d.strftime(date_format)

        t: dt.time = datetime_obj.time()
        if t.hour == 0 and t.minute == 0:
            time_str = ""
        elif time_format:
            time_str = t.strftime(time_format).lstrip("0").lower()

    return date_str, time_str

def datetime_from_date_and_time(date_obj, time_obj):
    """
    Return the combination of date & time, or date at midnight, time + current date, or None
    """
    assert date_obj is None or isinstance(date_obj, dt.date)
    assert time_obj is None or isinstance(time_obj, dt.time)
    
    # Combine the objects
    if date_obj and time_obj:
        return dt.datetime.combine(date_obj, time_obj)
    
    if date_obj:
        return dt.datetime.combine(date_obj, dt.time(0, 0))
    
    if time_obj:
        # Date defaults to today
        return dt.datetime.combine(dt.date.today(), time_obj)
    
    return None

class Moment:
    """
    Wrapper class for semi-nutsoid datetime module that contains
    datetime (truly!), as well as date, and time---a C module that only
    handles times, so you have to use strfTIME to det DAY from a date.
    
    TODO Eventual goal:
      Replace every datetime reference in the project with
      a more sane, more usable object like (maybe) this Moment class.
    """
    def __init__(self, when: dt.datetime):
        self.when = when

    @property
    def day_of_week(self):
        return self.when.strftime("%a")

    @property
    def date(self):
        return self.when.date()

    @property
    def time(self):
        return self.when.time()

    def format(self, fmt):
        return self.when.strftime(fmt)

    def __sub__(self, other):
        return self.when - other.when if isinstance(other, Moment) else self.when - other
