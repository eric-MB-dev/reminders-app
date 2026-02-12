from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtCore import Qt, QEvent, QSize
from .base_cell_delegate import BaseCellDelegate

class FlagDelegate(BaseCellDelegate):

    # Event can be button press or button release
    def editorEvent(self, event, table_model, option, index):
        if event.type() == QEvent.MouseButtonRelease:
            # print("Delegate model is:", type(model))   # DEBUG
            table_model.toggle_flag(index.row())
            return True
        return False

