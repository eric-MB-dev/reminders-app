import sys

from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, QFontMetrics, QTextDocument
from PySide6.QtWidgets import QStyledItemDelegate

# noinspection PyPep8Naming
import table_constants as C
import sys, traceback

class LeftJustifiedDelegate(QStyledItemDelegate):
    """
    Determine row height and expand rows as needed, and
    """
    def sizeHint(self, option, index):
        text = index.data(Qt.DisplayRole) or ""
        
        # Qt sometimes passes width=0 during geometry calculation
        width = option.rect.width()
        if width <= 1:
            width = option.widget.columnWidth(index.column())
        
        doc = QTextDocument()
        doc.setDefaultFont(option.font)
        doc.setPlainText(text)
        doc.setTextWidth(width)
        height = int(doc.size().height()) - 6
        return QSize(width, height)
    
    # Bold the first line only for a critical-item reminder
    def paint(self, painter, option, index):
        
        # If not critical, fall back to normal painting
        is_critical = index.model().is_critical_row(index.row())
        if not is_critical:
            super().paint(painter, option, index)
            return
        
        if index.column() != C.DESCR_COL:
            # Not the description column, so no bolding logic
            super().paint(painter, option, index)
            return
        
        # Item is Critical: bold first line only ---
        text = index.data()
        if not text:
            super().paint(painter, option, index)
            return
        
        lines = text.split("\n")
        first = lines[0]
        rest = lines[1:]
        
        painter.save()
        
        # Base fonts
        bold_font = option.font
        bold_font.setBold(True)
        normal_font = QFont(option.font)
        normal_font.setBold(False)
        
        # Starting position
        x = option.rect.left()
        y = option.rect.top()
        
        # First line (bold)
        painter.setFont(bold_font)
        fm_bold = QFontMetrics(bold_font)
        painter.drawText(x, y + fm_bold.ascent(), first)
        y += fm_bold.height()
        
        # Remaining lines (normal)
        painter.setFont(normal_font)
        fm_norm = QFontMetrics(normal_font)
        for line in rest:
            painter.drawText(x, y + fm_norm.ascent(), line)
            y += fm_norm.height()
        
        painter.restore()
