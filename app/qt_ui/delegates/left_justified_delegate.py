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
        # Get the rectangle actually used by the first line
        first_line_rect = painter.boundingRect(option.rect, Qt.TextFlag.TextWordWrap, first)
        painter.drawText(option.rect, Qt.TextFlag.TextWordWrap, first)

        # 5. Draw Remaining Lines (Normal)
        if remainder:
            painter.setFont(option.font)  # Back to normal
            # Shift the drawing area down by the height of the first (wrapped) line
            remainder_rect = option.rect.adjusted(0, first_line_rect.height(), 0, 0)
            painter.drawText(remainder_rect, Qt.TextFlag.TextWordWrap, remainder)

        painter.restore()
