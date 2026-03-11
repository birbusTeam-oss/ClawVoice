import os
import re
import logging

log = logging.getLogger("clawvoice")

# Module-level cached recognizer — loaded once, used forever
_recognizer = None

def _get_recognizer():
    global _recognizer
    if _recognizer is None:
        import speech_recognition as sr
        _recognizer = sr.Recognizer()
        _recognizer.energy_threshold = 300
        _recognizer.dynamic_energy_threshold = True
        _recognizer.pause_threshold = 0.6
    return _recognizer


def _clean_text(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    text = text[0].upper() + text[1:]
    text = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    if text and text[-1] not in '.!?':
        text += '.'
    return text


class Transcriber:
    def __init__(self, config):
        self.config = config

    def transcribe(self, audio_path: str) -> tuple[str | None, str | None]:
        if not os.path.exists(audio_path):
            return None, "Audio file not found"

        try:
            file_size = os.path.getsize(audio_path)
            log.info(f"Audio: {file_size // 1024}KB")

            if file_size < 2000:
                return None, None

            import speech_recognition as sr
            recognizer = _get_recognizer()

            with sr.AudioFile(audio_path) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.15)
                audio = recognizer.record(source)

            log.info("Transcribing...")
            try:
                text = recognizer.recognize_google(audio, language="en-US")
            except sr.UnknownValueError:
                log.info("No speech detected")
                return None, None
            except sr.RequestError as e:
                log.error(f"Speech API error: {e}")
                return None, f"Speech API error — check internet"

            if not text or not text.strip():
                return None, None

            text = _clean_text(text)
            words = len(text.split())
            log.info(f"Got {words} words: {text[:60]}{'...' if len(text) > 60 else ''}")
            return text, None

        except ImportError as e:
            return None, f"Missing library: {e}"
        except Exception as e:
            log.error(f"Transcription error: {e}")
            return None, f"Transcription error: {str(e)[:80]}"
