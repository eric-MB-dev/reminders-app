import sys

from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, QTextDocument # , QTextOption, QFontMetrics
from PySide6.QtWidgets import QStyledItemDelegate

# noinspection PyPep8Naming
import table_constants as C
from app.config import config

import os
#import sys, traceback

from typing import cast, TYPE_CHECKING
if TYPE_CHECKING:
    from model_adapter import ModelAdapter

class LeftJustifiedDelegate(QStyledItemDelegate):
    """
    Determine row height and expand rows as needed, and
    """
    # Left horizontal alignment for these cells
    h_alignment_bit = Qt.AlignmentFlag.AlignLeft

    def __init__(self, parent_table):
        super().__init__(parent_table)
        self.parent_table = parent_table # Now we can talk to the table!

    # Allow copying from DESCR column
    def createEditor(self, parent, option, index):
        if index.column() == C.DESCR_IDX:
            editor = QTextEdit(parent)
            editor.setReadOnly(True)
            # Allows mouse selection and keyboard (Ctrl+C)
            editor.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse |
                                           Qt.TextInteractionFlag.TextSelectableByKeyboard)
            # Optional: remove the border so it blends in while selecting
            editor.setFrameStyle(QFrame.Shape.NoFrame)
            return editor
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        # Pull data from model and shove it into the editor
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if isinstance(editor, QTextEdit):
            editor.setPlainText(text)
        else:
            super().setEditorData(editor, index)

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
    def draw_text_line(self, painter, x, y, width, line_text, font):
        """
        This was a *great* attempt. The idea was to elide a very long-line
        (like a link) if the text exceeds the rectangle width.
        BUT...
         - The rectangle is provided by Qt.
         - So the paint() re-write below didn't fix the problem
         - To override it, we need to moodify sizeHint
         - AND (the deal breaker) we *also* have to turn off resizeRowsToContents
         - That fcn is doing too much good for us, right now. Turning it
           off will lead to a plethora of other issues. Easier to live with
           the occasional long-link that wraps onto a short extra line.
        """
        return
    '''    
        fm = QFontMetrics(font)
        # Provides at end of the text
        available_width = width - 10

        # Elide a long line so it doesn't spill over into the next cell
        display_text = fm.elidedText(line_text, Qt.TextElideMode.ElideRight, available_width)

        painter.setFont(font)
        # Note: We use the baseline (y + ascent) for precise vertical control
        painter.drawText(x + 5, y + fm.ascent(), display_text)
    
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
        #
        norm_font = QFont(option.font)
        norm_font.setBold(False)
        #
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
        
        # Item is flagged  as critical: bold first line only ---
        text = index.data()
        if not text:
            super().paint(painter, option, index)
            return
        
        lines = text.split("\n")
        first = lines[0]
        remainder = lines[1:]
        
        painter.save()
        # Ensure we never paint outside the intended cell boundary
        painter.setClipRect(option.rect)

        # Compute total text height
        total_height = fm_bold.height() + len(remainder) * fm_norm.height()

        # Determine vertical alignment
        from model_adapter import v_alignment
        model = cast("ModelAdapter", index.model())
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
        ###self.draw_text_line(painter, x, y, option.rect.width(), first, bold_font)

        # drawText starts from a baseline (= ascent plus starting y)
        painter.drawText(x, y + fm_bold.ascent(), first)
        y += fm_bold.height()

        # Draw remaining lines in maximum-size cell rectangle
        actual_row_h = self.parent_table.rowHeight(index.row())
        cell_limit = option.rect.top() + actual_row_h

        painter.setFont(norm_font)
        for line in remainder:
            if y + fm_norm.ascent() > cell_limit:
                break  # Stop drawing at bottom of the cell rectangle

            ###self.draw_text_line(painter, x, y, option.rect.width(), line, norm_font)
            painter.drawText(x, y + fm_norm.ascent(), line)
            y += fm_norm.height()

        painter.restore()
'''

    def paint(self, painter, option, index):
        # Get the data and determin state.
        reminder = index.model().get_reminder(index.row())
        is_critical = getattr(reminder, "is_critical", False)

        if not is_critical or index.column() != C.DESCR_IDX:
            super().paint(painter, option, index)
            return

        text = index.data()
        if not text: return

        # Split the data
        lines = text.strip().split("\n")
        first = lines[0]
        remainder = "\n".join(lines[1:]) if len(lines) > 1 else ""

        painter.save()
        painter.setClipRect(option.rect)

        # Draw Bold First Line
        bold_font = QFont(option.font)
        bold_font.setBold(True)
        painter.setFont(bold_font)

        # We use a rect-based drawText to get automatic wrapping
        # This returns the rectangle actually used by the first line
        first_line_rect = painter.boundingRect(option.rect, Qt.TextFlag.TextWordWrap, first)
        painter.drawText(option.rect, Qt.TextFlag.TextWordWrap, first)

        # 5. Draw Remaining Lines (Normal)
        if remainder:
            painter.setFont(option.font)  # Back to normal
            # Shift the drawing area down by the height of the first (wrapped) line
            remainder_rect = option.rect.adjusted(0, first_line_rect.height(), 0, 0)
            painter.drawText(remainder_rect, Qt.TextFlag.TextWordWrap, remainder)

        painter.restore()
