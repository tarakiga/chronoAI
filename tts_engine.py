import pyttsx3
import threading
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TTSEngine:
    """
    A thread-safe wrapper for the pyttsx3 text-to-speech engine.
    This class manages a single instance of the TTS engine and handles speaking
    tasks in a non-blocking manner, with support for stopping speech prematurely.

    This addresses requirements FR-NOT-03 (volume control) and the technical
    need to interrupt speech for FR-NOT-06.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # Singleton pattern to ensure only one engine instance exists.
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(TTSEngine, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # The __init__ might be called multiple times in a singleton,
        # so we use a flag to ensure initialization happens only once.
        if hasattr(self, '_initialized') and self._initialized:
            return

        with self._lock:
            if hasattr(self, '_initialized') and self._initialized:
                return

            logging.info("Initializing TTS Engine...")
            try:
                self.engine = pyttsx3.init()
                self._initialized = True
                self._is_speaking = False
                self._speech_thread = None
            except Exception as e:
                logging.error(f"Failed to initialize pyttsx3 engine: {e}")
                self._initialized = False
                self.engine = None

    def _speak_worker(self, text: str, volume: float):
        """
        Internal worker function that runs the speech synthesis in a separate thread.
        This prevents the main application from blocking.
        """
        if not self.engine:
            logging.error("TTS engine not available. Cannot speak.")
            return

        try:
            self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
            self.engine.say(text)
            self.engine.runAndWait()
        finally:
            with self._lock:
                self._is_speaking = False

    def speak(self, text: str, volume: float = 1.0):
        """
        Speaks the given text at the specified volume in a non-blocking manner.

        Args:
            text (str): The text to be spoken.
            volume (float): The volume, from 0.0 (silent) to 1.0 (full).
        """
        with self._lock:
            if self._is_speaking:
                logging.warning("TTS Engine is already speaking. New request ignored.")
                return

            if not self._initialized or not self.engine:
                logging.error("Cannot speak, TTS Engine is not initialized.")
                return

            self._is_speaking = True
            self._speech_thread = threading.Thread(target=self._speak_worker, args=(text, volume))
            self._speech_thread.start()

    def stop(self):
        """
        Stops the currently speaking audio immediately.
        """
        with self._lock:
            if not self._is_speaking or not self.engine:
                return

            logging.info("Stopping current speech.")
            # pyttsx3's stop command is thread-safe
            self.engine.stop()
            self._is_speaking = False

        # It's good practice to wait for the thread to finish
        if self._speech_thread and self._speech_thread.is_alive():
            self._speech_thread.join(timeout=1.0)