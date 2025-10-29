"""
Calendar manager for handling multiple calendar integrations
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from chronoai.utils.logger import get_logger
from chronoai.calendar.google_calendar import GoogleCalendar
from chronoai.calendar.zoho_calendar import ZohoCalendar

logger = get_logger(__name__)

class CalendarManager:
    """Manager for handling multiple calendar integrations"""
    
    def __init__(self):
        self.google_calendar = GoogleCalendar()
        self.zoho_calendar = ZohoCalendar()
        self.calendars = {
            'google': self.google_calendar,
            'zoho': self.zoho_calendar
        }
        
        logger.info("Calendar manager initialized")
    
    def connect_calendar(self, provider: str, credentials: Dict[str, Any]):
        """Connect to a calendar provider"""
        try:
            if provider not in self.calendars:
                raise ValueError(f"Unsupported calendar provider: {provider}")
            
            calendar_service = self.calendars[provider]
            calendar_service.connect(credentials)
            
            logger.info(f"Connected to {provider} calendar")
            
        except Exception as e:
            logger.error(f"Failed to connect to {provider} calendar: {e}")
            raise
    
    def disconnect_calendar(self, provider: str):
        """Disconnect from a calendar provider"""
        try:
            if provider not in self.calendars:
                raise ValueError(f"Unsupported calendar provider: {provider}")
            
            calendar_service = self.calendars[provider]
            calendar_service.disconnect()
            
            logger.info(f"Disconnected from {provider} calendar")
            
        except Exception as e:
            logger.error(f"Failed to disconnect from {provider} calendar: {e}")
            raise
    
    def get_all_events(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get all events from all connected calendars"""
        try:
            all_events = []
            current_time = datetime.now()
            end_time = current_time + timedelta(days=days_ahead)
            
            # Get events from each calendar
            for provider, calendar_service in self.calendars.items():
                if calendar_service.is_connected():
                    try:
                        events = calendar_service.get_events(current_time, end_time)
                        # Add provider info to events
                        for event in events:
                            event['provider'] = provider
                        
                        all_events.extend(events)
                        logger.debug(f"Retrieved {len(events)} events from {provider} calendar")
                        
                    except Exception as e:
                        logger.error(f"Failed to get events from {provider} calendar: {e}")
            
            # Sort events by start time
            all_events.sort(key=lambda x: x['start_time'])
            
            logger.info(f"Retrieved {len(all_events)} total events from all calendars")
            return all_events
            
        except Exception as e:
            logger.error(f"Failed to get all events: {e}")
            return []
    
    def get_connected_calendars(self) -> List[str]:
        """Get list of connected calendar providers"""
        try:
            connected = []
            for provider, calendar_service in self.calendars.items():
                if calendar_service.is_connected():
                    connected.append(provider)
            
            return connected
            
        except Exception as e:
            logger.error(f"Failed to get connected calendars: {e}")
            return []
    
    def sync_calendars(self):
        """Force sync all calendars"""
        try:
            logger.info("Starting calendar sync...")
            
            for provider, calendar_service in self.calendars.items():
                if calendar_service.is_connected():
                    try:
                        calendar_service.sync()
                        logger.debug(f"Synced {provider} calendar")
                    except Exception as e:
                        logger.error(f"Failed to sync {provider} calendar: {e}")
            
            logger.info("Calendar sync completed")
            
        except Exception as e:
            logger.error(f"Failed to sync calendars: {e}")