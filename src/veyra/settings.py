"""Small local JSON settings store used by the Phase 1 UI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


DEFAULT_SETTINGS: dict[str, Any] = {
    "first_launch_complete": False,
    "theme": "dark",
    "transparency": 96,
    "hud_size": "medium",
    "hud_layout": "detailed",
    "hud_position": None,
}


def default_settings_path() -> Path:
    local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return local_app_data / "VEYRA" / "settings.json"


class SettingsStore:
    """Persist ordinary UI preferences locally as JSON."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_settings_path()
        self.values = dict(DEFAULT_SETTINGS)
        self.load()

    @property
    def first_launch_complete(self) -> bool:
        return bool(self.values["first_launch_complete"])

    @property
    def theme(self) -> str:
        return str(self.values["theme"])

    def load(self) -> None:
        if not self.path.is_file():
            return
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                self.values.update({key: loaded[key] for key in DEFAULT_SETTINGS if key in loaded})
        except (OSError, json.JSONDecodeError):
            self.values = dict(DEFAULT_SETTINGS)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.values, indent=2) + "\n", encoding="utf-8")

    def set(self, key: str, value: Any) -> None:
        if key not in DEFAULT_SETTINGS:
            raise KeyError(key)
        self.values[key] = value
        self.save()

    def mark_first_launch_complete(self) -> None:
        self.values["first_launch_complete"] = True
        self.save()
