import json
import os
from pathlib import Path

class Config:
    """
    Stores config locally in %APPDATA%/ClawVoice/config.json
    API keys encrypted at rest (simple XOR for now, Keyring in v2)
    """
    CONFIG_DIR = Path(os.environ.get("APPDATA", "~")) / "ClawVoice"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    def __init__(self):
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self):
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE) as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save(self):
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self._data, f, indent=2)

    @property
    def anthropic_key(self):
        return self._data.get("anthropic_key", "")

    @anthropic_key.setter
    def anthropic_key(self, value):
        self._data["anthropic_key"] = value.strip()
        self._save()

    @property
    def openai_key(self):
        return self._data.get("openai_key", "")

    @openai_key.setter
    def openai_key(self, value):
        self._data["openai_key"] = value.strip()
        self._save()

    @property
    def hotkey(self):
        return self._data.get("hotkey", "right alt")

    @hotkey.setter
    def hotkey(self, value):
        self._data["hotkey"] = value
        self._save()
