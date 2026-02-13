from PySide6.QtCore import QStandardPaths
from pathlib import Path

def get_app_file_path(filename):
    """
    Get the path to the user's version of this application file.
    """
    config_dir = QStandardPaths.writableLocation(
        QStandardPaths.AppConfigLocation
    )
    path = Path(config_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path / filename

# Bullet proof atomic save
import os
import tempfile
def atomic_save(data_string, target_path, encoding='utf-8'):
    """
    Writes data to a temporary file in the same directory as
    target_path, then renames it to target_path atomically.
    """
    # Get the directory so the temp file stays on the same partition
    target_dir = os.path.dirname(os.path.abspath(target_path))

    # Create a unique temp file name to avoid collisions
    # e.g., reminders.csv.tmp_xyz123
    fd, temp_path = tempfile.mkstemp(dir=target_dir, suffix=".tmp")

    try:
        with os.fdopen(fd, 'w', encoding=encoding) as f:
            f.write(data_string)

        # Atomic swap
        os.replace(temp_path, target_path)
    except Exception as e:
        # Clean up if something went wrong before the swap
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e
