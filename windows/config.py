import json
import os
from pathlib import Path


class Config:
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
