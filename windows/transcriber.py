import os
import re
import logging

log = logging.getLogger("clawvoice")


def _clean_text(text: str) -> str:
    """Post-process transcription for cleaner output."""
    text = text.strip()
    if not text:
        return text

    # Capitalize first letter
    text = text[0].upper() + text[1:]

    # Capitalize after sentence-ending punctuation
    text = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)

    # Fix common spacing issues
    text = re.sub(r'\s+', ' ', text)  # collapse multiple spaces
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)  # no space before punctuation

    # Add period at end if no sentence-ending punctuation
    if text and text[-1] not in '.!?':
        text += '.'

    return text


class Transcriber:
    def __init__(self, config):
        self.config = config
        self._recognizer = None

    def _get_recognizer(self):
        if self._recognizer is None:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
            # Tune for voice dictation
            self._recognizer.energy_threshold = 300
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.pause_threshold = 0.6
        return self._recognizer

    def transcribe(self, audio_path: str) -> tuple[str | None, str | None]:
        """Returns (text, error_message). One will be None."""
        if not os.path.exists(audio_path):
            return None, "Audio file not found"

        try:
            file_size = os.path.getsize(audio_path)
            log.info(f"Audio: {file_size // 1024}KB")

            if file_size < 2000:
                return None, None  # silence

            import speech_recognition as sr
            recognizer = self._get_recognizer()

            with sr.AudioFile(audio_path) as source:
                # Adjust for ambient noise briefly
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = recognizer.record(source)

            log.info("Transcribing...")
            try:
                # Use show_all=False for best single result
                text = recognizer.recognize_google(
                    audio,
                    language="en-US",
                    show_all=False
                )
            except sr.UnknownValueError:
                log.info("No speech detected")
                return None, None
            except sr.RequestError as e:
                log.error(f"Speech API error: {e}")
                return None, f"Speech API error — check internet connection"

            if not text or not text.strip():
                return None, None

            # Clean up the transcription
            text = _clean_text(text)

            words = len(text.split())
            log.info(f"Got {words} words: {text[:60]}{'...' if len(text) > 60 else ''}")
            return text, None

        except ImportError as e:
            log.error(f"Import error: {e}")
            return None, f"Missing library: {e}"
        except Exception as e:
            log.error(f"Transcription error: {e}")
            return None, f"Transcription error: {str(e)[:80]}"
