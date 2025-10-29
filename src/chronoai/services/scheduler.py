"""
Scheduler service for managing calendar events and notifications
"""

import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from chronoai.utils.logger import get_logger
from chronoai.calendar.manager import CalendarManager

logger = get_logger(__name__)

class SchedulerService:
    """Service for scheduling calendar events and notifications"""
    
    def __init__(self, notification_service):
        self.notification_service = notification_service
        self.calendar_manager = CalendarManager()
        self.scheduler = BackgroundScheduler()
        self.events = []
        
        self.init_scheduler()
    
    def init_scheduler(self):
        """Initialize the scheduler with default jobs"""
        try:
            # Start the scheduler
            self.scheduler.start()
            
            # Schedule calendar sync every 10 minutes
            self.scheduler.add_job(
                self.sync_calendars,
                trigger=CronTrigger(minute="*/10"),
                id='calendar_sync',
                name='Sync Calendars',
                replace_existing=True
            )
            
            # Initial calendar sync
            self.sync_calendars()
            
            logger.info("Scheduler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {e}")
            raise
    
    def sync_calendars(self):
        """Sync calendars and schedule notifications"""
        try:
            logger.info("Starting calendar sync...")
            
            # Fetch events from all connected calendars
            self.events = self.calendar_manager.get_all_events()
            
            # Clear existing notification jobs
            try:
                self.scheduler.remove_job('calendar_sync')
            except:
                pass  # Job doesn't exist yet, which is fine
            
            # Schedule notifications for each event
            for event in self.events:
                self.schedule_event_notification(event)
            
            # Schedule notifications for each event
            for event in self.events:
                self.schedule_event_notification(event)
            
            logger.info(f"Synced {len(self.events)} events and scheduled notifications")
            
        except Exception as e:
            logger.error(f"Failed to sync calendars: {e}")
    
    def schedule_event_notification(self, event):
        """Schedule notification for a specific event"""
        try:
            # Calculate notification time (15 minutes before event by default)
            notification_time = event['start_time'] - timedelta(minutes=15)
            
            # Only schedule if notification time is in the future
            if notification_time > datetime.now():
                self.scheduler.add_job(
                    self.trigger_notification,
                    trigger=DateTrigger(run_date=notification_time),
                    args=[event],
                    id=f'notification_{event["id"]}',
                    name=f'Notification for {event["title"]}',
                    replace_existing=True
                )
                logger.debug(f"Scheduled notification for event: {event['title']} at {notification_time}")
            
        except Exception as e:
            logger.error(f"Failed to schedule notification for event {event.get('id', 'unknown')}: {e}")
    
    def trigger_notification(self, event):
        """Trigger notification for an event"""
        try:
            logger.info(f"Triggering notification for event: {event['title']}")
            self.notification_service.show_notification(event)
            
        except Exception as e:
            logger.error(f"Failed to trigger notification for event {event.get('id', 'unknown')}: {e}")
    
    def get_next_event(self):
        """Get the next upcoming event"""
        try:
            current_time = datetime.now()
            
            # Filter events that are in the future
            future_events = [
                event for event in self.events 
                if event['start_time'] > current_time
            ]
            
            # Sort by start time
            future_events.sort(key=lambda x: x['start_time'])
            
            if future_events:
                return future_events[0]
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get next event: {e}")
            return None
    
    def get_all_events(self):
        """Get all scheduled events"""
        return self.events
    
    def shutdown(self):
        """Shutdown the scheduler"""
        try:
            logger.info("Shutting down scheduler...")
            self.scheduler.shutdown(wait=True)
            logger.info("Scheduler shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {e}")