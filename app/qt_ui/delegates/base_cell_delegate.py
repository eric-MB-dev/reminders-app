from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QStyledItemDelegate

from typing import cast, TYPE_CHECKING
if TYPE_CHECKING:
    from qt_table_model_adapter import QtTableModelAdapter
from qt_table_model_adapter import v_alignment

class BaseCellDelegate(QStyledItemDelegate):
    # Default horizontal alignment
    h_alignment_bit = Qt.AlignmentFlag.AlignHCenter

    def __init__(self, parent=None):
        super().__init__(parent)

    def sizeHint(self, option, index):
        fm = option.fontMetrics
        #print("fm.height", fm.height())  # => 20
        h = fm.height() - 6
        return QSize(option.rect.width(), h)

    def initStyleOption(self, option, index):
        """This code runs on non-critical rows, because paint() doesn't change it"""
        super().initStyleOption(option, index)

        model = cast("QtTableModelAdapter", index.model())
        reminder = model.get_reminder(index.row())
        v_bit = v_alignment(reminder)
        option.displayAlignment = v_bit | self.h_alignment_bit
