"""
Zoho Calendar integration
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
import json

from chronoai.utils.logger import get_logger

logger = get_logger(__name__)

class ZohoCalendar:
    """Zoho Calendar integration service"""
    
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.client_id = None
        self.client_secret = None
        self.base_url = "https://calendar.zoho.com/api/v2"
        self.connected = False
        
        logger.info("Zoho Calendar service initialized")
    
    def connect(self, credentials: Dict[str, Any]):
        """Connect to Zoho Calendar using OAuth2"""
        try:
            # Store credentials
            self.client_id = credentials.get('client_id')
            self.client_secret = credentials.get('client_secret')
            self.access_token = credentials.get('access_token')
            self.refresh_token = credentials.get('refresh_token')
            
            # Validate required credentials
            if not all([self.client_id, self.client_secret, self.access_token]):
                raise ValueError("Missing required Zoho credentials")
            
            # Test connection by making a simple API call
            self._make_request('/me')
            
            self.connected = True
            logger.info("Connected to Zoho Calendar")
            
        except Exception as e:
            logger.error(f"Failed to connect to Zoho Calendar: {e}")
            self.connected = False
            raise
    
    def disconnect(self):
        """Disconnect from Zoho Calendar"""
        try:
            self.access_token = None
            self.refresh_token = None
            self.client_id = None
            self.client_secret = None
            self.connected = False
            
            logger.info("Disconnected from Zoho Calendar")
            
        except Exception as e:
            logger.error(f"Failed to disconnect from Zoho Calendar: {e}")
            raise
    
    def is_connected(self) -> bool:
        """Check if connected to Zoho Calendar"""
        return self.connected
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
        """Make authenticated request to Zoho Calendar API"""
        try:
            if not self.access_token:
                raise Exception("No access token available")
            
            headers = {
                'Authorization': f'Zoho-oauthtoken {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            url = self.base_url + endpoint
            
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle token refresh on 401
            if response.status_code == 401:
                if self.refresh_token:
                    self._refresh_access_token()
                    headers['Authorization'] = f'Zoho-oauthtoken {self.access_token}'
                    response = requests.get(url, headers=headers)
                else:
                    raise Exception("Access token expired and no refresh token available")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Zoho Calendar API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to make request to Zoho Calendar: {e}")
            raise
    
    def _refresh_access_token(self):
        """Refresh access token using refresh token"""
        try:
            if not self.refresh_token:
                raise Exception("No refresh token available")
            
            data = {
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token
            }
            
            response = requests.post(
                'https://accounts.zoho.com/oauth/v2/token',
                data=data
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            
            # Update refresh token if a new one is provided
            if 'refresh_token' in token_data:
                self.refresh_token = token_data['refresh_token']
            
            logger.debug("Zoho Calendar access token refreshed")
            
        except Exception as e:
            logger.error(f"Failed to refresh Zoho Calendar access token: {e}")
            raise
    
    def get_events(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get events from Zoho Calendar"""
        try:
            if not self.connected:
                raise Exception("Not connected to Zoho Calendar")
            
            # Format datetime for Zoho API
            start_str = start_time.strftime('%Y-%m-%dT%H:%M:%S%z')
            end_str = end_time.strftime('%Y-%m-%dT%H:%M:%S%z')
            
            params = {
                'from': start_str,
                'to': end_str
            }
            
            response = self._make_request('/events', method='GET', params=params)
            events = response.get('events', [])
            
            formatted_events = []
            for event in events:
                # Parse datetime strings (Zoho uses ISO format)
                start_dt = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(event['end_time'].replace('Z', '+00:00'))
                
                formatted_event = {
                    'id': event.get('event_id'),
                    'title': event.get('title', 'No Title'),
                    'description': event.get('description', ''),
                    'start_time': start_dt,
                    'end_time': end_dt,
                    'location': event.get('location', ''),
                    'attendees': [attendee.get('email', '') for attendee in event.get('attendees', [])],
                    'organizer': event.get('organizer_email', ''),
                    'html_link': event.get('html_link', '')
                }
                
                formatted_events.append(formatted_event)
            
            logger.debug(f"Retrieved {len(formatted_events)} events from Zoho Calendar")
            return formatted_events
            
        except Exception as e:
            logger.error(f"Failed to get events from Zoho Calendar: {e}")
            return []
    
    def sync(self):
        """Sync Zoho Calendar"""
        try:
            if not self.connected:
                raise Exception("Not connected to Zoho Calendar")
            
            # For Zoho, sync is just a no-op for read-only access
            # We could make a simple API call to verify connection
            self._make_request('/me')
            
            logger.debug("Zoho Calendar sync completed")
            
        except Exception as e:
            logger.error(f"Failed to sync Zoho Calendar: {e}")
            raise