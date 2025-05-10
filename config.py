import json
import os
from pathlib import Path

class ConfigManager:
    _instance     = None
    SETTINGS_FILE = Path(__file__).parent / "settings.json"
    DEFAULTS = {
        "vt_api_key":         "",
        "db_path":            "blackice.db",
        "log_retention_days": 30
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        if self.SETTINGS_FILE.exists():
            try:
                self._data = json.loads(self.SETTINGS_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                self._data = self.DEFAULTS.copy()
        else:
            self._data = self.DEFAULTS.copy()
            self._save()

        for key in self.DEFAULTS:
            env_key = f"BLACKICE_{key.upper()}"
            if env_key in os.environ:
                self._data[key] = os.environ[env_key]

    def _save(self):
        try:
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4)
        except IOError:
            pass

    def get(self, key: str, default=None):
        if key in self._data:
            return self._data[key]
        if default is not None:
            return default
        return self.DEFAULTS.get(key)

    def set(self, key: str, value):
        self._data[key] = value
        self._save()

    def all(self):
        return self._data.copy()
