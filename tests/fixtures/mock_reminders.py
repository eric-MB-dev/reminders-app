# tests/fixtures/mock_reminders.py
"""
Data rows for UI testing (manual, and viewModel unit tests
"""
import datetime as dt
import utilities as fcn
from reminder_item import ReminderItem

test_data = [  # Flag, title, date_str, time_str, notes, repeat
    [ "", "Simple reminder", "2027-01-01", "09:00", "", "" ],
    [ "", "A rather long reminder with a lot of text in it", "2027-01-02", "10:30", "", "..." ],
    [ "", "Event with location note", "2027-01-04", "22:00", "At Ginny's house", "(10 pm)" ],
    [ "!", "Music w/ Gabie", "2026-02-01", "11:30", "", ""],
    [ "", "Vinyasa flow yoga", "2026-02-04", "12:45", "mountainview.gov/Seniors\nComm. ctr for now", "Weekly" ],
]

mock_reminders = []
for row in test_data:
    flag, title, date_str, time_str, notes, repeat = row
    when = fcn.datetime_from_date_and_time(date_obj, time_obj)
    date_obj = dt.date.fromisoformat(date_str) if date_str else None
    time_obj = dt.time.fromisoformat(time_str) if time_str else None
    mock_reminders.append(ReminderItem(when, title, flag, notes, repeat))

