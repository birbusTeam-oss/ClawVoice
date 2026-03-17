"""
Transcriber - offline-only using faster-whisper.
Zero cloud dependencies. Zero API keys.
"""
import os
import re
import logging

log = logging.getLogger("clawvoice")


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
    def __init__(self, config, model_manager=None):
        self.config = config
        self._model_manager = model_manager

    def transcribe(self, audio_path: str) -> tuple[str | None, str | None]:
        if not os.path.exists(audio_path):
            return None, "Audio file not found"

        file_size = os.path.getsize(audio_path)
        if file_size < 2000:
            return None, None

        # VAD check - skip silence
        try:
            from vad import has_speech
            if not has_speech(audio_path):
                log.info("VAD: no speech detected, skipping transcription")
                return None, None
        except ImportError:
            pass  # VAD not available, transcribe anyway

        # Try offline (faster-whisper) with model manager
        if self._model_manager and self._model_manager.is_loaded():
            return self._transcribe_offline(audio_path)

        # Try to load model via manager
        if self._model_manager:
            if self._model_manager.load():
                return self._transcribe_offline(audio_path)

        # Try faster-whisper standalone (no model manager)
        try:
            return self._transcribe_offline_standalone(audio_path)
        except ImportError:
            return None, "faster-whisper not installed. Run: pip install faster-whisper"

    def _transcribe_offline(self, audio_path: str) -> tuple[str | None, str | None]:
        try:
            model = self._model_manager.get_model()
            if model is None:
                return None, "Model not loaded"

            segments, info = model.transcribe(
                audio_path,
                beam_size=5,
                language="en",
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                    speech_pad_ms=200,
                ),
            )

            text = " ".join(seg.text for seg in segments).strip()
            if not text:
                return None, None

            text = _clean_text(text)
            words = len(text.split())
            log.info(f"Offline: {words} words: {text[:60]}{'...' if len(text) > 60 else ''}")
            return text, None

        except Exception as e:
            log.error(f"Offline transcription error: {e}")
            return None, f"Transcription error: {str(e)[:80]}"

    def _transcribe_offline_standalone(self, audio_path: str) -> tuple[str | None, str | None]:
        """Use faster-whisper without ModelManager."""
        from faster_whisper import WhisperModel
        from model_manager import MODEL_DIR, DEFAULT_MODEL

        model_name = self.config.get("model", DEFAULT_MODEL)
        model = WhisperModel(model_name, device="cpu", compute_type="int8",
                           download_root=str(MODEL_DIR))

        segments, info = model.transcribe(audio_path, beam_size=5, language="en",
                                          vad_filter=True)
        text = " ".join(seg.text for seg in segments).strip()
        if not text:
            return None, None
        text = _clean_text(text)
        log.info(f"Offline (standalone): {len(text.split())} words")
        return text, None
