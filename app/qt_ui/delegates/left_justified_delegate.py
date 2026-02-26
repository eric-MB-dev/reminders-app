import sys

from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, QTextDocument, QFontMetrics, QColor  #, QTextOption
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
        doc.setDocumentMargin(0)

        # Update the font with the configured point size
        f=QFont(option.font)
        f.setPointSize(config.cell_font_pt_size)
        doc.setDefaultFont(f)

        doc.setPlainText(text)
        doc.setTextWidth(width)

        # Calculate height for a single line
        metrics = QFontMetrics(f)
        line_height = metrics.lineSpacing()

        # Get the actual number of lines (after wrapping)
        # doc.lineCount() is the most accurate way to see how many
        # lines the text takes up inside the current 'width'.
        actual_lines = doc.lineCount()

        # Apply the User Governor (Max Lines)
        # e.g., the doce has 5 lines, but the user set max to 3
        max_allowed = config.line_limit
        display_lines = min(actual_lines, max_allowed)

        # Calculate final snug height (Line height * allowed lines)
        # No extra padding needed here because we are explicitly
        # defining the height by the font's own spacing.
        height =(line_height * display_lines) + 2

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

    def paint(self, painter, option, index):
        # 1. Make sure no text ever goes past a cell boundary
        painter.save()
        painter.setClipRect(option.rect)

        text = index.data()
        if not text:
            # Nothing to do (this code should never execute!)
            painter.restore()
            return

        # 2. Determine vertical alignment (Left align always)
        # Center vertically if it's a single line OR if the user restricted rows to 1 line.
        v_bit = Qt.AlignmentFlag.AlignVCenter

        # Check the 'anchor' column (Description) for newlines
        # We can check "text", but that value is good only if this IS the Descr column
        reminder = index.model().get_reminder(index.row())
        descr_text = getattr(reminder, "descr", "")

        # Only align to Top if there is a newline AND the user allows > 1 line.
        if "\n" in descr_text and config.line_limit > 1:
            v_bit = Qt.AlignmentFlag.AlignTop
        alignment = Qt.AlignmentFlag.AlignLeft | v_bit
        alignment = alignment | Qt.TextFlag.TextWordWrap

        # 3. Split the data to isolate the first line
        lines = text.strip().split("\n")
        first = lines[0]

        # If the user only wants 1 line, IGNORE the rest of the text
        # for drawing purposes. This ensures ONLY the first line is centered.
        if config.line_limit == 1:
            text = first  # If multiple, pretend the first line is the only line
            remainder = "" # Force no remainder
        else:
            remainder = "\n".join(lines[1:]) if len(lines) > 1 else ""

        # 4. Determine if we should bold the first line
        # of a critical description column
        reminder = index.model().get_reminder(index.row())
        is_critical = getattr(reminder, "is_critical", False)
        if not is_critical or index.column() != C.DESCR_IDX:
            # --- NON-CRITICAL: NORMAL DRAWING ---
            painter.setFont(option.font)
            painter.drawText(option.rect, alignment, text)
            self._draw_elide_indicator(painter, option, descr_text)
            painter.restore()
            return

        # 5. Initialize Style Options
        # Ensure that 'option' reflects current model data (selection, font, etc.)
        # before we begin manual multi-line font/rect calculations.
        if not "\n" in text:
            self.initStyleOption(option, index)

        # 6. Draw Bold First Line
        bold_font = QFont(option.font)
        bold_font.setBold(True)
        painter.setFont(bold_font)

        # boundingRect calculates the height used by the wrapped first line
        # drawText gives us automatic wrapping
        first_line_rect = painter.boundingRect(option.rect, alignment, first)
        painter.drawText(option.rect, alignment, first)

        # 7. Draw Remaining Lines (Normal weight)
        # shift the drawing area down by exactly the height of the first line
        if remainder:
            painter.setFont(option.font)  # Back to normal
            # Shift the drawing area down by the height of the first (wrapped) line
            remainder_rect = option.rect.adjusted(0, first_line_rect.height(), 0, 0)
            painter.drawText(remainder_rect, Qt.TextFlag.TextWordWrap, remainder)

        # 8. Elide the text, if needed
        self._draw_elide_indicator(painter, option, descr_text)

        painter.restore()
    #end paint()


    def _draw_elide_indicator(self, painter, option, text):
        # 1. Initialize doc with the current cell width and font
        check_doc = QTextDocument()
        check_doc.setDocumentMargin(0)
        check_doc.setDefaultFont(option.font)
        check_doc.setPlainText(text)
        check_doc.setTextWidth(option.rect.width())

        # 2. Check if text is "crushed out" based on user limit.
        # If so, add the ellipsis
        if check_doc.lineCount() > config.line_limit:
            painter.save()
            painter.setPen(QColor("#888888"))  # Subtle gray
            painter.drawText(option.rect,
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom,
                             "... ")
            painter.restore()
#endCLASS