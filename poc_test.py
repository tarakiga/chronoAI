import time
import logging
from datetime import datetime, timedelta

from src.core.scheduler import Scheduler
from src.core.tts_engine import TTSEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_escalating_notification(user_name: str):
    """
    Executes the escalating audio notification sequence as defined in the PRD (FR-NOT-03).
    This function is designed to be called by the scheduler.
    """
    tts = TTSEngine()
    scheduler = Scheduler()

    # Define the sequence steps
    sequence = [
        {"text": f"Psst, {user_name}...", "volume": 0.2, "delay": 0},
        {"text": f"Hey {user_name}...", "volume": 0.4, "delay": 3.0}, # 1.5s for speech + 1.5s pause
        {"text": f"{user_name}!", "volume": 0.75, "delay": 3.0}, # 1.5s for speech + 1.5s pause
    ]

    base_time = datetime.now()
    current_delay = 0

    logging.info("--- Starting Escalating Notification Sequence ---")

    for i, step in enumerate(sequence):
        # We schedule each part of the sequence to run at a specific time.
        # This is more robust than using time.sleep() in a long-running function.
        run_time = base_time + timedelta(seconds=current_delay)
        scheduler.add_job(
            tts.speak,
            args=[step["text"], step["volume"]],
            id=f"notification_step_{i}",
            trigger='date',
            run_date=run_time
        )
        current_delay += step["delay"]

def main():
    """
    Main function to set up and run the proof-of-concept test.
    """
    # --- Configuration ---
    USER_NAME = "Alex"
    SECONDS_TO_WAIT_BEFORE_START = 5
    # -------------------

    scheduler = Scheduler()
    scheduler.start()

    notification_time = datetime.now() + timedelta(seconds=SECONDS_TO_WAIT_BEFORE_START)
    logging.info(f"Scheduling notification sequence to start at {notification_time.strftime('%H:%M:%S')}")

    scheduler.add_job(run_escalating_notification, args=[USER_NAME], trigger='date', run_date=notification_time)

    logging.info(f"Proof-of-concept script running. Waiting for scheduled job. Press Ctrl+C to exit.")
    try:
        # Keep the script alive to allow the background scheduler to run its jobs.
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Script interrupted. Shutting down.")
        scheduler.shutdown()

if __name__ == "__main__":
    main()