# ChronoAI - Your Personal Calendar Assistant

![ChronoAI](https://img.shields.io/badge/ChronoAI-v1.0-blue)
![Python](https://img.shields.io/badge/Python-3.9+-brightgreen)
![Framework](https://img.shields.io/badge/Framework-PyQt5-orange)

ChronoAI is a personalized, AI-powered desktop assistant that integrates with your Google and Zoho calendars. It provides timely, engaging, and interactive voice reminders for your upcoming events, moving beyond standard, easily-ignored notifications.

---

## Features

- **Unified Calendar View**: Securely connect and sync events from both Google and Zoho calendars into a single, chronologically sorted list.
- **Interactive Voice Notifications**: A unique, escalating voice notification sequence playfully grabs your attention before an event.
- **One-Click Acknowledgment**: A simple, non-intrusive pop-up allows you to acknowledge the reminder with a single click, instantly stopping the audio and getting the event details.
- **Full Event Details**: If you acknowledge the notification (or if it times out), the assistant speaks the full event details, including the title and time.
- **System Tray Integration**: The application runs quietly in your system tray, providing at-a-glance access to your daily schedule without cluttering your desktop.
- **Deep Personalization**: Customize the name the assistant calls you, the TTS voice it uses, and the pre-event reminder time (5, 10, 15, or 30 minutes).
- **Secure Credential Storage**: All API tokens are stored securely using your operating system's native credential manager (e.g., Windows Credential Manager, macOS Keychain).

---

## Getting Started

Follow these instructions to get ChronoAI running on your local machine.

### Prerequisites

- Python 3.9+
- Access to a desktop environment (Windows, macOS, or Linux)

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd chrono-ai
```

### 2. Set Up a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. API Configuration (Crucial Step!)

ChronoAI requires API credentials to connect to your calendars.

#### For Google Calendar:

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project.
3.  Enable the "Google Calendar API".
4.  Go to "Credentials", click "Create Credentials", and select "OAuth client ID".
5.  Choose "Desktop app" as the application type.
6.  After creation, click the "Download JSON" button for the client ID.
7.  Rename the downloaded file to `credentials.json` and place it in the **root directory** of this project.

#### For Zoho Calendar:

1.  Go to the Zoho API Console.
2.  Click "Add Client" and select "Self Client".
3.  After creation, you will receive a **Client ID** and **Client Secret**.
4.  Open the `src/services/zoho_cal.py` file.
5.  Replace the placeholder values for `ZOHO_CLIENT_ID` and `ZOHO_CLIENT_SECRET` with the credentials you obtained.

```python
# In src/services/zoho_cal.py
ZOHO_CLIENT_ID = "YOUR_ZOHO_CLIENT_ID"
ZOHO_CLIENT_SECRET = "YOUR_ZOHO_CLIENT_SECRET"
```

### 5. Running the Application

Once the setup is complete, you can run the application from the root directory:

```bash
python src/main.py
```

- On the first run for each service, you will be guided through an authentication flow. For Google, a browser window will open. For Zoho, you will be prompted in the console to copy/paste a code.
- An icon will appear in your system tray. Click it to open the dashboard and access settings.

---

## Project Structure

The project is organized into a `src` directory containing the core logic, services, and UI components.

```
chrono_ai/
├── src/
│   ├── main.py             # Application entry point
│   ├── core/               # Core logic (scheduler, tts, event manager)
│   ├── services/           # API integrations (Google, Zoho, auth)
│   └── ui/                 # PyQt5 UI components
├── assets/
│   └── icon.png
└── requirements.txt
```
