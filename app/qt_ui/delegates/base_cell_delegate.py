from PySide6.QtCore import QSize
from PySide6.QtWidgets import QStyledItemDelegate

class BaseCellDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def sizeHint(self, option, index):
        fm = option.fontMetrics
        #print("fm.height", fm.height())  # => 20
        h = fm.height() - 6
        return QSize(option.rect.width(), h)
