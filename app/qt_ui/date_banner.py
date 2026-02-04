from PySide6.QtWidgets import QMainWindow, QToolBar, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import datetime as dt

import config

class DateBannerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #self.setWindowTitle("My Application")
        #self.resize(600, 400)
        self.date_label = ""

        # Create the Banner (a ToolBar, in reality)
        self.banner = QToolBar("DateBanner")
        self.banner.setMovable(False)  # Lock it in place
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.banner)

        # Style the Banner background
        self.banner.setStyleSheet("background-color: #f0f0f0; border-bottom: 1px solid #ccc;")

        # Create the label
        self.update_date_label()

        # Set Font: 12pt Bold
        font = QFont("Arial", config.cell_font_size)
        font.setBold(True)
        self.date_label.setFont(font)

        # Center it
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Allow the label to expand and occupy all available space
        self.date_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Forces the text toward the empty area of the window-banner above,
        self.date_label.setStyleSheet("""
            QLabel {
                margin-top: 0px;
                margin-bottom: 6px; 
                padding-top: 0px;
                color: #333;
            }
        """)

        # Ensure the Toolbar itself isn't adding extra space
        self.banner.setStyleSheet("""
            QToolBar {
                /* Match the system title bar color (light grey/silver) */
                background-color: #f0f0f0; 
                border: none;
                padding: 0px;
                spacing: 0px; 
            }
        """)

        # Tighten the vertical space
        self.banner.setFixedHeight(22)

        # Add label to banner
        self.banner.addWidget(self.date_label)

    def update_date_label(self):
        today = dt.date.today()
        day_format = f"%a,  {config.date_display_format}"
        day_and_date = today.strftime(day_format)   #("%a, %d %b %Y")
        self.date_label = QLabel(day_and_date)

