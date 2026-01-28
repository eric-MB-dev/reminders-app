# ---------------
# Data Structures
# ---------------

def sample_reminders():
    """List of Reminder objects from strings with iso-format dates & times"""
    return [
        make_reminder_from_args("Wake up", "2025-01-01", "06:00", "Daily", "Be grateful!"),
        make_reminder_from_args("Meditate", "2025-01-01", "06:30", "Daily", "Good fer ya!"),
    ]


def sample_display_rows():
    """List of text strings displayed in the reminder grid"""
    return [
        ["Wake up\nBe grateful!",  "Wed", "01 Jan 2025", "6:00 am", "Past"],
        ["Meditate\nGood fer ya!", "Wed", "01 Jan 2025", "6:30 am", "Past"],
    ]


def sample_csv_text():
    """Text values stored in the CSV file"""
    return """Title,Date,Time,Repeat,Notes
Wake up,2025-01-01,06:00,Daily,Be grateful!
Meditate,2025-01-01,06:30,Daily,Good fer ya!
"""

# --------------
# Helper fcns
# --------------

# Make a Reminder instance
def make_reminder_from_args(title, date_str, time_str, repeat, notes):
    import datetime as dt
    from reminder_item import ReminderItem
   
    date_obj = dt.date.fromisoformat(date_str)
    time_obj = dt.time.fromisoformat(time_str)
    when = dt.datetime.combine(date_obj, time_obj)

    return ReminderItem(when, title, repeat, notes)

# TODO determine: Is this ever used?
def make_reminder_from_row(row):
    title, date_str, time_str, repeat, notes = row
    return make_reminder_from_args(title, date_str, time_str, repeat, notes)

def make_two_reminders():
    rows = sample_display_rows()
    return reminders_from_display_rows(rows)

def reminders_from_display_rows(rows):
    import datetime as dt
    import utils as fcn
    from reminder_item import ReminderItem
    
    reminders = []
    for text, date_str, time_str, repeat, notes in rows:
        date_obj = dt.date.fromisoformat(date_str) if date_str else None
        time_obj = dt.time.fromisoformat(time_str) if time_str else None
        when = fcn.datetime_from_date_and_time(date_obj, time_obj)
        reminders.append(ReminderItem(when, text, notes, repeat))
    return reminders


