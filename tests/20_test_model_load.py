import os
from reminders_persistence import RemindersManager

def test_load_basic():
    # Arrange
    csv_path = os.path.join("tests", "fixtures", "load_test.csv")

    # Act
    manager = RemindersManager(csv_path)
    reminders = manager.load_reminders()

    # Assert
    # TODO: assert structure, field values
    assert False  # replace with real checks
