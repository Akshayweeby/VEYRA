from pathlib import Path

from veyra.settings import SettingsStore


def test_settings_round_trip_and_first_launch(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    settings = SettingsStore(path)
    assert settings.first_launch_complete is False

    settings.set("theme", "light")
    settings.mark_first_launch_complete()

    restored = SettingsStore(path)
    assert restored.first_launch_complete is True
    assert restored.theme == "light"
