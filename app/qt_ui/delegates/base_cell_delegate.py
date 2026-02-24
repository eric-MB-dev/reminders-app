from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import QStyledItemDelegate

from typing import cast, TYPE_CHECKING
if TYPE_CHECKING:
    from model_adapter import ModelAdapter
from model_adapter import v_alignment

class BaseCellDelegate(QStyledItemDelegate):
    # Default horizontal alignment
    h_alignment_bit = Qt.AlignmentFlag.AlignHCenter

    def __init__(self, parent=None):
        super().__init__(parent)

    def sizeHint(self, option, index):
        # Get the standard metrics
        fm = option.fontMetrics

        # Check if the row is critical (Needs Bold space)
        reminder = index.model().get_reminder(index.row())
        if reminder and reminder.is_critical:
            bold_font = QFont(option.font)
            bold_font.setBold(True)
            fm = QFontMetrics(bold_font)  # Use the wider bold metrics

        # Calculate width based on the actual text content
        text = str(index.data() or "")
        # horizontalAdvance measures the pixels the text actually takes up
        width = fm.horizontalAdvance(text) + 10  # 10px for cell padding

        # Keep row heights minimal
        # (Qt ignores it for single-line rows, but it works great for multi-lines
        h = fm.height() - 6

        return QSize(width, h)

    def initStyleOption(self, option, index):
        """This code runs on non-critical rows, because paint() doesn't change it"""
        super().initStyleOption(option, index)

        # Get the font from the Model
        font = index.data(Qt.FontRole)
        if font:
            option.font = font
        if font and font.bold():
            print(f"Delegate saw BOLD for Row {index.row()} Col {index.column()}")

        model = cast("ModelAdapter", index.model())
        reminder = model.get_reminder(index.row())
        v_bit = v_alignment(reminder)
        option.displayAlignment = v_bit | self.h_alignment_bit
