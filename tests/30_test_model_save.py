import os
from reminders_persistence import RemindersManager

def test_save_structure():
    # Arrange
    reminders = [
        # TODO: insert Reminder objects
    ]
    csv_path = os.path.join("tests", "temp", "save_test.csv")

    manager = RemindersManager(csv_path)

    # Act
    manager.save(reminders)

    # Assert
    with open(csv_path, "r", encoding="utf-8") as f:
        text = f.read()

    expected = """\
        # TODO: expected CSV text here
        """
    assert text == expected
