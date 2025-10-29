# ChronoAI - Personal Calendar Assistant

ChronoAI is a personalized, AI-powered desktop assistant designed to integrate with your Google and Zoho calendars. It provides timely, engaging, and interactive voice reminders for upcoming calendar events, moving beyond standard, intrusive alarms.

## Features

- **Calendar Integration**: Secure OAuth 2.0 authentication for Google and Zoho calendars
- **Escalating Notifications**: Playful voice notification system that starts with a whisper and increases in volume
- **Interactive UI**: Clean, simple interface with system tray integration
- **Personalization**: Customizable user name, voice type, and notification timing
- **Background Service**: Runs efficiently as a system tray application with automatic syncing

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or uv package manager

### Install with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/tarakiga/chronoAI.git
cd chronoai

# Create and activate virtual environment with uv
uv venv

# Install dependencies
uv sync
```

### Install with pip

```bash
# Clone the repository
git clone https://github.com/tarakiga/chronoAI.git
cd chronoai

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -e .
```

## Quick Start

1. **Run the application**:

   ```bash
   uv run chronoai
   ```

2. **Connect your calendars**:

   - When first launched, ChronoAI will guide you through connecting your Google and/or Zoho calendars
   - Follow the OAuth 2.0 authentication process for each calendar service

3. **Customize your experience**:
   - Access settings to customize your name, preferred voice, and notification timing
   - Choose from available text-to-speech voices

## How It Works

ChronoAI monitors your calendars and provides 15-minute pre-event reminders through an escalating voice sequence:

1. **T-15:00s**: A whisper at 20% volume: _"Psst, [User Name]..."_
2. **T-13.5s**: A louder whisper at 40% volume: _"Hey [User Name]..."_
3. **T-12.0s**: A normal speaking voice at 75% volume: _"[User Name]!"_

During this sequence, a simple pop-up notification appears with an "Acknowledge" button. Clicking it stops the escalation and provides event details. If not acknowledged, the system speaks the full event details after the sequence.

## Requirements

### Functional Requirements

- **Calendar Integration**: OAuth 2.0 authentication for Google and Zoho calendars
- **Notification Engine**: 15-minute pre-event reminder with escalating audio sequence
- **Interactive UI**: Simple pop-up with "Acknowledge" button during notifications
- **Personalization**: Customizable user name, voice type, and reminder timing
- **Background Service**: Runs as a system tray application with automatic syncing

### Technical Requirements

- **Language**: Python
- **UI Framework**: PyQt6
- **Calendar APIs**: Google APIs Client Library, requests for Zoho
- **Scheduling**: APScheduler
- **Text-to-Speech**: pyttsx3
- **Audio Control**: pydub (for future volume control enhancements)

## Configuration

ChronoAI uses environment variables for configuration. Create a `.env` file in the project root:

```env
# Google Calendar API Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Zoho Calendar API Configuration
ZHOHO_CLIENT_ID=your_zoho_client_id
ZHOHO_CLIENT_SECRET=your_zoho_client_secret
```

### Obtaining API Keys

#### Google Calendar API Keys

1. **Go to the Google Cloud Console**

   - Visit [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable the Google Calendar API**

   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API" and click "Enable"

3. **Configure OAuth Consent Screen**

   - Navigate to "APIs & Services" > "OAuth consent screen"
   - Choose "External" user type and click "Create"
   - Fill in required information:
     - App name: "ChronoAI"
     - User support email: Your email
     - Developer contact information: Your email
   - Click "Save and Continue"
   - On "Scopes" page, click "Add or Remove Scopes"
   - Search for and select "Google Calendar API"
     - Scope: `.../auth/calendar.readonly`
   - Click "Update", then "Save and Continue"
   - On "Test users" page, click "Add Users"
   - Add your Google account email as a test user
   - Click "Save and Continue"

4. **Create OAuth 2.0 Credentials**

   - Navigate to "APIs & Services" > "Credentials"
   - Click "+ CREATE CREDENTIALS" > "OAuth client ID"
   - Application type: "Desktop app"
   - Name: "ChronoAI Desktop Client"
   - Click "Create"
   - Copy the "Client ID" and "Client Secret" values

5. **Download Credentials File (Optional)**
   - You can download the credentials as a JSON file
   - Save it as `credentials_google.json` in your project root

#### Zoho Calendar API Keys

1. **Go to Zoho Developer Console**

   - Visit [https://api.zoho.com/](https://api.zoho.com/)
   - Sign in with your Zoho account

2. **Create a New Client**

   - Click "CREATE NEW CLIENT"
   - Fill in the details:
     - Client Name: "ChronoAI"
     - Client Description: "Desktop calendar assistant"
     - Homepage URL: `http://localhost`
     - Authorization Grant Type: "Authorization Code"
     - Redirect URI: `http://localhost`
   - Click "CREATE"

3. **Note Down Credentials**

   - Copy the "Client ID" and "Client Secret" values
   - These will be used in your `.env` file

4. **Configure API Scope**
   - In your Zoho Developer Console, navigate to your client
   - Under "OAuth Settings", ensure you have the necessary scopes:
     - `ZohoCalendar.events.READ`
     - `ZohoCalendar.settings.READ`

## Development

### Setup Development Environment

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run black .

# Lint code
uv run flake8 .

# Type checking
uv run mypy .
```

### Project Structure

```
chronoai/
├── src/
│   └── chronoai/
│       ├── __init__.py
│       ├── main.py                 # Application entry point
│       ├── ui/                     # User interface components
│       │   ├── __init__.py
│       │   └── main_window.py      # Main application window
│       ├── calendar/               # Calendar integration
│       │   ├── __init__.py
│       │   ├── manager.py          # Calendar manager
│       │   ├── google_calendar.py  # Google Calendar integration
│       │   └── zoho_calendar.py    # Zoho Calendar integration
│       ├── notifications/          # Notification system
│       │   ├── __init__.py
│       │   └── voice_engine.py     # Text-to-speech engine
│       ├── services/               # Core services
│       │   ├── __init__.py
│       │   ├── scheduler.py        # Event scheduling
│       │   └── notification_service.py # Notification management
│       └── utils/                  # Utility functions
│           ├── __init__.py
│           └── logger.py           # Logging configuration
├── tests/                          # Test files
├── config/                         # Configuration files
├── pyproject.toml                  # Project configuration
└── README.md                       # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/tarakiga/chronoAI/issues) page
2. Create a new issue with detailed information
3. Join our community discussions

## Roadmap

- [ ] Mobile application (iOS/Android)
- [ ] Natural language processing for dynamic messages
- [ ] Integration with other calendar services (Outlook, Apple Calendar)
- [ ] "Snooze" functionality for notifications
- [ ] Analytics dashboard on notification patterns

## Acknowledgments

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the excellent UI framework
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3) for offline text-to-speech
- [APScheduler](https://apscheduler.readthedocs.io/) for robust task scheduling
- Google and Zoho Calendar APIs for seamless calendar integration
