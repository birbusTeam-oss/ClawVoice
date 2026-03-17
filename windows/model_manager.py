"""
ModelManager -- handles faster-whisper model lifecycle.
Downloads model on first use, caches locally, loads once at startup.
"""
import os
import logging
from pathlib import Path

log = logging.getLogger("clawvoice")

MODEL_DIR = Path(os.environ.get("APPDATA", os.path.expanduser("~"))) / "ClawVoice" / "models"

# Available models: tiny.en, base.en, small.en
DEFAULT_MODEL = "base.en"


class ModelManager:
    def __init__(self, config):
        self.config = config
        self._model = None
        self._model_name = config.get("model", DEFAULT_MODEL)
        MODEL_DIR.mkdir(parents=True, exist_ok=True)

    @property
    def model_name(self):
        return self._model_name

    def load(self):
        """Load the whisper model. Call at startup."""
        try:
            from faster_whisper import WhisperModel
            log.info(f"Loading whisper model: {self._model_name}")

            # Try GPU first, fallback to CPU
            try:
                self._model = WhisperModel(
                    self._model_name,
                    device="cuda",
                    compute_type="float16",
                    download_root=str(MODEL_DIR)
                )
                log.info(f"Model loaded on GPU (CUDA)")
            except Exception:
                self._model = WhisperModel(
                    self._model_name,
                    device="cpu",
                    compute_type="int8",
                    download_root=str(MODEL_DIR)
                )
                log.info(f"Model loaded on CPU")

            return True
        except ImportError:
            log.error("faster-whisper not installed. Run: pip install faster-whisper")
            return False
        except Exception as e:
            log.error(f"Model load failed: {e}")
            return False

    def get_model(self):
        """Return loaded model, loading if needed."""
        if self._model is None:
            self.load()
        return self._model

    def change_model(self, model_name: str):
        """Switch to a different model size."""
        self._model_name = model_name
        self._model = None
        self.config.set("model", model_name)
        return self.load()

    def is_loaded(self):
        return self._model is not None
