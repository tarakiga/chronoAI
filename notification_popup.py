from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QDesktopWidget, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont

class NotificationPopup(QWidget):
    """
    A small, non-intrusive pop-up window that appears to notify the user
    of an upcoming event. It contains the "Acknowledge" button.

    This class fulfills FR-NOT-04 and FR-NOT-05.
    """
    acknowledged = pyqtSignal()
    snoozed = pyqtSignal()

    def __init__(self, event_title: str):
        super().__init__()

        # --- Window Configuration ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedSize(320, 110)

        # --- Widgets ---
        self.label = QLabel(f"Upcoming: {event_title}")
        font = self.label.font()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setWordWrap(True)

        self.acknowledge_button = QPushButton("Acknowledge")
        self.snooze_button = QPushButton("Snooze")
        self.acknowledge_button.clicked.connect(self.on_acknowledged)
        self.snooze_button.clicked.connect(self.on_snoozed)

        # --- Layout ---
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.snooze_button)
        button_layout.addStretch()
        button_layout.addWidget(self.acknowledge_button)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # --- Positioning ---
        screen_geometry = QDesktopWidget().availableGeometry()
        self.move(screen_geometry.right() - self.width() - 15,
                  screen_geometry.bottom() - self.height() - 15)

    def on_acknowledged(self):
        """Emits the acknowledged signal and closes the window."""
        self.acknowledged.emit()
        self.close()

    def on_snoozed(self):
        """Emits the snoozed signal and closes the window."""
        self.snoozed.emit()
        self.close()