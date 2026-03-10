import json
import os
import re
from pathlib import Path


class Config:
    CONFIG_DIR = Path(os.environ.get("APPDATA", "~")) / "ClawVoice"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    KEY_PATTERN = re.compile(r'^sk-ant-[a-zA-Z0-9\-_]{20,}$')

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
                # Back up corrupted config
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

    @property
    def anthropic_key(self):
        return self._data.get("anthropic_key", "")

    @anthropic_key.setter
    def anthropic_key(self, value):
        self._data["anthropic_key"] = value.strip()
        self._save()

    def is_valid_key(self, key: str) -> bool:
        return bool(self.KEY_PATTERN.match(key.strip()))

    def get_api_key(self) -> str:
        return self.anthropic_key

    def set_api_key(self, key: str):
        self.anthropic_key = key

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self._save()

    def is_first_run(self) -> bool:
        """True if config file didn't exist before this session."""
        return not self.CONFIG_FILE.exists() or not self._data
