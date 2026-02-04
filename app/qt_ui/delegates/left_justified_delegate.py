import sys

from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, QFontMetrics, QTextDocument
from PySide6.QtWidgets import QStyledItemDelegate

# noinspection PyPep8Naming
import table_constants as C
#import sys, traceback

from typing import cast, TYPE_CHECKING
if TYPE_CHECKING:
    from qt_table_model_adapter import QtTableModelAdapter

class LeftJustifiedDelegate(QStyledItemDelegate):
    """
    Determine row height and expand rows as needed, and
    """
    def __init__(self, parent_table):
        super().__init__(parent_table)
        self.parent_table = parent_table # Now we can talk to the table!

    def initStyleOption(self, option, index):
        """This code runs on non-critical rows, because paint() doesn't change it"""
        super().initStyleOption(option, index)
        from qt_table_model_adapter import QtTableModelAdapter
        model = cast("QtTableModelAdapter", index.model())
        vert_align = model.v_alignment_for(index.row(), index.column())
        option.displayAlignment = vert_align | Qt.AlignmentFlag.AlignLeft

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
        # --- INSTRUMENTATION ---
        actual_row_h = self.parent_table.rowHeight(index.row())
        rect_h = option.rect.height()

        # Only log if there's a mismatch or if the row is 'tall'
        #if rect_h != actual_row_h or rect_h > 100:
        #    print(f"[DEBUG] Paint Row {index.row()}:")
        #    print(f"  > Actual Row Height: {actual_row_h}")
        #    print(f"  > Option Rect Height: {rect_h}")
        #    print(f"  > State: {option.state}")  # Tells us if it's hovered, active, etc.
        # ------------------------

        # If not flagged as critical, paint normally within the cell's max-height rectangle
        is_critical = index.model().is_critical(index.row())
        if not is_critical:
            painter.save()
            painter.setClipRect(option.rect)  # The magic wall
            super().paint(painter, option, index)
            painter.restore()
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
        remainder = lines[1:]
        
        painter.save()

        # Fonts & metrics
        bold_font = option.font
        bold_font.setBold(True)
        normal_font = QFont(option.font)
        normal_font.setBold(False)

        fm_bold = QFontMetrics(bold_font)
        fm_norm = QFontMetrics(normal_font)

        # Compute total text height
        total_height = fm_bold.height() + len(remainder) * fm_norm.height()

        # Determine vertical alignment
        from qt_table_model_adapter import QtTableModelAdapter
        model = cast("QtTableModelAdapter", index.model())
        vert_align = model.v_alignment_for(index.row(), index.column())

        # Qtable refuses to adjust it's minimum row size below 28px or so.
        # So we resort to code like this to center single-line rows in the
        # overly-tall rows. (Multi-line rows work beautifully.)
        if vert_align & Qt.AlignmentFlag.AlignVCenter:
            # Single-line row (no note, centered)
            y = option.rect.top() + (option.rect.height() - fm_bold.height()) // 2
        else:
            # Multi-line row start at top left of cell
            y = option.rect.top()

        # Starting x
        x = option.rect.left()

        # Draw first (bold) line
        painter.setFont(bold_font)
        painter.drawText(x, y + fm_bold.ascent(), first)
        y += fm_bold.height()

        # Draw remaining lines in maximum-size cell rectangle
        actual_row_h = self.parent_table.rowHeight(index.row())
        cell_limit = option.rect.top() + actual_row_h

        painter.setFont(normal_font)
        for line in remainder:
            if y + fm_norm.ascent() > cell_limit:
                break  # Stop drawing at bottom of the cell rectangle

            painter.drawText(x, y + fm_norm.ascent(), line)
            y += fm_norm.height()

        painter.restore()
