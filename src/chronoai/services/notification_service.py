"""
Notification service for handling voice and popup notifications
"""

import logging
import threading
import time
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer, Qt

from chronoai.utils.logger import get_logger
from chronoai.notifications.voice_engine import VoiceEngine

logger = get_logger(__name__)

class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self):
        self.voice_engine = VoiceEngine()
        self.active_notifications = {}
        self.notification_settings = {
            'reminder_time': 15,  # minutes before event
            'user_name': 'User',
            'voice_type': 'default'
        }
        
        logger.info("Notification service initialized")
    
    def show_notification(self, event):
        """Show notification for an event"""
        try:
            logger.info(f"Showing notification for event: {event['title']}")
            
            # Create unique notification ID
            notification_id = f"event_{event['id']}_{datetime.now().timestamp()}"
            
            # Store notification info
            self.active_notifications[notification_id] = {
                'event': event,
                'start_time': datetime.now(),
                'acknowledged': False
            }
            
            # Start notification sequence in a separate thread
            notification_thread = threading.Thread(
                target=self._run_notification_sequence,
                args=(notification_id, event),
                daemon=True
            )
            notification_thread.start()
            
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")
    
    def _run_notification_sequence(self, notification_id, event):
        """Run the escalating notification sequence"""
        try:
            notification_info = self.active_notifications[notification_id]
            user_name = self.notification_settings['user_name']
            
            # T-15:00s - Whisper (20% volume)
            if not notification_info['acknowledged']:
                self.voice_engine.speak(f"Psst, {user_name}...", volume=0.2)
                time.sleep(1.5)
            
            # T-13.5s - Louder whisper (40% volume)
            if not notification_info['acknowledged']:
                self.voice_engine.speak(f"Hey {user_name}...", volume=0.4)
                time.sleep(1.5)
            
            # T-12.0s - Normal voice (75% volume)
            if not notification_info['acknowledged']:
                self.voice_engine.speak(f"{user_name}!", volume=0.75)
                time.sleep(1.5)
            
            # Show popup notification
            if not notification_info['acknowledged']:
                self._show_popup_notification(notification_id, event)
            
            # If not acknowledged after sequence, speak full details
            if not notification_info['acknowledged']:
                self._speak_full_event_details(event)
            
            # Clean up notification
            if notification_id in self.active_notifications:
                del self.active_notifications[notification_id]
            
        except Exception as e:
            logger.error(f"Error in notification sequence: {e}")
            # Clean up on error
            if notification_id in self.active_notifications:
                del self.active_notifications[notification_id]
    
    def _show_popup_notification(self, notification_id, event):
        """Show popup notification with acknowledge button"""
        try:
            # Create popup dialog
            popup = QMessageBox()
            popup.setWindowTitle("ChronoAI Reminder")
            popup.setText(f"You have an upcoming event:")
            popup.setInformativeText(f"{event['title']}\n{event['start_time'].strftime('%H:%M')}")
            
            # Add acknowledge button
            popup.addButton("Acknowledge", QMessageBox.ButtonRole.AcceptRole)
            
            # Set popup to be non-modal and on top
            popup.setWindowFlags(
                Qt.WindowType.Popup |
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.Tool |
                Qt.WindowType.WindowStaysOnTopHint
            )
            
            # Position popup in bottom right corner
            popup.move(
                popup.screen().geometry().width() - popup.width() - 20,
                popup.screen().geometry().height() - popup.height() - 50
            )
            
            # Show popup and handle response
            result = popup.exec()
            
            if result == QMessageBox.ButtonRole.AcceptRole:
                self._acknowledge_notification(notification_id, event)
            
        except Exception as e:
            logger.error(f"Failed to show popup notification: {e}")
    
    def _speak_full_event_details(self, event):
        """Speak full event details"""
        try:
            event_time = event['start_time'].strftime('%H:%M')
            attendees = ', '.join(event.get('attendees', [])) or 'no specific attendees'
            location = event.get('location', 'no specific location')
            
            message = (
                f"You have a meeting at {event_time} with {event['title']}. "
                f"Location: {location}. "
                f"Attendees: {attendees}. "
                f"Just wanted to let you know."
            )
            
            self.voice_engine.speak(message, volume=0.75)
            
        except Exception as e:
            logger.error(f"Failed to speak event details: {e}")
    
    def _acknowledge_notification(self, notification_id, event):
        """Handle notification acknowledgment"""
        try:
            if notification_id in self.active_notifications:
                self.active_notifications[notification_id]['acknowledged'] = True
                
                # Speak acknowledgment message
                event_time = event['start_time'].strftime('%H:%M')
                message = f"You have a meeting at {event_time} with {event['title']}. Just wanted to let you know."
                self.voice_engine.speak(message, volume=0.75)
                
                logger.info(f"Notification acknowledged for event: {event['title']}")
            
        except Exception as e:
            logger.error(f"Failed to acknowledge notification: {e}")
    
    def update_settings(self, settings):
        """Update notification settings"""
        try:
            self.notification_settings.update(settings)
            logger.info(f"Notification settings updated: {settings}")
            
        except Exception as e:
            logger.error(f"Failed to update notification settings: {e}")
    
    def get_settings(self):
        """Get current notification settings"""
        return self.notification_settings.copy()
    
    def shutdown(self):
        """Shutdown the notification service"""
        try:
            logger.info("Shutting down notification service...")
            
            # Cancel all active notifications
            self.active_notifications.clear()
            
            # Shutdown voice engine
            self.voice_engine.shutdown()
            
            logger.info("Notification service shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during notification service shutdown: {e}")