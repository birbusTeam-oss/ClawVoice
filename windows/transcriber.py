import os
import sys
import logging

log = logging.getLogger("clawvoice")


class Transcriber:
    def __init__(self, config):
        self.config = config
        self._recognizer = None

    def _get_recognizer(self):
        if self._recognizer is None:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
            # Reduce pause threshold for faster response
            self._recognizer.pause_threshold = 0.5
        return self._recognizer

    def transcribe(self, audio_path: str) -> tuple[str | None, str | None]:
        """Returns (text, error_message). One will be None."""
        if not os.path.exists(audio_path):
            return None, "Audio file not found"

        try:
            file_size = os.path.getsize(audio_path)
            log.info(f"Audio file: {file_size} bytes")

            if file_size < 2000:
                log.info("Too short, skipping")
                return None, None  # silence

            import speech_recognition as sr
            recognizer = self._get_recognizer()

            log.info("Loading audio file...")
            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
            log.info(f"Audio loaded, {len(audio.get_raw_data())} bytes raw")

            log.info("Sending to Google Speech API...")
            try:
                text = recognizer.recognize_google(audio, language="en-US")
            except sr.UnknownValueError:
                log.info("No speech detected")
                return None, None
            except sr.RequestError as e:
                log.error(f"Google API error: {e}")
                return None, f"Speech API error: {e}"

            text = text.strip()
            if not text:
                return None, None

            log.info(f"Got: '{text[:50]}...' ({len(text.split())} words)")
            return text, None

        except ImportError as e:
            log.error(f"Import error: {e}")
            return None, f"Missing library: {e}"
        except Exception as e:
            log.error(f"Transcription exception: {e}")
            return None, f"Transcription error: {str(e)[:100]}"
