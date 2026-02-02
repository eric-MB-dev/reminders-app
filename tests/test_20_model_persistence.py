import os
from pathlib import Path

TEST_DIR = Path(__file__).parent
TEMP_DIR = TEST_DIR / "temp"
csv_test_path = TEMP_DIR / "save_test.csv"

from tests.fixtures.reminder_factory import sample_reminders, sample_csv_text
from reminders_persistence import RemindersPersistence

def test_save():
    if os.path.exists(csv_test_path):
        # Clean out old data, if any
        os.remove(csv_test_path)

    reminders = sample_reminders()
    manager = RemindersPersistence(csv_test_path)  # Initialize an empty file w/ "Add entries"
    manager.save(reminders)   # Overwrite the file?

    with open(csv_test_path, "r", encoding="utf-8") as f:
        actual = f.read().strip()

    expected = sample_csv_text().strip()
    #print(f"ACTUAL:   {repr(actual)}")
    #print(f"EXPECTED: {repr(expected)}")
    assert actual == expected

# RESULTS OF THIS TEST ARE VALID ONLY IF THE SAVE TEST SUCCEEDS
def test_load():
    manager = RemindersPersistence(csv_test_path)
    actual = manager.load()
    expected = sample_reminders()

    # Ensure they are at least the same length first
    assert len(actual) == len(expected), f"Length mismatch: {len(actual)} vs {len(expected)}"

    # Zip pairs them up: (actual[0], expected[0]), (actual[1], expected[1])...
    for i, (a, e) in enumerate(zip(actual, expected)):
        # This will tell you EXACTLY which index and which field failed
        assert a == e, f"Mismatch at index {i}!\nActual: {repr(act)}\nExpected: {repr(exp)}"
