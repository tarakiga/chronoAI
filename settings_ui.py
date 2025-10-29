from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QComboBox, QPushButton, QDialogButtonBox,
                             QLabel, QHBoxLayout, QGroupBox)
from PyQt5.QtCore import Qt

class SettingsWindow(QDialog):
    """
    A dialog window for user settings and preferences.
    This class fulfills all requirements from FR-SET-01 to FR-SET-04.
    """
    def __init__(self, available_voices, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ChronoAI Settings")
        self.setMinimumWidth(400)

        # Main layout
        self.main_layout = QVBoxLayout(self)

        # --- General Settings Group ---
        general_group = QGroupBox("Personalization")
        form_layout = QFormLayout()

        # User Name (FR-SET-01)
        self.name_edit = QLineEdit()
        form_layout.addRow("Your Name:", self.name_edit)

        # Reminder Time (FR-SET-03)
        self.reminder_time_combo = QComboBox()
        self.reminder_times = {"5 minutes": 5, "10 minutes": 10, "15 minutes": 15, "30 minutes": 30}
        self.reminder_time_combo.addItems(self.reminder_times.keys())
        form_layout.addRow("Remind Me Before Event:", self.reminder_time_combo)

        # Voice Selection (FR-SET-02)
        self.voice_combo = QComboBox()
        self.available_voices = available_voices
        if available_voices:
            self.voice_combo.addItems([v.name for v in available_voices])
        else:
            self.voice_combo.addItem("No voices found")
            self.voice_combo.setEnabled(False)
        form_layout.addRow("Assistant Voice:", self.voice_combo)

        # Snooze Duration
        self.snooze_duration_combo = QComboBox()
        self.snooze_durations = {"2 minutes": 2, "5 minutes": 5, "10 minutes": 10, "15 minutes": 15}
        self.snooze_duration_combo.addItems(self.snooze_durations.keys())
        form_layout.addRow("Snooze Duration:", self.snooze_duration_combo)

        general_group.setLayout(form_layout)
        self.main_layout.addWidget(general_group)

        # --- Account Management Group (FR-SET-04) ---
        accounts_group = QGroupBox("Connected Accounts")
        accounts_layout = QFormLayout()

        # Google Account
        google_widget = QWidget()
        google_layout = QHBoxLayout(google_widget)
        self.google_status_label = QLabel("Not Connected")
        self.google_connect_button = QPushButton("Connect")
        google_layout.addWidget(self.google_status_label)
        google_layout.addStretch()
        google_layout.addWidget(self.google_connect_button)
        accounts_layout.addRow("Google Calendar:", google_widget)

        # Zoho Account
        zoho_widget = QWidget()
        zoho_layout = QHBoxLayout(zoho_widget)
        self.zoho_status_label = QLabel("Not Connected")
        self.zoho_connect_button = QPushButton("Connect")
        zoho_layout.addWidget(self.zoho_status_label)
        zoho_layout.addStretch()
        zoho_layout.addWidget(self.zoho_connect_button)
        accounts_layout.addRow("Zoho Calendar:", zoho_widget)

        accounts_group.setLayout(accounts_layout)
        self.main_layout.addWidget(accounts_group)

        # --- Save/Cancel Buttons ---
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

        # Signals for connect/disconnect buttons will be handled in the main app logic

    def load_settings(self, settings: dict):
        """Populates the UI with values from a settings dictionary."""
        self.name_edit.setText(settings.get("user_name", ""))

        # Set reminder time
        reminder_minutes = settings.get("reminder_time", 15)
        for text, minutes in self.reminder_times.items():
            if minutes == reminder_minutes:
                self.reminder_time_combo.setCurrentText(text)
                break

        # Set voice
        voice_id = settings.get("voice_id")
        if voice_id and self.available_voices:
            for i, voice in enumerate(self.available_voices):
                if voice.id == voice_id:
                    self.voice_combo.setCurrentIndex(i)
                    break

        # Set snooze duration
        snooze_minutes = settings.get("snooze_duration", 5)
        for text, minutes in self.snooze_durations.items():
            if minutes == snooze_minutes:
                self.snooze_duration_combo.setCurrentText(text)
                    break

    def get_settings(self) -> dict:
        """Returns a dictionary of the current settings from the UI."""
        selected_voice_index = self.voice_combo.currentIndex()
        voice_id = self.available_voices[selected_voice_index].id if selected_voice_index >= 0 and self.available_voices else None

        return {
            "user_name": self.name_edit.text(),
            "reminder_time": self.reminder_times[self.reminder_time_combo.currentText()],
            "voice_id": voice_id,
            "snooze_duration": self.snooze_durations[self.snooze_duration_combo.currentText()]
        }