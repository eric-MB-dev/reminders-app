from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QStyledItemDelegate

from .base_cell_delegate import BaseCellDelegate

class CenteredDelegate(BaseCellDelegate):
    """
    Centering delegate for data columns (& buttons?)
    Usage:
        table.setItemDelegateForColumn(col, CenteredDelegate())
    """
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter

