import qtawesome as qta
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QSize

class ReminderButton(QPushButton):
    def __init__(self, icon_name, color="gray", parent=None):
        super().__init__(parent)
        # 1. Look and Feel
        self.setFixedSize(30, 30)
        self.setIconSize(QSize(24, 24))
        #self.setFlat(True)  # Removes the "button box" for a cleaner look

        # 2. Set the Icon (using QtAwesome for that tapered trashcan/bell)
        self.setIcon(qta.icon(icon_name, color=color))

class TrashButton(ReminderButton):
    def __init__(self, parent=None):
        super().__init__('fa5s.trash', color="darkred", parent=parent)
        self.setToolTip("Delete Reminder")
