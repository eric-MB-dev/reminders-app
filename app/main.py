# main.py
import sys
from PySide6.QtWidgets import QApplication

import app.config as config

from app.qt_ui.reminders_window       import RemindersWindow
from app.qt_ui.qt_table_model_adapter import QtTableModelAdapter
from app.reminders_persistence        import RemindersPersistence
from app.model.reminders_model        import RemindersModel

# noinspection PyPep8Naming
import table_constants as C

USE_MOCK_DATA = True  # TODO: Set to False for production version

def main():
    """
    Confguration sequence:
    RemindersPersistence → RemindersModel → RemindersTableModel → RemindersWindow
    """
    if USE_MOCK_DATA:
        from tests.fixtures.mock_reminders import mock_reminders
        mock_data = C.INITIAL_DATA + mock_reminders
        domain_model = RemindersModel(reminder_list=mock_reminders)
    else:
        manager = RemindersPersistence(config.curr_csv_path)
        domain_model = RemindersModel(data_manager=manager)
    from PySide6.QtCore import QCoreApplication

    from PySide6.QtCore import QCoreApplication
    QCoreApplication.setOrganizationName("MeditateBetter")
    QCoreApplication.setApplicationName("ReminderSystem")

    app = QApplication(sys.argv)
    rtm = QtTableModelAdapter(domain_model)
    window = RemindersWindow(rtm)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

# TODO FOR PRODUCTION: Invoke at startup
# FUTURE (maybe):
#   When multiple reminder files exist, log into the active reminder-list folder.
def setup_logging(self):
    """
     Usage:
        logging.info("Something happened")
        logging.error("Something failed")
    """
    import logging
    logging.basicConfig(
        filename="reminder.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )
