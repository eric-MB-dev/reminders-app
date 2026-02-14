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
                               QAbstractScrollArea,
                               )
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QFontMetrics

import qtawesome as qta

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
    def __init__(self, model_adapter):
        #print(">>> Reminders init() Started")

        super().__init__()
        self.setWindowTitle(C.APP_NAME)

        # Delay layout logic until the window is fully initialized
        # (Making it visible forces the initialization process to finish!)
        #self.setVisible(False)

        self.setUpdatesEnabled(False)  # "Freeze" the UI
        self._suppress_qt_events = True      # Ignore, paint, resize, and show until we're ready
        self._initial_layout_done = False      # Prevent resize events until it's done

        # Reminders Table
        #self.table_view = QtRowAwareTableView()      # The Qt view model
        self.table_view = AutoResizingTableView()
        self.model_adapter = model_adapter      # My domain model = table_model.reminders_model
        self.table_view.setModel(self.model_adapter)

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

        # Expand table to fill available space
        self.table_view.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred
        )
        # Alwauys let the window know how wide the table_view really is
        self.table_view.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        # Central widget & layout
        main_container = QWidget()
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        #container_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        container_layout.addWidget(self.table_view)

        # Horizontal column alignments
        for col_idx, col_def in enumerate(C.ALL_COLS):
            # Check the column's horizontal alignment bit
            if C.ALIGN_MAP[col_def.align] == Qt.AlignmentFlag.AlignCenter:
                # Set centered data cells
                self.table_view.setItemDelegateForColumn(col_idx, CenteredDelegate())

        # Data-row font
        cell_font = self.table_view.font()
        cell_font.setPointSize(config.cell_font_pt_size)
        self.table_view.setFont(cell_font)
        config.font_changed.connect(self.on_font_changed)  # Listen for font-changed events

        # Enable headers
        self.table_view.horizontalHeader().setVisible(True)
        hdr_font = self.table_view.horizontalHeader().font()
        hdr_font.setPointSize(config.hdr_font_pt_size)
        hdr_font.setBold(True)
        self.table_view.horizontalHeader().setFont(hdr_font)

        # Now that fonts are established, turn off Qt's row-height minimums.
        # Install Left-justified delegate for item description & countdown columns
        from delegates.left_justified_delegate import LeftJustifiedDelegate
        left_justified_delegate = LeftJustifiedDelegate(self.table_view)
        self.table_view.setItemDelegateForColumn(
            C.DESCR_IDX, left_justified_delegate
        )
        self.table_view.setItemDelegateForColumn(
            C.COUNTDOWN_IDX, left_justified_delegate
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

        # Make scrollbars wide enough to be visible
        self.table_view.setStyleSheet("""
            QScrollBar:vertical { width: 16px; }
            QScrollBar:horizontal { height: 16px; }
        """)

        # Wiring to toggle the is_critical flag
        from delegates.flag_delegate import FlagDelegate
        self.table_view.setItemDelegateForColumn(
            C.FLAG_IDX, FlagDelegate(self.table_view)
        )
        '''
        # Wire up the Action Buttons
        for col_idx, col_def in enumerate(C._COLUMN_SCHEMA):
            if col_def.icon:
                # Create BaseButton to handle clicks
                btn = ReminderButton(col_def.icon)
                btn.action_type = col_def.id  # Tag it so the handler knows what to do

                # Connect to the "smart" row finder
                btn.clicked.connect(self.handle_button_click)

                # Put it in the table
                self.table.setIndexWidget(self.table.model().index(row_idx, col_idx), btn)
        '''

        '''
        from delegates.zOLD_delete_button_delegate import DeleteButtonDelegate
        delegate = DeleteButtonDelegate()
        delegate.clicked.connect(self.on_delete_clicked)
        self.table_view.setItemDelegateForColumn(C.DEL_IDX, delegate)
        #DEGUG: print("C3: after DeleteButtonDelegate:", self.table)
        '''

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


    def resizeEvent(self, event):
        if getattr(self, "_suppress_qt_events", False):
            # Ignore the the less-than-truly-helpful events generated
            # during column sizing, even when suppress_events is True!!!
            event.ignore()
            return
        super().resizeEvent(event)


    def on_font_changed(self):
        # Tell the table to ask its delegates for new sizeHints.
        self.table_view.resizeRowsToContents()
        self.table_view.viewport().update()

    # Window exists. Make visible to trigger the paint event we need
    def _finish_init(self):
        #print(">>> _finish_init() Started")
        # Remove row height minimums, so single-line rows match multi-line rows.
        #   (Must occur after the delegate is assigned.)
        QTimer.singleShot(0, self.refresh_layout)  # schedule initial layout refresh once

    def refresh_layout(self):
        # Don't display updates while we're making them
        self.setUpdatesEnabled(False)

        # Size columns and rows
        self._apply_column_sizing()
        self.table_view.resizeRowsToContents()
        self._apply_row_height_limits()   # Cap row heights

        # RE-CREATE BUTTONS (required after any sort or model change)
        self._update_action_buttons()

        # Tell window to tell the window that sizeHint has changed
        self.table_view.resizeColumnsToContents()
        self.table_view.updateGeometry()  # Refresh the sizeHint

        # --- INSTRUMENTATION START ---
        #t_hint = self.table_view.sizeHint()
        #print(f"\n[DEBUG] Table Hint: {t_hint.width()}x{t_hint.height()}")
        #print(f"[DEBUG] Window Size BEFORE: {self.width()}x{self.height()}")
        # --- INSTRUMENTATION END ---

        if self.layout():
            # Lock the layout to its new, smaller sizeHint
            self.layout().setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)

        self.setUpdatesEnabled(True) # "Thaw" the UI
        self.adjustSize()
        self.show()

        # --- INSTRUMENTATION START ---
        #print(f"[DEBUG] Window Size AFTER:  {self.width()}x{self.height()}")
        # --- INSTRUMENTATION END ---

        # Initial layout has finished. Enable RESIZE and keep it from happening again.
        self._initial_layout_done = True
        self._suppress_qt_events = False

    #end refresh_layout

    def _apply_row_height_limits(self):
        # Calculate the max height for 3 lines
        metrics = self.table_view.fontMetrics()
        # height() is for one line; lineSpacing() is the distance between baselines
        max_h = (metrics.lineSpacing() * 2) + metrics.height() + 4  # 3 lines + margin for cell border

        v_header = self.table_view.verticalHeader()

        # TEMPORARILY allow manual resizing
        # If the mode is 'ResizeToContents', manual resizeSection() calls are ignored.
        #old_mode = v_header.sectionsClickable()  # A placeholder to show we're changing state
        #v_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Iterate and cap
        for row in range(self.model_adapter.rowCount()):
            current_h = self.table_view.rowHeight(row)
            if current_h > max_h:
                v_header.resizeSection(row, max_h)


    #--------------------------------
    # Item Action-button behaviours
    #--------------------------------
    def on_delete_clicked(self, row):
        self.vm.delete_row(row)
        self.model_adapter.layoutChanged.emit()

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

        # Save window position
        config.window_geom = (w, h, x, y)
        config.save_config()

        # Save data
        # (Insurance policy. Data is supposed to be saved as we go along
        # But just in case..)
        try:
            self.model_adapter.save_to_disk()
        except Exception as e:
            print(f"Final save failed:\n{e}")

        # QApplication.quit() -- # PyQt handles the quit() automatically when the window vanishes.
        event.accept()

    def clamp_to_screen(self, x, y, w, h):
        """Make sure the window is visible on a small monitor"""
        screen = QApplication.primaryScreen().availableGeometry()

        max_x = screen.right() - w
        max_y = screen.bottom() - h

        x = max(screen.left(), min(x, max_x))   # Clamp x to range [constraint, max_x]
        y = max(screen.top(), min(y, max_y))

        return x, y

    def on_row_font_changed(self, _row):
        self._apply_column_sizing()
        ###self.adjust_window_width_to_columns()

    def _apply_column_sizing(self):
        # Let Qt compute a baseline (helps with icon columns, etc.)
        self.table_view.resizeColumnsToContents()

        model = self.model_adapter
        view = self.table_view
        row_count = model.rowCount()
        col_count = model.columnCount()

        # If row_count is 0 or None, we aren't ready to measure fonts yet!
        if not row_count:
            # Wait 50ms and try again
            QTimer.singleShot(50, self._apply_column_sizing)
            return

        # --- 1. Compute description column separately (your existing logic)
        self.compute_descr_col_width()

        # --- 2. Compute all other columns using actual row fonts
        for col in range(col_count):
            if col == C.DESCR_IDX:
                continue

            col_def = C.ALL_COLS[col]
            min_w = col_def.min_w
            max_w = col_def.max_w

            natural_max = 0

            for row in range(row_count):
                index = model.index(row, col)
                text = index.data(Qt.DisplayRole) or ""

                # Get the actual font for this cell
                font = view.font()
                reminder = model.get_reminder(row)
                if getattr(reminder, "is_critical", False):
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
        model = self.model_adapter
        view = self.table_view
        row_count = model.rowCount()

        col_def = C.ALL_COLS[C.DESCR_IDX]
        min_w = col_def.min_w
        max_w = col_def.max_w

        natural_max = 0
        for row in range(row_count):
            col_idx = model.index(row, C.DESCR_IDX)
            text = col_idx.data(Qt.DisplayRole) or ""

            # Split into lines
            lines = text.split("\n")

            # Determine fonts for this row
            base_font = view.font()
            bold_font = QFont(base_font)
            bold_font.setBold(True)

            # First line may be bold
            for i, line in enumerate(lines):
                reminder = model.get_reminder(row)
                if i == 0 and getattr(reminder,"is_critical", False):
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
        view.setColumnWidth(C.DESCR_IDX, final)

    def _update_action_buttons(self):
        """
        MUST BE CALLED after and SORT or MODEL CHANGE
        """
        model = self.table_view.model()
        for row in range(model.rowCount()):
            for col, col_def in enumerate(C.COLUMN_SCHEMA):
                if col_def.icon:
                    # Check if this ID is a 'Button' type in our map
                    btn_cfg = C.ICON_MAP.get(col_def.id)
                    if not btn_cfg:
                        continue

                    # Default values from the map
                    icon_str = btn_cfg["icon"]
                    icon_color = btn_cfg["color"]
                    icon_size = QSize(22,22)

                    if col_def.id == "ALERTS":
                        icon_size = QSize(24,24)
                        alerts_enabled = model.data(model.index(row, col), C.ALERTS_ROLE)
                        if not alerts_enabled:
                            icon_str = btn_cfg.get("off_icon", icon_str)
                            icon_color = "lightgray"
                            # "gray"--dark gray, "lightgray"--std light gray,
                            # #E0E0E0--very soft gray for disabled states

                    if col_def.id == "NEXT":
                        has_repeats = model.data(model.index(row, col), C.REPEAT_ROLE)
                        if not has_repeats:
                            icon_color = "lightgray"

                    # Build the button
                    btn = QPushButton()
                    btn.setIcon(qta.icon(icon_str, color=icon_color))
                    btn.setIconSize(icon_size)
                    btn.setFlat(True)
                    # Transparent background, no extra padding
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: transparent; 
                            border: none;
                            padding: 0px;
                            margin: 0px;
                        }
                    """)

                    # Tag it with the action ID
                    btn.setProperty("action_id", col_def.id)

                    # Connect to the smart row-finder
                    btn.clicked.connect(self.on_button_click)

                    # 2. Create a Container to center the icon
                    container = QWidget()
                    layout = QHBoxLayout(container)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setSpacing(0)

                    # Apply Alignment from the Schema
                    if col_def.align == "Ctr":
                        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    elif col_def.align == "Left":
                        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

                    layout.addWidget(btn)

                    # Set it in the view
                    self.table_view.setIndexWidget(model.index(row, col), container)

    def on_button_click(self):
        button = self.sender()
        action_id = button.property("action_id")

        # Map the button's local (0,0) coordinate to the TableView's coordinate system
        global_pos = button.mapTo(self.table_view.viewport(), button.rect().center())
        index = self.table_view.indexAt(global_pos)

        if index.isValid():
            row = index.row()

#endClass RemindersWindow
