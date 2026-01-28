from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QStyledItemDelegate
from .base_cell_delegate import BaseCellDelegate

class NextButtonDelegate(BaseCellDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.icon = QIcon(":/icons/edit.png")
        #self.icon = "→" # unicode glyph

