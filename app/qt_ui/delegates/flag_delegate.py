from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtCore import Qt, QEvent, QSize
from .base_cell_delegate import BaseCellDelegate

from typing import cast, TYPE_CHECKING
if TYPE_CHECKING:
    from qt_table_model_adapter import QtTableModelAdapter

class FlagDelegate(BaseCellDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        from qt_table_model_adapter import QtTableModelAdapter
        model = cast("QtTableModelAdapter", index.model())
        vert_align = model.v_alignment_for(index.row(), index.column())
        option.displayAlignment = vert_align | Qt.AlignmentFlag.AlignHCenter
        
    # Event can be button press or button release
    def editorEvent(self, event, table_model, option, index):
        if event.type() == QEvent.MouseButtonRelease:
            # print("Delegate model is:", type(model))   # DEBUG
            table_model.toggle_flag(index.row())
            return True
        return False

