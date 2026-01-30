from PySide6.QtCore import Qt
#from PySide6.QtCore import QSize
#from PySide6.QtWidgets import QStyledItemDelegate

from .base_cell_delegate import BaseCellDelegate

from typing import cast, TYPE_CHECKING
if TYPE_CHECKING:
    from qt_table_model_adapter import QtTableModelAdapter

class CenteredDelegate(BaseCellDelegate):
    """
    Centering delegate for data columns (& buttons?)
    Usage:
        table.setItemDelegateForColumn(col, CenteredDelegate())
    """
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        from qt_table_model_adapter import QtTableModelAdapter
        model = cast("QtTableModelAdapter", index.model())
        vert_align = model.v_alignment_for(index.row(), index.column())
        option.displayAlignment = vert_align | Qt.AlignmentFlag.AlignHCenter

