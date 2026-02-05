# reminder_window.py
#
# RemindersWindow builds the actual UI frame: it creates the QTableView,
# installs delegates, applies column widths, configures selection behavior,
# and arranges layouts. It does not define column labels, column indices,
# or structural constants—those belong to the table model. This layer is
# responsible only for visual presentation and widget composition.

# Qt is a C++ library, methods are injected dynamically, sp PyCharm's static type checks fail.
# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import (QMainWindow, QWidget, QAbstractItemView,
                               QHBoxLayout, QVBoxLayout, QTableView, QLayout,
                               QApplication, QSizePolicy, QPushButton, QLabel,
                               QStyledItemDelegate, QHeaderView, QTableWidgetItem,
                               )
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QFontMetrics

from date_banner import DateBannerWindow
from auto_resizing_table_view import AutoResizingTableView
from delegates.centered_delegate import CenteredDelegate

# noinspection PyPep8Naming
import app.table_constants as C

from app.config import config

INIT_WINDOW_WIDTH = 800
INIT_WINDOW_HEIGHT = 300

MAX_WINDOW_WIDTH = 3000  # WAS = sum(C.VM_COLUMN_WIDTHS) + GRID_STRUCTURE_PADDING
MAX_WINDOW_HEIGHT = 800

class RemindersWindow(DateBannerWindow):
    def __init__(self, table_model):
        #print(">>> Reminders init() Started")
        
        super().__init__()
        self.setWindowTitle(C.APP_NAME)
        # Delay layout logic until the window is fully initialized
        # (Making it visible forces the initialization process to finish!)
        self.setVisible(False)
        self._suppress_qt_events = True      # Ignore, paint, resize, and show until we're ready
        self._initial_layout_done = False      # Prevent resize events until it's done
        
        # Reminders Table
        #self.table_view = QtRowAwareTableView()      # The Qt view model
        self.table_view = AutoResizingTableView()
        self.table_model = table_model      # My domain model = table_model.reminders_model
        self.table_view.setModel(self.table_model)

        # TUrn off cell selections &  highlighting on hover
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table_view.setMouseTracking(False)
        self.table_view.setStyleSheet("""
            QTableView::item:hover {
                background-color: transparent;
            }
        """)

        # Add 3 dots to the end of a cell with too much data to display
        self.table_view.setTextElideMode(Qt.TextElideMode.ElideRight)

        # Allow for vertical row-expansion via our descr-column delegate
        vh = self.table_view.verticalHeader()
        vh.setDefaultSectionSize(16)
        vh.setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # Central widget & layout
        main_container = QWidget()
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        #container_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        # Expand table to fill available space
        self.table_view.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred
        )
        container_layout.addWidget(self.table_view)
     
        # Column alignments
        for col, alignment in enumerate(C.ALL_COL_ALIGNMENTS):
            if alignment == "Ctr":
                # Set centered data cells
                self.table_view.setItemDelegateForColumn(col, CenteredDelegate())

        # Data-row font
        cell_font = self.table_view.font()
        cell_font.setPointSize(config.cell_font_size)
        self.table_view.setFont(cell_font)
        
        # Enable headers
        self.table_view.horizontalHeader().setVisible(True)
        hdr_font = self.table_view.horizontalHeader().font()
        hdr_font.setPointSize(config.hdr_font_size)
        hdr_font.setBold(True)
        self.table_view.horizontalHeader().setFont(hdr_font)

        # Now that fonts are established, turn off Qt's row-height minimums.
        # Install Left-justified delegate for item description & countdown columns
        from delegates.left_justified_delegate import LeftJustifiedDelegate
        left_justified_delegate = LeftJustifiedDelegate(self.table_view)
        self.table_view.setItemDelegateForColumn(
            C.DESCR_COL, left_justified_delegate
        )
        self.table_view.setItemDelegateForColumn(
            C.COUNTDOWN_COL, left_justified_delegate
        )
    
        # Bottom BUTTON-BAR BUTTONS
        btn_row = QHBoxLayout()
        container_layout.addLayout(btn_row)
        #
        gear_btn = QPushButton("⚙")    # Unicode gear character
        add_btn = QPushButton("Add Entry")
        exit_btn = QPushButton("Exit")
        #
        btn_row.addWidget(gear_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(add_btn)
        btn_row.addStretch(1)
        # btn_row.addWidget(date_label)
        btn_row.addWidget(exit_btn)
        
        # --- Final window setup ---
        self.setCentralWidget(main_container)
        # container_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        
        # Resize window to fit table width
        #int = self.table_view.sizeHint()
        #self.resize(hint.width(), hint.height() + 50)
        
        # Basic table behavior
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows) # type: ignore[attr-defined]
        self.table_view.setSelectionMode(QAbstractItemView.NoSelection) # type: ignore[attr-defined]
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.horizontalHeader().setStretchLastSection(False)

        # Wiring to toggle the is_critical flag
        from delegates.flag_delegate import FlagDelegate
        self.table_view.setItemDelegateForColumn(
            C.COLUMN_INDICES["FLAG"],
            FlagDelegate(self.table_view)
        )
        
        # Wiring for Item Action Button
        from delegates.delete_button_delegate import DeleteButtonDelegate
        delegate = DeleteButtonDelegate()
        delegate.clicked.connect(self.on_delete_clicked)
        self.table_view.setItemDelegateForColumn(C.DEL_COL, delegate)
        #DEGUG: print("C3: after DeleteButtonDelegate:", self.table)
        
        # Restore saved window location and user configuration settings.
        config.load_config()
        (w, h, x, y) = config.window_geom
        self.move(x, y)
        # ToDo: Clamp the window to the screen (for a move to a smaller screen)
        '''
        g = self.geometry()
        x, y = self.clamp_to_screen(g.x(), g.y(), g.width(), g.height())
        '''
        
        # Use QTimer to defer layout until the window is done & the event-loop is running
        QTimer.singleShot(0, self._finish_init)
    
    # end Init
    
    # Window exists. Make visible to trigger the paint event we need
    def _finish_init(self):
        #print(">>> _finish_init() Started")
        # Remove row height minimums, so single-line rows match multi-line rows.
        #   (Must occur after the delegate is assigned.)
        QTimer.singleShot(0, self.refresh_layout)  # schedule initial layout refresh once

    def refresh_layout(self):
        # Size columns and rows
        self._apply_column_sizing()
        self.table_view.resizeRowsToContents()
        self._apply_row_height_limits()   # Cap row heights

        # Tell window to tell the window that sizeHint has changed
        self.table_view.updateGeometry()  # Refresh the sizeHint

        # --- INSTRUMENTATION START ---
        #t_hint = self.table_view.sizeHint()
        #print(f"\n[DEBUG] Table Hint: {t_hint.width()}x{t_hint.height()}")
        #print(f"[DEBUG] Window Size BEFORE: {self.width()}x{self.height()}")
        # --- INSTRUMENTATION END ---

        if self.layout():
            # Lock the layout to its new, smaller sizeHint
            self.layout().setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.adjustSize()

        # --- INSTRUMENTATION START ---
        #print(f"[DEBUG] Window Size AFTER:  {self.width()}x{self.height()}")
        # --- INSTRUMENTATION END ---

        # Initial layout has finished. Enable RESIZE and keep it from happening again.
        self._initial_layout_done = True
        self._suppress_qt_events = False


    def _apply_row_height_limits(self):
        # Calculate the max height for 3 lines
        metrics = self.table_view.fontMetrics()
        # height() is for one line; lineSpacing() is the distance between baselines
        max_h = (metrics.lineSpacing() * 2) + metrics.height() + 4  # 3 lines + margin for cell border

        v_header = self.table_view.verticalHeader()

        # TEMPORARILY allow manual resizing
        # If the mode is 'ResizeToContents', manual resizeSection() calls are ignored.
        old_mode = v_header.sectionsClickable()  # A placeholder to show we're changing state
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Iterate and cap
        for row in range(self.table_model.rowCount()):
            current_h = self.table_view.rowHeight(row)
            if current_h > max_h:
                v_header.resizeSection(row, max_h)


    #--------------------------------
    # Item Action-button behaviours
    #--------------------------------
    def on_delete_clicked(self, row):
        self.vm.delete_row(row)
        self.table_model.layoutChanged.emit()
    
    # ------------------------
    # Window behaviors
    # ------------------------
    def closeEvent(self, event):
        pos = self.pos()
        x = pos.x()
        y = pos.y()
        
        size = self.size()
        w = size.width()
        h = size.height()
        
        config.window_geom = (w, h, x, y)
        config.save_config()
        
        QApplication.quit()
        event.accept()
        
    def clamp_to_screen(self, x, y, w, h):
        """Make sure the window is visible on a small monitor"""
        screen = QApplication.primaryScreen().availableGeometry()
        
        max_x = screen.right() - w
        max_y = screen.bottom() - h
        
        x = max(screen.left(), min(x, max_x))   # Clamp x to range [constraint, max_x]
        y = max(screen.top(), min(y, max_y))
        
        return x, y
    
    def on_row_font_changed(self, row):
        self._apply_column_sizing()
        self.adjust_window_width_to_columns()
    
    def _apply_column_sizing(self):
        # Let Qt compute a baseline (helps with icon columns, etc.)
        self.table_view.resizeColumnsToContents()
        QApplication.processEvents()
        
        model = self.table_model
        view = self.table_view
        row_count = model.rowCount()
        col_count = model.columnCount()
        
        # --- 1. Compute description column separately (your existing logic)
        self.compute_descr_col_width()
        
        # --- 2. Compute all other columns using actual row fonts
        for col in range(col_count):
            if col == C.DESCR_COL:
                continue
            
            min_w = C.ALL_COL_MIN_WIDTHS[col]
            max_w = C.ALL_COL_MAX_WIDTHS[col]
            
            natural_max = 0
            
            for row in range(row_count):
                index = model.index(row, col)
                text = index.data(Qt.DisplayRole) or ""
                
                # Get the actual font for this cell
                font = view.font()
                if model.is_critical(row):
                    font.setBold(True)
                
                fm = QFontMetrics(font)
                w = fm.horizontalAdvance(text)
                
                if w > natural_max:
                    natural_max = w
            
            # Apply padding (optional but recommended)
            padded = natural_max + 12
            
            # Clamp
            final = max(min_w, min(padded, max_w))
            view.setColumnWidth(col, final)
    
    def compute_descr_col_width(self):
        """
        Compute width of multi-line, where first line may be bold
        """
        model = self.table_model
        view = self.table_view
        row_count = model.rowCount()
        
        min_w = C.ALL_COL_MIN_WIDTHS[C.DESCR_COL]
        max_w = C.ALL_COL_MAX_WIDTHS[C.DESCR_COL]
        
        natural_max = 0
        for row in range(row_count):
            index = model.index(row, C.DESCR_COL)
            text = index.data(Qt.DisplayRole) or ""
            
            # Split into lines
            lines = text.split("\n")
            
            # Determine fonts for this row
            base_font = view.font()
            bold_font = QFont(base_font)
            bold_font.setBold(True)
            
            # First line may be bold
            for i, line in enumerate(lines):
                if i == 0 and model.is_critical(row):
                    fm = QFontMetrics(bold_font)
                else:
                    fm = QFontMetrics(base_font)
                
                w = fm.horizontalAdvance(line)
                if w > natural_max:
                    natural_max = w
        
        # Add padding
        padded = natural_max + 20
        
        # Clamp
        final = max(min_w, min(padded, max_w))
        view.setColumnWidth(C.DESCR_COL, final)

#endClass RemindersWindow
