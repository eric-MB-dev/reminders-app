# wx_ui/formatting.py

"""
Foramating FCNs for UI-display
"""

def format_text(text):
    """Return the short text field exactly as it should appear in the grid."""
    return text.strip()


def format_notes(notes):
    """Return notes in a UI-friendly form (single-line or truncated)."""
    return notes.strip()


def combine_text_and_notes(text, notes):
    """Return a combined preview for the grid."""
    if notes:
        return f"{text} — {notes}"
    return text


def format_day_of_week(dt):
    """Return something like 'Tue' or 'Tuesday'."""
    return dt.strftime("%a")   # or "%A" for full name


def formatted_date_time(dt):
    """Return (date_str, time_str) using config-defined formats."""
    from app.config import config
    date_fmt = config.date_display_format
    time_fmt = config.time_display_format
    return dt.strftime(date_fmt), dt.strftime(time_fmt)


def reminders_to_display_rows(reminder):
    """Return a list of strings for each column in the grid."""
    date_str, time_str = formatted_date_time(reminder._when)
    
    return [
        combine_text_and_notes(reminder.text, reminder.notes),
        format_day_of_week(reminder._when),
        date_str,
        time_str,
    ]
