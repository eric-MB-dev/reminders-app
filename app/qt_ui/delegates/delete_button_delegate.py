from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionButton, QApplication, QStyle
from PySide6.QtCore import QRect, Signal, Qt, QSize
from .base_cell_delegate import BaseCellDelegate

#noinspection PyPep8Naming
import app.table_constants as C

class DeleteButtonDelegate(BaseCellDelegate):
    clicked = Signal(int)  # row index

    def __init__(self, parent=None):
        super().__init__(parent)
        self._button_rects = {}
    
    def paint(self, painter, option, index):
        # Get the Column ID to decide which icon to show
        col_id = C.ALL_COLS[index.column()].id

        # Setup the Button Style Option
        btn = QStyleOptionButton()
        # Ensure the button fits perfectly in the cell (with 2px margin)
        btn.rect = option.rect.adjusted(2, 2, -2, -2)

        # Get the Icon (efficient lookup)
        btn.icon = C.get_icon(col_id)
        btn.iconSize = btn.rect.size() * 0.7  # Scale icon slightly smaller than btn

        # Set the State (Enabled, and potentially Sunken if clicked)
        btn.state = QStyle.State_Enabled | QStyle.State_Active
        if option.state & QStyle.State_Selected:
            # This makes the button look "pressed" if the cell is selected
            btn.state |= QStyle.State_Sunken

        # Store the rect for mouse-click detection
        self._button_rects[index] = QRect(btn.rect)

        # Draw the Native PushButton control
        # using the OS-specific style (Windows/macOS/Linux)
        QApplication.style().drawControl(QStyle.CE_PushButton, btn, painter)

    def get_icon_for_id(self, col_id):
        # Placeholder: Return your QIcon based on "EDIT", "DEL", etc.
        # This keeps the Model's data() method clean!
        return self.parent().get_cached_icon(col_id)

    def editorEvent(self, event, model, option, index):
        if event.type() == event.MouseButtonRelease:
            rect = self._button_rects.get(index)
            if rect and rect.contains(event.pos()):
                self.clicked.emit(index.row())
                return True
        return False
