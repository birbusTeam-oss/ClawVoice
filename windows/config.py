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
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except (json.JSONDecodeError, IOError) as e:
                print(f"Config load error (using defaults): {e}")
                try:
                    self.CONFIG_FILE.rename(self.CONFIG_FILE.with_suffix('.json.bak'))
                except Exception:
                    pass
        return {}

    def _save(self):
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self._data, f, indent=2)
        except IOError as e:
            print(f"Config save error: {e}")

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self._save()

    def is_first_run(self) -> bool:
        return not self.CONFIG_FILE.exists() or not self._data
