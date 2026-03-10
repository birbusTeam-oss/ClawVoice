import os


class Transcriber:
    def __init__(self, config):
        self.config = config
        self._model = None
        self._model_type = None  # "faster_whisper" or "openai_whisper"

    def _get_model(self):
        if self._model is not None:
            return self._model, None

        try:
            from faster_whisper import WhisperModel
            # base model: ~150MB, good accuracy, runs fast on CPU
            self._model = WhisperModel("base", device="cpu", compute_type="int8")
            self._model_type = "faster_whisper"
            return self._model, None
        except ImportError:
            pass

        try:
            import whisper
            self._model = whisper.load_model("base")
            self._model_type = "openai_whisper"
            return self._model, None
        except ImportError:
            pass

        return None, "Whisper not installed — run: pip install faster-whisper"

    def transcribe(self, audio_path: str) -> tuple[str | None, str | None]:
        """Returns (text, error_message). One of them will be None."""
        if not os.path.exists(audio_path):
            return None, "Audio file not found"

        try:
            file_size = os.path.getsize(audio_path)

            # Skip near-silence (< 1KB)
            if file_size < 1024:
                return None, None  # silence, not an error

            model, err = self._get_model()
            if err:
                return None, err

            if self._model_type == "faster_whisper":
                segments, _info = model.transcribe(audio_path, beam_size=5, language="en")
                text = " ".join(seg.text.strip() for seg in segments).strip()
            else:
                # openai-whisper fallback
                import whisper
                result = model.transcribe(audio_path, language="en")
                text = result["text"].strip()

            if not text or text.lower() in ('[blank_audio]', '[silence]', ''):
                return None, None  # silence, not an error

            return text, None

        except Exception as e:
            return None, f"Transcription error: {str(e)[:80]}"
