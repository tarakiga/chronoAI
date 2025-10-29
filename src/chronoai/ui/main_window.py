"""
Main application window for ChronoAI
"""

import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSystemTrayIcon, QMenu, QAction, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap

from chronoai.utils.logger import get_logger

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, scheduler_service, notification_service):
        super().__init__()
        
        self.scheduler_service = scheduler_service
        self.notification_service = notification_service
        
        self.init_ui()
        self.setup_system_tray()
        
        logger.info("Main window initialized")
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("ChronoAI - Personal Calendar Assistant")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # App title and icon
        app_title = "ChronoAI"
        self.setWindowTitle(app_title)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Add widgets to main layout
        main_layout.addLayout(header_layout)
        
        # Initialize timer for status updates
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(30000)  # Update every 30 seconds
        
        logger.info("UI initialized successfully")
    
    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create a simple icon (can be replaced with a proper icon file)
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.blue)
        self.tray_icon.setIcon(QIcon(pixmap))
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Show/Hide action
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tray_menu.addAction(settings_action)
        
        tray_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close_application)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Connect double-click event
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        logger.info("System tray setup completed")
    
    def tray_icon_activated(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
    
    def update_status(self):
        """Update status bar with current information"""
        # Get next upcoming event
        next_event = self.scheduler_service.get_next_event()
        
        if next_event:
            event_time = next_event['start_time'].strftime("%H:%M")
            event_title = next_event['title']
            status_text = f"Next event: {event_title} at {event_time}"
        else:
            status_text = "No upcoming events"
        
        self.status_bar.showMessage(status_text)
    
    def show_settings(self):
        """Show settings dialog"""
        # TODO: Implement settings dialog
        logger.info("Settings dialog requested")
    
    def close_application(self):
        """Close the application"""
        logger.info("Closing application...")
        self.close()
    
    def closeEvent(self, event):
        """Handle window close event"""
        logger.info("Window close event triggered")
        # Hide to system tray instead of closing
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()