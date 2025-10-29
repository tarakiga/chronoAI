import datetime
import logging
from typing import List, Dict, Any

from dateutil import parser

from src.services.google_cal import GoogleCalendarService
from src.services.zoho_cal import ZohoCalendarService
from src.services.auth_manager import AuthManager

class EventManager:
    """
    Manages fetching, merging, and sorting events from all connected calendar services.
    This class fulfills FR-CAL-05.
    """

    def __init__(self):
        self.google_service = GoogleCalendarService()
        self.zoho_service = ZohoCalendarService()

    def get_unified_events(self, start_date: datetime.datetime, end_date: datetime.datetime) -> List[Dict[str, Any]]:
        """
        Fetches events from all connected and configured calendar services,
        merges them, and sorts them chronologically.

        Args:
            start_date: The start of the time window to fetch events for.
            end_date: The end of the time window.

        Returns:
            A single list of event dictionaries, sorted by start time.
        """
        all_events = []

        # Fetch from Google if a token exists in the keyring
        if AuthManager.get_token('google'):
            logging.info("Fetching events from Google Calendar.")
            google_events = self.google_service.fetch_events(start_date, end_date)
            all_events.extend(google_events)
        else:
            logging.info("Google account not connected. Skipping.")

        # Fetch from Zoho if a token exists in the keyring
        if AuthManager.get_token('zoho'):
            logging.info("Fetching events from Zoho Calendar.")
            zoho_events = self.zoho_service.fetch_events(start_date, end_date)
            all_events.extend(zoho_events)
        else:
            logging.info("Zoho account not connected. Skipping.")

        if not all_events:
            return []

        # Normalize and sort
        try:
            # The key to robust sorting is parsing the datetime strings into actual datetime objects.
            # dateutil.parser is excellent at handling various ISO 8601 formats from different APIs.
            all_events.sort(key=lambda event: parser.isoparse(event['start_time']))
            logging.info(f"Successfully merged and sorted {len(all_events)} events.")
        except (parser.ParserError, TypeError) as e:
            logging.error(f"Could not sort events due to a datetime parsing error: {e}")
            # Return unsorted list in case of parsing failure to avoid crashing

        return all_events