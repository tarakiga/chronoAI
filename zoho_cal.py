import datetime
import logging
import json
from typing import List, Dict, Any, Optional

import requests

from src.services.auth_manager import AuthManager

# --- Zoho Configuration ---
# IMPORTANT: These must be replaced with your actual Client ID and Secret
# from the Zoho API Console for a "Self Client" application.
ZOHO_CLIENT_ID = "YOUR_ZOHO_CLIENT_ID"
ZOHO_CLIENT_SECRET = "YOUR_ZOHO_CLIENT_SECRET"

# This is a placeholder. If your client ID is not set, the app will not work.
if "YOUR_ZOHO" in ZOHO_CLIENT_ID:
    logging.warning("Zoho Client ID and Secret are not set in zoho_cal.py. Zoho integration will not work.")

ACCOUNT_NAME = 'zoho'
SCOPES = "ZohoCalendar.events.READ,ZohoCalendar.calendars.READ"

# Zoho API Endpoints
ACCOUNTS_URL = "https://accounts.zoho.com" # Or .eu, .in, etc.
TOKEN_URL = f"{ACCOUNTS_URL}/oauth/v2/token"
API_BASE_URL = "https://calendar.zoho.com/api/v1"

class ZohoCalendarService:
    """
    Handles authentication and data fetching for the Zoho Calendar API.
    This class implements FR-CAL-02 and parts of FR-CAL-04.
    """

    def __init__(self):
        self.access_token: Optional[str] = None

    def _get_access_token(self) -> Optional[str]:
        """
        Ensures a valid access token is available.
        It uses a stored refresh token to get a new access token.
        If no refresh token exists, it guides the user through the initial auth flow.
        """
        if self.access_token:
            return self.access_token

        refresh_token = AuthManager.get_token(ACCOUNT_NAME)

        if not refresh_token:
            logging.info("No Zoho refresh token found. Starting initial authentication.")
            refresh_token = self._initiate_auth_flow()
            if not refresh_token:
                return None
            AuthManager.save_token(ACCOUNT_NAME, refresh_token)

        # We have a refresh token, so let's get a new access token
        try:
            response = requests.post(TOKEN_URL, params={
                'refresh_token': refresh_token,
                'client_id': ZOHO_CLIENT_ID,
                'client_secret': ZOHO_CLIENT_SECRET,
                'grant_type': 'refresh_token'
            })
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data['access_token']
            logging.info("Successfully refreshed Zoho access token.")
            return self.access_token
        except requests.exceptions.RequestException as e:
            logging.error(f"Error refreshing Zoho access token: {e}")
            if e.response and e.response.status_code in [400, 401]:
                logging.error("Zoho refresh token might be invalid. Please try disconnecting and reconnecting.")
                AuthManager.delete_token(ACCOUNT_NAME)
            return None

    def _initiate_auth_flow(self) -> Optional[str]:
        """
        Guides the user through the one-time manual process of getting a grant token
        and exchanging it for a refresh token.
        """
        if "YOUR_ZOHO" in ZOHO_CLIENT_ID:
            logging.error("Cannot initiate Zoho auth flow. Client ID/Secret not configured.")
            return None

        auth_url = f"{ACCOUNTS_URL}/oauth/v2/auth?scope={SCOPES}&client_id={ZOHO_CLIENT_ID}&response_type=code&access_type=offline"
        print("--- Zoho First-Time Setup ---")
        print(f"1. Open this URL in your browser:\n{auth_url}")
        print("2. Grant access to your account.")
        print("3. You will be redirected to a page with a 'code' in the URL. Copy that code.")
        grant_token = input("4. Paste the 'code' here and press Enter: ").strip()

        if not grant_token:
            logging.error("No grant token provided. Zoho authentication cancelled.")
            return None

        try:
            response = requests.post(TOKEN_URL, params={
                'code': grant_token,
                'client_id': ZOHO_CLIENT_ID,
                'client_secret': ZOHO_CLIENT_SECRET,
                'grant_type': 'authorization_code'
            })
            response.raise_for_status()
            token_data = response.json()
            logging.info("Successfully obtained Zoho refresh token.")
            return token_data['refresh_token']
        except requests.exceptions.RequestException as e:
            logging.error(f"Error exchanging Zoho grant token: {e}")
            return None

    def fetch_events(self, start_date: datetime.datetime, end_date: datetime.datetime) -> List[Dict[str, Any]]:
        """Fetches events from the user's Zoho calendars."""
        access_token = self._get_access_token()
        if not access_token:
            logging.error("Cannot fetch Zoho events: Authentication failed.")
            return []

        headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
        
        # Zoho API requires time in a specific format with 'T' and 'Z'
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        params = {
            'from': start_date.strftime(time_format),
            'to': end_date.strftime(time_format)
        }

        try:
            # First, get the list of calendars
            cal_response = requests.get(f"{API_BASE_URL}/calendars", headers=headers)
            cal_response.raise_for_status()
            calendars = cal_response.json().get('calendars', [])

            all_events = []
            for calendar in calendars:
                cal_uid = calendar['uid']
                events_url = f"{API_BASE_URL}/calendars/{cal_uid}/events"
                events_response = requests.get(events_url, headers=headers, params=params)
                events_response.raise_for_status()
                events = events_response.json().get('events', [])
                all_events.extend([self._parse_event(e) for e in events])
            
            logging.info(f"Found {len(all_events)} total events in Zoho Calendar.")
            return all_events

        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while fetching Zoho events: {e}")
            return []

    def _parse_event(self, event: Dict) -> Dict[str, Any]:
        """Converts a Zoho Calendar API event object into our standard format."""
        return {
            'source': 'zoho',
            'id': event['uid'],
            'title': event.get('title', 'No Title'),
            'start_time': event.get('starttime'), # Zoho provides ISO 8601 format
            'end_time': event.get('endtime'),
            'attendees': [att['email'] for att in event.get('attendees', []) if 'email' in att],
            'location': event.get('location', None)
        }

    @staticmethod
    def disconnect():
        """Deletes the stored refresh token for Zoho Calendar."""
        logging.info("Disconnecting Zoho Calendar account.")
        AuthManager.delete_token(ACCOUNT_NAME)