from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionButton, QApplication, QStyle
from PySide6.QtCore import QRect, Signal, QEvent, Qt, QSize
from .base_cell_delegate import BaseCellDelegate

#noinspection PyPep8Naming
import app.table_constants as C

class BaseButtonDelegate(BaseCellDelegate):
    clicked = Signal(int)  # row index

    def __init__(self, parent=None):
        super().__init__(parent)
        self._button_rects = {}
        self._icon = None

    def paint(self, painter, option, index):
        #col_id = C.ALL_COLS[index.column()].id

        # Call the subclass implementation
        icon_name = self.get_icon_name()

        # --- Button Icon ---
        btn = QStyleOptionButton()

        # Define a fixed size click-area, centered in the cell rectangle
        fixed_width, fixed_height = 30, 30
        center = option.rect.center()
        btn.rect = QRect(center.x() - fixed_width // 2,
                         center.y() - fixed_height // 2,
                         fixed_width, fixed_height)
        if self._icon:
            btn.icon = self._icon
            btn.iconSize = QSize(24, 24)

        # Simplify features to the default state
        btn.features = QStyleOptionButton.ButtonFeature.None_

        # Set the state to active & enabled
        btn.state = QStyle.State_Enabled | QStyle.State_Active

        # Check for Mouse Hover (Requires MouseTracking enabled on the TableView)
        '''
        if option.state & QStyle.State_MouseOver:
            btn.state |= QStyle.State_Raised  # Highlighting effect
        '''
        # Use Sunken if the user is actually CLICKING
        # This usually requires checking your custom 'pressed' index state
        '''
        if hasattr(self, "_pressed_index") and self._pressed_index == index:
            btn.state |= QStyle.State_Sunken        
        '''
        # Store the rect for hit-testing in edit_event
        self._button_rects[index] = QRect(btn.rect)

        # Draw the button
        curr_style = option.widget.style() if option.widget else QApplication.style()
        curr_style.drawControl(QStyle.CE_PushButton, btn, painter)

    #end paint()

    ''' 
    # ICON LIBRARY
    import qtawesome as qta
    from PySide6.QtWidgets import QPushButton
    
    # Create your icons with custom colors
    delete_icon = qta.icon('fa5s.trash-alt', color='red')
    edit_icon = qta.icon('fa5s.pencil-alt')
    repeat_icon = qta.icon('fa.repeat', color='blue')
    
    # Apply to your buttons  -- MOVE TO DELETE DELEGATE
    btn = QPushButton()
    btn.setIcon(delete_icon)
    '''

    @abstractmethod
    def do_action(self):
        """Semantics for what happens when clicked."""
        pass

    @abstractmethod
    def get_icon_name(self):
        """Subclasses MUST implement this to return a string."""
        pass

    def get_icon(self):
        """Lazy-load of icon"""
        if self._icon is None:
            # We use the style from the widget currently being painted
            style = QApplication.style()
            '''option.widget.style() if option.widget else QApplication.style()'''
            icon = style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
            if not icon.isNull():
                self._icon = icon

    # Must be overriden??
    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease:
            rect = self._button_rects.get(index)
            if rect and rect.contains(event.pos()):
                self.clicked.emit(index.row())
                self.do_action()
                return True
        return False