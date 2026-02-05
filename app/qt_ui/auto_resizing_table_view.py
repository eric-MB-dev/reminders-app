from PySide6.QtWidgets import QTableView, QSizePolicy, QHeaderView
from PySide6.QtCore import QSize, Qt

class AutoResizingTableView(QTableView):
    """
    Usage:
    Make an instance of this class
    # Inside your window class after adding rows to the model:
    table_view.updateGeometry()
    self.adjustSize() # Tells the main window to shrink/expand to fit the new sizeHint
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1. Setup the wrap/resize behavior for the rows
        self.setWordWrap(True)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # 2. Setup Policy: This tells layouts to respect our sizeHint
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        # 3. Disable scrollbars if you want the window to do all the work
        # (Or set to AsNeeded if you have a hard maximum window size)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)


    def sizeHint(self):
        # If no data, don't let the table push the window wide
        if self.model().columnCount() == 0:
            return QSize(400, 200)  # Default sensible starting size

        # --- 1. TOTAL WIDTH: Use a loop to sum the *actual* applied widths ---
        total_w = 0
        for col in range(self.model().columnCount()):
            # Get the actual pixel width currently applied to the view
            total_w += self.columnWidth(col)

        # Add headers and frames just like your old manual function did
        total_w += self.verticalHeader().width() if self.verticalHeader().isVisible() else 0
        total_w += 2 * self.frameWidth()

        if self.verticalScrollBar().isVisible():
            total_w += self.verticalScrollBar().sizeHint().width()

        # --- 2. TOTAL HEIGHT (Remains the same, using automatic length) ---
        total_h = self.verticalHeader().length()
        total_h += self.horizontalHeader().height() if self.horizontalHeader().isVisible() else 0
        total_h += 2 * self.frameWidth()

        if self.horizontalScrollBar().isVisible():
            total_h += self.horizontalScrollBar().sizeHint().height()

        # --- INSTRUMENTATION LOG ---
        #print(f"\n[DEBUG] QTableView.sizeHint() Calculated:")
        #print(f"  > Columns Widths: {sum(col_details)} {col_details}")
        #print(f"  > Decorators: V-Header:{v_header_w}, Frame:{frame_w}, V-Scroll:{v_bar_w}")
        #print(f"  > Result: {total_w}x{total_h}")

        return QSize(total_w, total_h)


    def minimumSizeHint(self):
        return self.sizeHint()
