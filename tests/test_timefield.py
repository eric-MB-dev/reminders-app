import pytest
import tkinter as tk

#import math, threading, time, datetime
#import utils as fcn

@pytest.fixture
def tf():
    root = tk.Tk()
    widget = TimeField(root)
    yield widget
    root.destroy()

def test_empty_initial_state(tf):
    assert tf.get_time_string() == ""
    assert tf.get_time_24h() == ""

def test_set_time_24h(tf):
    tf.set_time("14:30")
    assert tf.get_time_string() == "02:30 PM"
    assert tf.get_time_24h() == "14:30"

def test_set_time_12h(tf):
    tf.set_time("02:30 PM")
    assert tf.get_time_string() == "02:30 PM"
    assert tf.get_time_24h() == "14:30"

def test_midnight_and_noon(tf):
    tf.set_time("00:15")
    assert tf.get_time_string() == "12:15 AM"
    assert tf.get_time_24h() == "00:15"

    tf.set_time("12:00 PM")
    assert tf.get_time_24h() == "12:00"

def test_manual_entry(tf):
    tf.time_var.set("9:45 pm")
    assert tf.get_time_24h() == "21:45"
