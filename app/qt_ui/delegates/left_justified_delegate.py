import sys

from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, QFontMetrics, QTextDocument
from PySide6.QtWidgets import QStyledItemDelegate

# noinspection PyPep8Naming
import table_constants as C
from app.config import config

import os
#import sys, traceback

from typing import cast, TYPE_CHECKING
if TYPE_CHECKING:
    from qt_table_model_adapter import QtTableModelAdapter

class LeftJustifiedDelegate(QStyledItemDelegate):
    """
    Determine row height and expand rows as needed, and
    """
    # Left horizontal alignment for these cells
    h_alignment_bit = Qt.AlignmentFlag.AlignLeft

    def __init__(self, parent_table):
        super().__init__(parent_table)
        self.parent_table = parent_table # Now we can talk to the table!

    def sizeHint(self, option, index):
        text = index.data(Qt.DisplayRole) or ""

        # INSTRUMENTATION: Check for non-string data
        if not isinstance(text, str) and text is not None:
            # Determine which function/method is breaking (returning a method instead of a string)
            print(f"\n[CRITICAL ERROR] Delegate received non-string data!")
            print(f"Row: {index.row()}, Col: {index.column()}")
            print(f"Data Type: {type(text)}")
            print(f"Data Value: {text}")
            os._exit(1)

        # Qt sometimes passes width=0 during geometry calculation
        width = option.rect.width()
        if width <= 1:
            width = option.widget.columnWidth(index.column())
        
        doc = QTextDocument()

        # Update the font with the configured point size
        f=QFont(option.font)
        f.setPointSize(config.cell_font_pt_size)
        doc.setDefaultFont(f)

        doc.setPlainText(text)
        doc.setTextWidth(width)

        height = int(doc.size().height()) - 6
        return QSize(width, height)
    
    # Bold the first line only for a critical-item reminder
    def paint(self, painter, option, index):
        actual_row_h = self.parent_table.rowHeight(index.row())
        rect_h = option.rect.height()

        # --- INSTRUMENTATION ---
        # Only log if there's a mismatch or if the row is 'tall'
        #if rect_h != actual_row_h or rect_h > 100:
        #    print(f"[DEBUG] Paint Row {index.row()}:")
        #    print(f"  > Actual Row Height: {actual_row_h}")
        #    print(f"  > Option Rect Height: {rect_h}")
        #    print(f"  > State: {option.state}")  # Tells us if it's hovered, active, etc.
        # ------------------------

        # Fonts & metrics
        bold_font = QFont(option.font)
        bold_font.setBold(True)
        norm_font = QFont(option.font)
        norm_font.setBold(False)
        fm_bold = QFontMetrics(bold_font)
        fm_norm = QFontMetrics(norm_font)

        # If not flagged as critical, paint normally within the cell's max-height rectangle
        reminder = index.model().get_reminder(index.row())
        is_critical = getattr(reminder, "is_critical", False)
        if not is_critical:
            painter.save()
            painter.setFont(norm_font)
            painter.setClipRect(option.rect)  # The magic wall
            super().paint(painter, option, index)
            painter.restore()
            return

        if index.column() != C.DESCR_IDX:
            # Not the description column, so no first-line bolding logic
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

        # Compute total text height
        total_height = fm_bold.height() + len(remainder) * fm_norm.height()

        # Determine vertical alignment
        from qt_table_model_adapter import v_alignment
        model = cast("QtTableModelAdapter", index.model())
        reminder = model.get_reminder(index.row())
        vert_align = v_alignment(reminder)

        # Qtable refuses to adjust it's minimum row size below 28px or so.
        # So we resort to code like this to center single-line rows in the
        # overly-tall rows. (Multi-line rows work beautifully.)
        #print(f"DEBUG: Row {index.row()} Vert Align Bits: {bin(int(vert_align or 0))}")
        if vert_align & Qt.AlignmentFlag.AlignTop:
            # Multi-line row start at top left of cell
            y = option.rect.top()
        else:
            # Single-line row (no note, centered)
            y = option.rect.top() + (option.rect.height() - fm_bold.height()) // 2

        # Starting x
        x = option.rect.left()

        # Draw first (bold) line
        painter.setFont(bold_font)
        self.draw_text_line(painter, x, y, option.rect.width(), first, bold_font)
        #painter.drawText(x, y + fm_bold.ascent(), first)
        y += fm_bold.height()

        # Draw remaining lines in maximum-size cell rectangle
        actual_row_h = self.parent_table.rowHeight(index.row())
        cell_limit = option.rect.top() + actual_row_h

        painter.setFont(norm_font)
        for line in remainder:
            if y + fm_norm.ascent() > cell_limit:
                break  # Stop drawing at bottom of the cell rectangle

            self.draw_text_line(painter, x, y, option.rect.width(), line, norm_font)
            #painter.drawText(x, y + fm_norm.ascent(), line)
            y += fm_norm.height()

        painter.restore()


    def draw_text_line(self, painter, x, y, width, text, font):
        """
        Draws a single line of text at (x, y) coordinates.
        Elides if the text exceeds the provided width.
        """
        fm = QFontMetrics(font)
        # The '10' provides a 5px buffer on each side of the text
        available_width = width - 10

        # Standardize the eliding here so no line ever spills
        display_text = fm.elidedText(text, Qt.TextElideMode.ElideRight, available_width)

        painter.setFont(font)
        # Note: We use the baseline (y + ascent) for precise vertical control
        painter.drawText(x + 5, y + fm.ascent(), display_text)
