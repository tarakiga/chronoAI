import sys
import os
import json
import logging
from datetime import datetime, timedelta

from PyQt5.QtWidgets import QApplication
from dateutil import parser

from src.core.scheduler import Scheduler
from src.core.tts_engine import TTSEngine
from src.core.event_manager import EventManager
from src.ui.tray_icon import TrayIcon
from src.ui.main_window import MainWindow
from src.ui.settings_ui import SettingsWindow
from src.ui.notification_popup import NotificationPopup
from src.services.auth_manager import AuthManager

# --- Configuration ---
SETTINGS_FILE = "settings.json"
ICON_PATH = "assets/icon.png"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class ChronoAI:
    """
    The main application class that orchestrates all components.
    """
    def __init__(self):
        self.app = QApplication(sys.argv)
        # This is crucial for tray apps; otherwise, the app quits when the last window is closed.
        self.app.setQuitOnLastWindowClosed(False)

        # Initialize core components
        self.tts_engine = TTSEngine()
        self.scheduler = Scheduler()
        self.event_manager = EventManager()

        # Load settings
        self.settings = self.load_settings()

        # Initialize UI components
        if not os.path.exists(ICON_PATH):
            logging.error(f"Icon file not found at {ICON_PATH}. Please create it.")
            # Ensure the directory exists before creating the file
            # Create a dummy file to prevent crashing
            os.makedirs(os.path.dirname(ICON_PATH), exist_ok=True)
            with open(ICON_PATH, 'w') as f: pass

        self.main_window = MainWindow()
        self.tray_icon = TrayIcon(ICON_PATH)
        self.settings_window = SettingsWindow(self.tts_engine.engine.getProperty('voices') if self.tts_engine.engine else [])

        # A reference to the current notification popup to prevent garbage collection
        self.notification_popup = None

        # Connect signals and slots
        self.connect_signals()

        # Apply initial settings
        self.apply_settings()

        logging.info("ChronoAI application initialized.")

    def run(self):
        """Starts the application."""
        self.scheduler.start()
        # Schedule the first sync to run immediately, then every 10 minutes
        self.scheduler.add_job(self.sync_calendars, 'interval', minutes=10, id='recurring_sync')
        self.sync_calendars() # Run once on startup

        logging.info("ChronoAI is running. Starting Qt event loop.")
        sys.exit(self.app.exec_())

    def connect_signals(self):
        """Connects all UI signals to their corresponding slots."""
        # Tray Icon actions
        self.tray_icon.show_action.triggered.connect(self.main_window.show)
        self.tray_icon.sync_action.triggered.connect(self.sync_calendars)
        self.tray_icon.quit_action.triggered.connect(self.app.quit)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Main Window buttons
        self.main_window.refresh_button.clicked.connect(self.sync_calendars)
        self.main_window.settings_button.clicked.connect(self.open_settings)

        # Settings Window account buttons
        self.settings_window.google_connect_button.clicked.connect(self.toggle_google_connection)
        self.settings_window.zoho_connect_button.clicked.connect(self.toggle_zoho_connection)

    def on_tray_icon_activated(self, reason):
        """Shows the main window on a single click of the tray icon."""
        if reason == QSystemTrayIcon.Trigger: # Single click
            self.main_window.show()

    def load_settings(self) -> dict:
        """Loads settings from the JSON file or creates default settings."""
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                logging.info("Loading settings from file.")
                return json.load(f)
        else:
            logging.info("No settings file found, creating default settings.")
            return {
                "user_name": "User",
                "reminder_time": 15, # minutes
                "voice_id": None,
                "snooze_duration": 5 # minutes
            }

    def save_settings(self):
        """Saves the current settings to the JSON file."""
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f, indent=4)
        logging.info("Settings saved.")

    def apply_settings(self):
        """Applies the loaded settings to the application components."""
        if self.settings.get("voice_id") and self.tts_engine.engine:
            self.tts_engine.engine.setProperty('voice', self.settings["voice_id"])
        self.update_account_status_in_settings()
        logging.info("Settings applied.")

    def sync_calendars(self):
        """Fetches events, updates the UI, and schedules notifications."""
        logging.info("Starting calendar sync...")
        self.tray_icon.show_message("ChronoAI", "Syncing calendars...")

        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        events = self.event_manager.get_unified_events(today_start, today_end)
        self.main_window.update_events(events)
        self.schedule_notifications(events)
        logging.info("Calendar sync complete.")

    def schedule_notifications(self, events: list):
        """Schedules a notification job for each upcoming event."""
        # First, clear any existing notification jobs to prevent duplicates
        for job in self.scheduler.get_jobs():
            if job.id.startswith('event_notification_'):
                self.scheduler.remove_job(job.id)

        now = datetime.now()
        reminder_minutes = self.settings.get("reminder_time", 15)

        for event in events:
            try:
                start_time = parser.isoparse(event['start_time'])
                notification_time = start_time - timedelta(minutes=reminder_minutes)

                # Only schedule notifications for future events
                if notification_time > now:
                    job_id = f"event_notification_{event['id']}"
                    self.scheduler.add_job(
                        self.trigger_notification_flow,
                        args=[event],
                        trigger='date',
                        run_date=notification_time,
                        id=job_id,
                        replace_existing=True # Belt-and-suspenders
                    )
            except (parser.ParserError, TypeError) as e:
                logging.error(f"Could not schedule notification for event {event.get('id')}: {e}")

    def trigger_notification_flow(self, event: dict):
        """
        Triggers the full interactive notification flow, including the pop-up
        and escalating audio, fulfilling FR-NOT-02 to FR-NOT-07.
        """
        logging.info(f"--- NOTIFICATION TRIGGERED FOR: {event['title']} ---")
        user_name = self.settings.get("user_name", "User")

        # 1. Create and show the popup
        self.notification_popup = NotificationPopup(event['title'])

        # Define the escalating audio sequence (FR-NOT-03)
        sequence = [
            {"text": f"Psst, {user_name}...", "volume": 0.2, "delay": 0},
            {"text": f"Hey {user_name}...", "volume": 0.4, "delay": 3.0}, # 1.5s speech + 1.5s pause
            {"text": f"{user_name}!", "volume": 0.75, "delay": 3.0}, # 1.5s speech + 1.5s pause
        ]
        total_sequence_duration = sum(step['delay'] for step in sequence) + 1.5 # Add buffer

        # --- Define handler functions ---
        def on_acknowledged():
            logging.info("Notification acknowledged by user.")
            self.tts_engine.stop()

            # Clean up all scheduled parts of this notification sequence
            for i in range(len(sequence)):
                self.scheduler.remove_job(f"notification_step_{event['id']}_{i}")
            self.scheduler.remove_job(f"notification_timeout_{event['id']}")

            # Speak the full details (FR-NOT-06)
            start_time = parser.isoparse(event['start_time'])
            time_str = start_time.strftime('%I:%M %p')
            details_text = f"You have a meeting at {time_str} titled {event['title']}. Just wanted to let you know."
            self.tts_engine.speak(details_text, volume=0.8)

        def on_timeout():
            logging.info("Notification timed out (not acknowledged).")
            # The popup might still be open if the last audio finished
            if self.notification_popup and self.notification_popup.isVisible():
                self.notification_popup.close()

            # Speak the full details (FR-NOT-07)
            start_time = parser.isoparse(event['start_time'])
            time_str = start_time.strftime('%I:%M %p')
            details_text = f"You have a meeting at {time_str} titled {event['title']}. Just wanted to let you know."
            self.tts_engine.speak(details_text, volume=0.8)

        def on_snoozed():
            snooze_minutes = self.settings.get("snooze_duration", 5)
            logging.info(f"Notification snoozed by user for {snooze_minutes} minutes.")
            self.tts_engine.stop()

            # Clean up all scheduled parts of this notification sequence
            for i in range(len(sequence)):
                self.scheduler.remove_job(f"notification_step_{event['id']}_{i}")
            self.scheduler.remove_job(f"notification_timeout_{event['id']}")

            # Reschedule the notification for later
            snooze_time = datetime.now() + timedelta(minutes=snooze_minutes)
            self.scheduler.add_job(
                self.trigger_notification_flow,
                args=[event],
                trigger='date',
                run_date=snooze_time,
                id=f"event_notification_{event['id']}", # Use the same base ID to allow replacement
                replace_existing=True
            )
            self.tray_icon.show_message("Snoozed", f"Reminder for '{event['title']}' snoozed for {snooze_minutes} minutes.")

        # 2. Connect the "Acknowledge" button signal
        self.notification_popup.acknowledged.connect(on_acknowledged)
        self.notification_popup.snoozed.connect(on_snoozed)
        self.notification_popup.show()

        # 3. Schedule the escalating audio sequence
        base_time = datetime.now()
        current_delay = 0
        for i, step in enumerate(sequence):
            run_time = base_time + timedelta(seconds=current_delay)
            self.scheduler.add_job(
                self.tts_engine.speak,
                args=[step["text"], step["volume"]],
                id=f"notification_step_{event['id']}_{i}",
                trigger='date',
                run_date=run_time
            )
            current_delay += step["delay"]

        # 4. Schedule the timeout handler
        timeout_time = base_time + timedelta(seconds=total_sequence_duration)
        self.scheduler.add_job(on_timeout, id=f"notification_timeout_{event['id']}", trigger='date', run_date=timeout_time)

    def open_settings(self):
        """Opens the settings dialog and handles the result."""
        self.settings_window.load_settings(self.settings)
        self.update_account_status_in_settings()

        if self.settings_window.exec_() == QDialog.Accepted:
            self.settings = self.settings_window.get_settings()
            self.save_settings()
            self.apply_settings()
            # Reschedule notifications with new settings
            self.sync_calendars()
            logging.info("Settings updated and applied.")

    def update_account_status_in_settings(self):
        """Updates the connection status labels in the settings window."""
        # Google
        if AuthManager.get_token('google'):
            self.settings_window.google_status_label.setText("Connected")
            self.settings_window.google_connect_button.setText("Disconnect")
        else:
            self.settings_window.google_status_label.setText("Not Connected")
            self.settings_window.google_connect_button.setText("Connect")
        # Zoho
        if AuthManager.get_token('zoho'):
            self.settings_window.zoho_status_label.setText("Connected")
            self.settings_window.zoho_connect_button.setText("Disconnect")
        else:
            self.settings_window.zoho_status_label.setText("Not Connected")
            self.settings_window.zoho_connect_button.setText("Connect")

    def toggle_google_connection(self):
        if AuthManager.get_token('google'):
            self.event_manager.google_service.disconnect()
        else:
            # This will block and open a browser
            self.event_manager.google_service._get_credentials()
        self.update_account_status_in_settings()

    def toggle_zoho_connection(self):
        if AuthManager.get_token('zoho'):
            self.event_manager.zoho_service.disconnect()
        else:
            # This will block and print to console
            self.event_manager.zoho_service._get_access_token()
        self.update_account_status_in_settings()

if __name__ == '__main__':
    app = ChronoAI()
    app.run()