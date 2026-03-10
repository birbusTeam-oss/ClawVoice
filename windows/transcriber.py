import os


class Transcriber:
    def __init__(self, config):
        self.config = config
        self._recognizer = None

    def _get_recognizer(self):
        if self._recognizer is None:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
        return self._recognizer

    def transcribe(self, audio_path: str) -> tuple[str | None, str | None]:
        """Returns (text, error_message). One will be None."""
        if not os.path.exists(audio_path):
            return None, "Audio file not found"

        try:
            file_size = os.path.getsize(audio_path)
            if file_size < 1024:
                return None, None  # silence

            import speech_recognition as sr
            recognizer = self._get_recognizer()

            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)

            try:
                text = recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                return None, None  # silence / unintelligible
            except sr.RequestError as e:
                return None, f"Speech API unavailable: {e}"

            text = text.strip()
            if not text:
                return None, None

            return text, None

        except ImportError:
            return None, "SpeechRecognition not installed"
        except Exception as e:
            return None, f"Transcription error: {str(e)[:100]}"
