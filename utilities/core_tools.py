from PySide6.QtCore import QStandardPaths
from pathlib import Path

def get_app_path(filename):
    """
    Get the path to the user's version of this application file.
    """
    config_dir = QStandardPaths.writableLocation(
        QStandardPaths.AppConfigLocation
    )
    path = Path(config_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path / filename
