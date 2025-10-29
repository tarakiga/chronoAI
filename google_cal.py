import datetime
import os.path
import logging
import json
from typing import List, Dict, Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.services.auth_manager import AuthManager

# If modifying these scopes, delete the stored token.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
ACCOUNT_NAME = 'google'
CREDENTIALS_FILE = 'credentials.json' # Must be in the project root

class GoogleCalendarService:
    """
    Handles authentication and data fetching for the Google Calendar API.
    This class implements FR-CAL-01 and parts of FR-CAL-04.
    """

    def __init__(self):
        self.creds: Optional[Credentials] = None

    def _get_credentials(self) -> Optional[Credentials]:
        """
        Gets valid user credentials. It tries to load them from the secure store,
        refreshes them if expired, or initiates a new login flow if necessary.
        """
        stored_token_str = AuthManager.get_token(ACCOUNT_NAME)
        creds = None

        if stored_token_str:
            try:
                token_info = json.loads(stored_token_str)
                creds = Credentials.from_authorized_user_info(token_info, SCOPES)
            except json.JSONDecodeError:
                logging.error("Failed to decode stored Google token. Please re-authenticate.")
                AuthManager.delete_token(ACCOUNT_NAME) # Clear corrupted token

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logging.info("Refreshing Google API token.")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logging.error(f"Failed to refresh token: {e}. Please re-authenticate.")
                    AuthManager.delete_token(ACCOUNT_NAME)
                    return self._initiate_auth_flow()
            else:
                logging.info("No valid Google credentials found, initiating auth flow.")
                creds = self._initiate_auth_flow()

            # Save the credentials for the next run
            if creds:
                AuthManager.save_token(ACCOUNT_NAME, creds.to_json())

        self.creds = creds
        return self.creds

    def _initiate_auth_flow(self) -> Optional[Credentials]:
        """Initiates the OAuth 2.0 installed application flow."""
        if not os.path.exists(CREDENTIALS_FILE):
            logging.error(f"'{CREDENTIALS_FILE}' not found. Please download it from Google Cloud Console and place it in the project root.")
            return None
        try:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            # The port=0 will find a free port, which is robust.
            creds = flow.run_local_server(port=0)
            return creds
        except Exception as e:
            logging.error(f"Failed to run authentication flow: {e}")
            return None

    def fetch_events(self, start_date: datetime.datetime, end_date: datetime.datetime) -> List[Dict[str, Any]]:
        """
        Fetches events from the user's primary calendar within a given date range.

        Returns:
            A list of events, where each event is a standardized dictionary.
        """
        creds = self._get_credentials()
        if not creds:
            logging.error("Cannot fetch Google Calendar events: Authentication failed.")
            return []

        try:
            service = build('calendar', 'v3', credentials=creds)

            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_date.isoformat(),
                timeMax=end_date.isoformat(),
                maxResults=50, # Reasonable limit for a day's/week's view
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            logging.info(f"Found {len(events)} events in Google Calendar.")
            return [self._parse_event(e) for e in events]

        except HttpError as error:
            logging.error(f'An HTTP error occurred: {error}')
            return []
        except Exception as e:
            logging.error(f'An unexpected error occurred while fetching events: {e}')
            return []

    def _parse_event(self, event: Dict) -> Dict[str, Any]:
        """Converts a Google Calendar API event object into our standard format."""
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))

        return {
            'source': 'google',
            'id': event['id'],
            'title': event.get('summary', 'No Title'),
            'start_time': start,
            'end_time': end,
            'attendees': [att['email'] for att in event.get('attendees', []) if 'email' in att],
            'location': event.get('location', None)
        }

    @staticmethod
    def disconnect():
        """Deletes the stored token for Google Calendar."""
        logging.info("Disconnecting Google Calendar account.")
        AuthManager.delete_token(ACCOUNT_NAME)