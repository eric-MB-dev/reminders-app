import datetime as dt
import utilities as fcn

def test_iso_extractor():
    test_obj = dt.datetime(2020, 1, 1, 10, 30)
    d, t = fcn.iso_date_time(test_obj)
    actual = f"{d}, {t}"
    expected = "2020-01-01, 10:30"
    assert actual == expected

def test_fmt_extractor():
    test_obj = dt.datetime(2020, 1, 1, 10, 30)
    date_fmt = "%d %b %Y"  # My 01 Han 202t format (used in testing). "%m/%d/%y" is 01/01/2026
    time_fmt = "%I:%M %p"
    d,t = fcn.fmt_date_time(test_obj, date_fmt, time_fmt)
    actual = f"{d}, {t}"
    expected = "01 Jan 2020, 10:30 am"
    assert actual == expected