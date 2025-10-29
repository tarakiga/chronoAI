"""
Google Calendar integration
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pickle
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from chronoai.utils.logger import get_logger

logger = get_logger(__name__)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendar:
    """Google Calendar integration service"""
    
    def __init__(self):
        self.credentials = None
        self.service = None
        self.connected = False
        
        logger.info("Google Calendar service initialized")
    
    def connect(self, credentials: Dict[str, Any]):
        """Connect to Google Calendar using OAuth2"""
        try:
            # Check if we have stored credentials
            token_file = 'token_google.pickle'
            
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # If there are no valid credentials, request authorization
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    # Use provided credentials or request new ones
                    if 'client_id' in credentials and 'client_secret' in credentials:
                        flow = InstalledAppFlow.from_client_config(
                            {
                                'installed': {
                                    'client_id': credentials['client_id'],
                                    'client_secret': credentials['client_secret'],
                                    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                                    'token_uri': 'https://oauth2.googleapis.com/token',
                                    'redirect_uris': ['http://localhost']
                                }
                            },
                            SCOPES
                        )
                        self.credentials = flow.run_local_server(port=0)
                    else:
                        # Fallback to default flow
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'credentials_google.json', SCOPES
                        )
                        self.credentials = flow.run_local_server(port=0)
                
                # Save the credentials for next run
                with open(token_file, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=self.credentials)
            self.connected = True
            
            logger.info("Connected to Google Calendar")
            
        except Exception as e:
            logger.error(f"Failed to connect to Google Calendar: {e}")
            self.connected = False
            raise
    
    def disconnect(self):
        """Disconnect from Google Calendar"""
        try:
            self.credentials = None
            self.service = None
            self.connected = False
            
            # Remove token file
            token_file = 'token_google.pickle'
            if os.path.exists(token_file):
                os.remove(token_file)
            
            logger.info("Disconnected from Google Calendar")
            
        except Exception as e:
            logger.error(f"Failed to disconnect from Google Calendar: {e}")
            raise
    
    def is_connected(self) -> bool:
        """Check if connected to Google Calendar"""
        return self.connected
    
    def get_events(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get events from Google Calendar"""
        try:
            if not self.connected:
                raise Exception("Not connected to Google Calendar")
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_time.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Parse datetime
                if 'T' in start:
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                else:
                    # All-day event
                    start_dt = datetime.fromisoformat(start)
                    end_dt = datetime.fromisoformat(end)
                
                formatted_event = {
                    'id': event.get('id'),
                    'title': event.get('summary', 'No Title'),
                    'description': event.get('description', ''),
                    'start_time': start_dt,
                    'end_time': end_dt,
                    'location': event.get('location', ''),
                    'attendees': [attendee.get('email', '') for attendee in event.get('attendees', [])],
                    'organizer': event.get('organizer', {}).get('email', ''),
                    'html_link': event.get('htmlLink', '')
                }
                
                formatted_events.append(formatted_event)
            
            logger.debug(f"Retrieved {len(formatted_events)} events from Google Calendar")
            return formatted_events
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            return []
        except Exception as e:
            logger.error(f"Failed to get events from Google Calendar: {e}")
            return []
    
    def sync(self):
        """Sync Google Calendar (no-op for read-only access)"""
        try:
            if not self.connected:
                raise Exception("Not connected to Google Calendar")
            
            # For read-only access, sync is just a no-op
            # We could fetch current time to verify connection
            now = self.service.events().list(
                calendarId='primary',
                timeMin=datetime.utcnow().isoformat() + 'Z',
                maxResults=1,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            logger.debug("Google Calendar sync completed")
            
        except Exception as e:
            logger.error(f"Failed to sync Google Calendar: {e}")
            raise