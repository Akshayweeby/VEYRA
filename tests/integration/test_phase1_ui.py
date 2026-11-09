import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel

from veyra.settings import SettingsStore
from veyra.ui.hud import HudWindow
from veyra.ui.setup_wizard import SetupWizard


def test_hud_starts_camera_off_and_supports_collapse(tmp_path) -> None:
    QApplication.instance() or QApplication([])
    hud = HudWindow(SettingsStore(tmp_path / "settings.json"))
    assert hud.camera_on is False
    assert hud.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
    hud.toggle_collapsed()
    assert hud.collapsed is True
    hud.toggle_collapsed()
    assert hud.collapsed is False
    hud.close()


def test_setup_wizard_contains_future_phase_placeholders() -> None:
    QApplication.instance() or QApplication([])
    wizard = SetupWizard()
    assert wizard.pageCount() == 8
    assert "camera" in wizard.page(4).findChild(QLabel, "wizardTitle").text().lower()
    wizard.close()
