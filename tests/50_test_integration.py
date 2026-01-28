import os
from reminders_persistence import RemindersManager

def test_roundtrip():
    # Arrange
    original = [
        # TODO: Reminder objects
    ]
    csv_path = os.path.join("tests", "temp", "roundtrip_output.csv")
    manager = RemindersManager(csv_path)

    # Act
    manager.save(original)
    loaded = manager.load()

    # Assert
    assert loaded == original
