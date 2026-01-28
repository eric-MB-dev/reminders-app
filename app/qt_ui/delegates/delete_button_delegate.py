from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionButton, QApplication, QStyle
from PySide6.QtCore import QRect, Signal, Qt, QSize
from .base_cell_delegate import BaseCellDelegate

class DeleteButtonDelegate(BaseCellDelegate):
    clicked = Signal(int)  # row index

    def __init__(self, parent=None):
        super().__init__(parent)
        self._button_rects = {}
    
    def paint(self, painter, option, index):
        icon = index.data(Qt.DecorationRole)

        btn = QStyleOptionButton()
        btn.rect = option.rect
        btn.icon = icon
        btn.state = QStyle.State_Enabled

        self._button_rects[index] = QRect(btn.rect)
        QApplication.style().drawControl(QStyle.CE_PushButton, btn, painter)

    def editorEvent(self, event, model, option, index):
        if event.type() == event.MouseButtonRelease:
            rect = self._button_rects.get(index)
            if rect and rect.contains(event.pos()):
                self.clicked.emit(index.row())
                return True
        return False
