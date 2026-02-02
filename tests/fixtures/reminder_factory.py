# ---------------
# Data Structures
# ---------------

def sample_reminders():
    """List of Reminder objects from strings with iso-format dates & times"""
    return [
        make_reminder_from_args("", "Wake up", "2025-01-01", "06:00", "Be grateful!", "Daily"),
        make_reminder_from_args("!","Meditate", "2025-01-01", "06:30", "Good fer ya!", "Daily"),
    ]


def sample_display_rows():
    """List of text strings displayed in the reminder window"""
    return [
        ['', "Wake up\nBe grateful!",  "Wed", "01 Jan 2025", "6:00 am", "Daily", "Past"],
        ['!', "Meditate\nGood fer ya!", "Wed", "01 Jan 2025", "6:30 am", "Daily", "Past"],
    ]


def sample_csv_text():
    """Text values stored in the CSV file (empty line at the end)"""
    return """Title,Date,Time,Flag,Notes,Repeat
Wake up,2025-01-01,06:00,,Be grateful!,Daily
Meditate,2025-01-01,06:30,!,Good fer ya!,Daily
"""

# --------------
# Helper fcns
# --------------

# Make a Reminder instance
def make_reminder_from_args(flag, title, date_str, time_str, notes, repeat):
    import datetime as dt
    from reminder_item import ReminderItem
   
    date_obj = dt.date.fromisoformat(date_str)
    time_obj = dt.time.fromisoformat(time_str)
    when = dt.datetime.combine(date_obj, time_obj)

    return ReminderItem(when, title, flag, notes, repeat)

# TODO determine: Is this ever used?
def make_reminder_from_row(row):
    flag, title, date_str, time_str, repeat, notes = row
    return make_reminder_from_args(flag, title, date_str, time_str, notes, repeat)

def make_two_reminders():
    rows = sample_display_rows()
    return reminders_from_display_rows(rows)

def reminders_from_display_rows(rows):
    import datetime as dt
    import utilities as fcn
    from reminder_item import ReminderItem
    
    reminders = []
    for flag, text, date_str, time_str, notes, repeat in rows:
        date_obj = dt.date.fromisoformat(date_str) if date_str else None
        time_obj = dt.time.fromisoformat(time_str) if time_str else None
        when = fcn.datetime_from_date_and_time(date_obj, time_obj)
        reminders.append(ReminderItem(when, text, notes, repeat))
    return reminders


