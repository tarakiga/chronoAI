"""
Voice engine for text-to-speech functionality
"""

import logging
import threading
import platform
import pyttsx3
import os
from typing import List, Dict, Any

from chronoai.utils.logger import get_logger

logger = get_logger(__name__)

class VoiceEngine:
    """Engine for text-to-speech functionality"""
    
    def __init__(self):
        self.engine = None
        self.voices = {}
        self.current_voice_id = None
        self.is_initialized = False
        self.speaking_lock = threading.Lock()
        
        # Initialize the engine
        self._init_engine()
        
        logger.info("Voice engine initialized")
    
    def _init_engine(self):
        """Initialize the TTS engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            self.voices = {i: voice.name for i, voice in enumerate(voices)}
            
            # Set default voice (first available)
            if voices:
                self.current_voice_id = 0
                self.engine.setProperty('voice', voices[0].id)
            
            self.is_initialized = True
            logger.info(f"Voice engine initialized with {len(self.voices)} voices available")
            
        except Exception as e:
            logger.error(f"Failed to initialize voice engine: {e}")
            self.is_initialized = False
    
    def get_available_voices(self) -> Dict[int, str]:
        """Get list of available voices"""
        try:
            if not self.is_initialized:
                self._init_engine()
            
            return self.voices.copy()
            
        except Exception as e:
            logger.error(f"Failed to get available voices: {e}")
            return {}
    
    def set_voice(self, voice_id: int):
        """Set the voice to use"""
        try:
            if not self.is_initialized:
                self._init_engine()
            
            if voice_id in self.voices:
                self.engine.setProperty('voice', voice_id)
                self.current_voice_id = voice_id
                logger.info(f"Voice set to: {self.voices[voice_id]}")
            else:
                logger.warning(f"Voice ID {voice_id} not available")
                
        except Exception as e:
            logger.error(f"Failed to set voice: {e}")
    
    def speak(self, text: str, volume: float = 0.75, rate: int = 200):
        """
        Speak the given text with specified volume and rate
        
        Args:
            text: Text to speak
            volume: Volume level (0.0 to 1.0)
            rate: Speech rate (words per minute)
        """
        try:
            if not self.is_initialized:
                logger.warning("Voice engine not initialized, skipping speech")
                return
            
            if not text or not text.strip():
                logger.debug("Empty text, skipping speech")
                return
            
            with self.speaking_lock:
                # Set properties
                self.engine.setProperty('volume', volume)
                self.engine.setProperty('rate', rate)
                
                # Log speech
                logger.debug(f"Speaking: {text[:50]}{'...' if len(text) > 50 else ''}")
                
                # Speak in a separate thread to avoid blocking
                speech_thread = threading.Thread(
                    target=self._speak_thread,
                    args=(text,),
                    daemon=True
                )
                speech_thread.start()
                
        except Exception as e:
            logger.error(f"Failed to speak text: {e}")
    
    def _speak_thread(self, text: str):
        """Thread function for speaking"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            
        except Exception as e:
            logger.error(f"Error in speech thread: {e}")
    
    def stop_speaking(self):
        """Stop current speech"""
        try:
            if self.engine:
                self.engine.stop()
                logger.debug("Speech stopped")
                
        except Exception as e:
            logger.error(f"Failed to stop speaking: {e}")
    
    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        try:
            if not self.is_initialized or not self.engine:
                return False
            
            # pyttsx3 doesn't have a direct way to check if speaking
            # We'll return False as a default
            return False
            
        except Exception as e:
            logger.error(f"Failed to check speaking status: {e}")
            return False
    
    def set_rate(self, rate: int):
        """Set speech rate"""
        try:
            if not self.is_initialized:
                self._init_engine()
            
            self.engine.setProperty('rate', rate)
            logger.debug(f"Speech rate set to: {rate}")
            
        except Exception as e:
            logger.error(f"Failed to set speech rate: {e}")
    
    def set_volume(self, volume: float):
        """Set speech volume"""
        try:
            if not self.is_initialized:
                self._init_engine()
            
            # Clamp volume between 0.0 and 1.0
            volume = max(0.0, min(1.0, volume))
            self.engine.setProperty('volume', volume)
            logger.debug(f"Speech volume set to: {volume}")
            
        except Exception as e:
            logger.error(f"Failed to set speech volume: {e}")
    
    def get_current_voice(self) -> str:
        """Get current voice name"""
        try:
            if not self.is_initialized:
                self._init_engine()
            
            if self.current_voice_id is not None and self.current_voice_id in self.voices:
                return self.voices[self.current_voice_id]
            else:
                return "Unknown"
                
        except Exception as e:
            logger.error(f"Failed to get current voice: {e}")
            return "Unknown"
    
    def shutdown(self):
        """Shutdown the voice engine"""
        try:
            if self.engine:
                self.stop_speaking()
                # pyttsx3 doesn't have a proper shutdown method
                # We'll just set it to None
                self.engine = None
                self.is_initialized = False
                logger.info("Voice engine shutdown")
                
        except Exception as e:
            logger.error(f"Error during voice engine shutdown: {e}")