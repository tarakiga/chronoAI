"""
Main application window for ChronoAI
"""

import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSystemTrayIcon, QMenu, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction, QPixmap

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
        
        # Calendar connection section
        self.setup_calendar_connection(main_layout)
        
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
        
        # Initial status update
        self.update_status()
        
        logger.info("UI initialized successfully")
    
    def setup_calendar_connection(self, parent_layout):
        """Setup calendar connection section in the UI"""
        from chronoai.calendar.manager import CalendarManager
        
        # Create calendar connection widget
        calendar_widget = QWidget()
        calendar_layout = QVBoxLayout(calendar_widget)
        
        # Title
        title = self.create_label("Calendar Connections", font_size=14, bold=True)
        calendar_layout.addWidget(title)
        
        # Google Calendar section
        google_section = self.create_calendar_section("Google Calendar", "google")
        calendar_layout.addWidget(google_section)
        
        # Zoho Calendar section
        zoho_section = self.create_calendar_section("Zoho Calendar", "zoho")
        calendar_layout.addWidget(zoho_section)
        
        # Add stretch to push everything to the top
        calendar_layout.addStretch()
        
        # Add to parent layout
        parent_layout.addWidget(calendar_widget)
    
    def create_calendar_section(self, provider_name, provider_key):
        """Create a calendar connection section"""
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        
        # Provider label
        label = self.create_label(f"{provider_name}:", bold=True)
        section_layout.addWidget(label)
        
        # Status label
        status_label = self.create_label("Not connected")
        section_layout.addWidget(status_label)
        
        # Connect button
        connect_button = self.create_button("Connect", lambda: self.connect_calendar(provider_key, status_label))
        section_layout.addWidget(connect_button)
        
        # Store references for later use
        if not hasattr(self, 'calendar_sections'):
            self.calendar_sections = {}
        self.calendar_sections[provider_key] = {
            'status_label': status_label,
            'connect_button': connect_button
        }
        
        return section_widget
    
    def create_label(self, text, font_size=10, bold=False):
        """Create a label with styling"""
        from PyQt6.QtWidgets import QLabel
        label = QLabel(text)
        if bold:
            label.setStyleSheet("font-weight: bold;")
        if font_size > 10:
            label.setStyleSheet(f"font-size: {font_size}px; font-weight: bold;")
        return label
    
    def create_button(self, text, click_handler):
        """Create a button with click handler"""
        from PyQt6.QtWidgets import QPushButton
        button = QPushButton(text)
        button.clicked.connect(click_handler)
        return button
    
    def connect_calendar(self, provider, status_label):
        """Handle calendar connection"""
        try:
            from chronoai.calendar.manager import CalendarManager
            import os
            from dotenv import load_dotenv
            
            # Load environment variables
            load_dotenv()
            
            # Get credentials
            if provider == "google":
                client_id = os.getenv('GOOGLE_CLIENT_ID')
                client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
            elif provider == "zoho":
                client_id = os.getenv('ZHOHO_CLIENT_ID')
                client_secret = os.getenv('ZHOHO_CLIENT_SECRET')
            else:
                raise ValueError(f"Unknown provider: {provider}")
            
            if not client_id or not client_secret:
                status_label.setText("Missing credentials")
                return
            
            # Create calendar manager and connect
            calendar_manager = CalendarManager()
            credentials = {
                'client_id': client_id,
                'client_secret': client_secret
            }
            
            if provider == "google":
                calendar_manager.connect_calendar('google', credentials)
                status_label.setText("Connected to Google Calendar")
            elif provider == "zoho":
                calendar_manager.connect_calendar('zoho', credentials)
                status_label.setText("Connected to Zoho Calendar")
            
            # Trigger a manual sync
            self.scheduler_service.sync_calendars()
            
        except Exception as e:
            logger.error(f"Failed to connect to {provider} calendar: {e}")
            status_label.setText(f"Connection failed: {str(e)}")
    
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