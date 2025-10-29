import unittest
from unittest.mock import patch, MagicMock
import datetime

# We need to add the project root to the path for the import to work
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.event_manager import EventManager

class TestEventManager(unittest.TestCase):

    @patch('src.core.event_manager.AuthManager')
    @patch('src.core.event_manager.ZohoCalendarService')
    @patch('src.core.event_manager.GoogleCalendarService')
    def test_get_unified_events_merges_and_sorts_correctly(
        self, MockGoogleService, MockZohoService, MockAuthManager
    ):
        """
        Tests that get_unified_events correctly merges events from multiple
        sources and sorts them chronologically by start_time.
        """
        # --- 1. Setup Mocks ---

        # Mock AuthManager to simulate both accounts being connected
        MockAuthManager.get_token.return_value = 'dummy_token'

        # Mock calendar services instances
        mock_google_instance = MockGoogleService.return_value
        mock_zoho_instance = MockZohoService.return_value

        # Define mock event data (out of order)
        mock_google_events = [
            {
                'source': 'google', 'id': 'g1', 'title': 'Google Meeting',
                'start_time': '2023-10-27T10:00:00-07:00'
            },
            {
                'source': 'google', 'id': 'g2', 'title': 'Google Lunch',
                'start_time': '2023-10-27T14:00:00-07:00'
            }
        ]
        mock_zoho_events = [
            {
                'source': 'zoho', 'id': 'z1', 'title': 'Zoho Standup',
                'start_time': '2023-10-27T09:00:00-07:00'
            },
            {
                'source': 'zoho', 'id': 'z2', 'title': 'Zoho Sync',
                'start_time': '2023-10-27T11:00:00-07:00'
            }
        ]

        # Configure the fetch_events methods to return our mock data
        mock_google_instance.fetch_events.return_value = mock_google_events
        mock_zoho_instance.fetch_events.return_value = mock_zoho_events

        # --- 2. Execute the Method Under Test ---

        event_manager = EventManager()
        # The date range doesn't matter here as the mock returns fixed data
        unified_events = event_manager.get_unified_events(datetime.datetime.now(), datetime.datetime.now())

        # --- 3. Assert the Results ---

        # Check that all events were merged
        self.assertEqual(len(unified_events), 4)

        # Check that the events are sorted correctly by start_time
        self.assertEqual(unified_events[0]['id'], 'z1') # 09:00
        self.assertEqual(unified_events[1]['id'], 'g1') # 10:00
        self.assertEqual(unified_events[2]['id'], 'z2') # 11:00
        self.assertEqual(unified_events[3]['id'], 'g2') # 14:00

if __name__ == '__main__':
    unittest.main()