"""VEYRA application entry point for the Phase 1 UI shell."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from veyra.logging_config import configure_logging
from veyra.settings import SettingsStore
from veyra.camera.controller import CameraController
from veyra.ui.hud import HudWindow
from veyra.ui.setup_wizard import SetupWizard
from veyra.ui.theme import apply_theme

# Backward-compatible import name retained for the Phase 0 scaffold test.
PlaceholderWindow = HudWindow


def create_application() -> QApplication:
    """Create the Qt application without opening hardware or network resources."""

    configure_logging()
    return QApplication.instance() or QApplication(sys.argv)


def main() -> int:
    """Run the HUD and first-launch setup flow."""

    application = create_application()
    settings = SettingsStore()
    apply_theme(application, settings.theme)
    if not settings.first_launch_complete:
        wizard = SetupWizard()
        wizard.exec()
        settings.mark_first_launch_complete()
    camera_controller = CameraController()
    application.aboutToQuit.connect(camera_controller.shutdown)
    window = HudWindow(settings=settings, camera_controller=camera_controller)
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())

