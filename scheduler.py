import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
import atexit

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Scheduler:
    """
    A singleton wrapper for the APScheduler BackgroundScheduler.
    This class manages scheduling, adding, and removing background jobs for the application,
    such as calendar syncs and notification triggers.
    """
    _instance = None
    _scheduler = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Scheduler, cls).__new__(cls)
            # daemon=True ensures the scheduler thread exits when the main app exits
            cls._scheduler = BackgroundScheduler(daemon=True)
            logging.info("Scheduler initialized.")
        return cls._instance

    def start(self):
        """Starts the background scheduler if it's not already running."""
        if not self._scheduler.running:
            self._scheduler.start()
            # Ensure the scheduler shuts down cleanly when the application exits
            atexit.register(self.shutdown)
            logging.info("Scheduler started.")

    def shutdown(self):
        """Shuts down the scheduler and waits for running jobs to complete."""
        if self._scheduler.running:
            logging.info("Shutting down scheduler.")
            self._scheduler.shutdown()

    def add_job(self, func, *args, **kwargs):
        """
        Adds a job to the scheduler.

        Args:
            func (callable): The function to execute.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments for the scheduler (e.g., trigger, id, run_date).

        Returns:
            str: The ID of the added job.
        """
        job = self._scheduler.add_job(func, *args, **kwargs)
        logging.info(f"Added job '{job.id}' with trigger: {job.trigger}")
        return job.id

    def remove_job(self, job_id: str):
        """
        Removes a job from the scheduler.

        Args:
            job_id (str): The ID of the job to remove.
        """
        try:
            self._scheduler.remove_job(job_id)
            logging.info(f"Successfully removed job '{job_id}'.")
        except JobLookupError:
            logging.warning(f"Could not remove job '{job_id}': Job not found.")

    def get_jobs(self):
        """Returns a list of all scheduled jobs."""
        return self._scheduler.get_jobs()