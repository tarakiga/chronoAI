from typing import List, Dict, Any

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel,
                             QListWidget, QPushButton, QListWidgetItem,
                             QHBoxLayout)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont
from dateutil import parser

class MainWindow(QMainWindow):
    """
    The main dashboard window for the application.
    It displays a list of today's events and provides access to settings.
    This class fulfills FR-UI-02 and FR-UI-03.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChronoAI Dashboard")
        self.setGeometry(100, 100, 500, 600)  # x, y, width, height

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # --- Title ---
        self.title_label = QLabel("Today's Events")
        font = self.title_label.font()
        font.setPointSize(16)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # --- Event List ---
        self.event_list_widget = QListWidget()
        self.layout.addWidget(self.event_list_widget)

        # --- Buttons ---
        self.button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.settings_button = QPushButton("Settings")
        self.button_layout.addWidget(self.refresh_button)
        self.button_layout.addWidget(self.settings_button)
        self.layout.addLayout(self.button_layout)

        # The signals for these buttons (e.g., self.refresh_button.clicked)
        # will be connected in the main application logic.

    def update_events(self, events: List[Dict[str, Any]]):
        """
        Clears the current list and populates it with a new set of events.
        """
        self.event_list_widget.clear()
        if not events:
            self.event_list_widget.addItem("No upcoming events for today.")
            return

        for event in events:
            try:
                # Parse the datetime string and format it nicely
                start_time = parser.isoparse(event['start_time'])
                time_str = start_time.strftime('%I:%M %p')  # e.g., "02:30 PM"

                title = event.get('title', 'No Title')
                source = event.get('source', 'Unknown').capitalize()

                display_text = f"{time_str} - {title} ({source})"
                item = QListWidgetItem(display_text)
                self.event_list_widget.addItem(item)

            except (parser.ParserError, TypeError) as e:
                # Log this error in a real scenario
                print(f"Could not parse event: {event}. Error: {e}")

    def closeEvent(self, event: QEvent):
        """
        Overrides the default close event. Instead of closing the application,
        it just hides the main window, which is typical for tray applications.
        """
        event.ignore()
        self.hide()