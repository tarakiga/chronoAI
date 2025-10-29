"""
Main entry point for ChronoAI application
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from chronoai.ui.main_window import MainWindow
from chronoai.services.scheduler import SchedulerService
from chronoai.services.notification_service import NotificationService
from chronoai.utils.logger import setup_logging

# Setup logging
setup_logging()

logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    try:
        # Create Qt application
        app = QApplication(sys.argv)
        
        # Initialize services
        notification_service = NotificationService()
        scheduler_service = SchedulerService(notification_service)
        
        # Create main window
        main_window = MainWindow(scheduler_service, notification_service)
        main_window.show()
        
        # Set up application exit handling
        def cleanup():
            """Clean up resources on application exit"""
            logger.info("Cleaning up resources...")
            scheduler_service.shutdown()
            notification_service.shutdown()
        
        # Connect cleanup to application about to quit
        app.aboutToQuit.connect(cleanup)
        
        # Start the application event loop
        logger.info("Starting ChronoAI application...")
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()