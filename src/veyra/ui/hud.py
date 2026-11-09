"""Floating VEYRA HUD and Phase 1 UI-only controls."""

from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from veyra.settings import SettingsStore
from veyra.camera.controller import CameraController
from veyra.ui.settings_window import SettingsWindow
from veyra.ui.theme import apply_theme


SIZE_PRESETS = {"small": (330, 210), "medium": (410, 270), "large": (510, 330)}


class HudWindow(QMainWindow):
    """Always-on-top, draggable HUD with no hardware integrations."""

    def __init__(self, settings: SettingsStore, camera_controller: CameraController | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.camera_controller = camera_controller or CameraController(parent=self)
        self.camera_on = self.camera_controller.is_on
        self.gesture_locked = False
        self.collapsed = False
        self._drag_offset: QPoint | None = None
        self.setWindowTitle("VEYRA")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._build_ui()
        self.camera_controller.status_changed.connect(self._set_status)
        self.camera_controller.state_changed.connect(lambda state: setattr(self, "camera_on", state == "CAMERA_ON"))
        self.camera_controller.error.connect(self._show_camera_error)
        self._apply_size(str(self.settings.values["hud_size"]))
        self.details.setVisible(str(self.settings.values["hud_layout"]) == "detailed")
        self._restore_position()
        self.setWindowOpacity(int(self.settings.values["transparency"]) / 100)

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        self.card = QFrame()
        self.card.setObjectName("card")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(18, 14, 18, 16)

        titlebar = QFrame()
        titlebar.setObjectName("titlebar")
        title_layout = QHBoxLayout(titlebar)
        title_layout.setContentsMargins(12, 6, 8, 6)
        brand = QLabel("VEYRA")
        brand.setObjectName("brand")
        title_layout.addWidget(brand)
        title_layout.addStretch()
        collapse = QPushButton("—")
        collapse.setToolTip("Collapse HUD")
        collapse.clicked.connect(self.toggle_collapsed)
        title_layout.addWidget(collapse)
        close = QPushButton("×")
        close.clicked.connect(self.close)
        title_layout.addWidget(close)
        card_layout.addWidget(titlebar)

        tagline = QLabel("The Future Is in Your Hands.")
        tagline.setObjectName("tagline")
        card_layout.addWidget(tagline)
        self.status = QLabel("CAMERA OFF  •  CONTROLLER READY")
        self.status.setObjectName("status")
        card_layout.addWidget(self.status)

        self.details = QFrame()
        detail_layout = QVBoxLayout(self.details)
        detail_layout.setContentsMargins(0, 8, 0, 8)
        detail_layout.addWidget(QLabel("CURRENT GESTURE      —", objectName="muted"))
        detail_layout.addWidget(QLabel("LAST ACTION          —", objectName="muted"))
        detail_layout.addWidget(QLabel("FPS                  —", objectName="muted"))
        card_layout.addWidget(self.details)

        controls = QHBoxLayout()
        camera = QPushButton("Camera ON")
        camera.setObjectName("primary")
        camera.clicked.connect(self.request_camera_on)
        controls.addWidget(camera)
        lock = QPushButton("Lock")
        lock.clicked.connect(self.toggle_lock)
        controls.addWidget(lock)
        stop = QPushButton("Emergency Stop")
        stop.setObjectName("danger")
        stop.clicked.connect(self.emergency_stop)
        controls.addWidget(stop)
        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.open_settings)
        controls.addWidget(settings_button)
        card_layout.addLayout(controls)

        self.indicator = QPushButton("V  •  OFF")
        self.indicator.setObjectName("primary")
        self.indicator.clicked.connect(self.toggle_collapsed)
        self.indicator.hide()
        root_layout.addWidget(self.card)
        root_layout.addWidget(self.indicator)
        self.setCentralWidget(root)

    def _apply_size(self, preset: str) -> None:
        width, height = SIZE_PRESETS.get(preset, SIZE_PRESETS["medium"])
        self.setFixedSize(width, height)

    def _restore_position(self) -> None:
        stored = self.settings.values.get("hud_position")
        if isinstance(stored, list) and len(stored) == 2:
            self.move(int(stored[0]), int(stored[1]))
            return
        screen = QApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            self.move(available.right() - self.width() - 24, available.top() + 24)

    def _save_position(self) -> None:
        self.settings.set("hud_position", [self.x(), self.y()])

    def request_camera_on(self) -> None:
        answer = QMessageBox.question(
            self,
            "Turn camera on?",
            "VEYRA will request camera access in a future phase.\n\nPhase 1 keeps the camera OFF.",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        )
        if answer == QMessageBox.StandardButton.Ok:
            self.camera_controller.start()

    def emergency_stop(self) -> None:
        self.camera_controller.stop()
        self._set_status("CAMERA OFF  •  EMERGENCY STOP READY")

    def toggle_lock(self) -> None:
        self.gesture_locked = not self.gesture_locked
        self.status.setText("CAMERA OFF  •  GESTURES LOCKED" if self.gesture_locked else "CAMERA OFF  •  CONTROLLER READY")

    def toggle_collapsed(self) -> None:
        self.collapsed = not self.collapsed
        self.card.setVisible(not self.collapsed)
        self.indicator.setVisible(self.collapsed)
        if self.collapsed:
            self.setFixedSize(100, 46)
        else:
            self._apply_size(str(self.settings.values["hud_size"]))

    def open_settings(self) -> None:
        dialog = SettingsWindow(self.settings, self.camera_controller, self)
        dialog.themeChanged.connect(self._theme_changed)
        dialog.transparencyChanged.connect(lambda value: self.setWindowOpacity(value / 100))
        dialog.hudSizeChanged.connect(self._apply_size)
        dialog.hudLayoutChanged.connect(lambda value: self.details.setVisible(value == "detailed"))
        dialog.show()
        self._settings_dialog = dialog

    def _theme_changed(self, theme: str) -> None:
        apply_theme(QApplication.instance(), theme)

    def _set_status(self, status: str) -> None:
        self.status.setText(status)

    def _show_camera_error(self, message: str) -> None:
        QMessageBox.warning(self, "Camera unavailable", f"VEYRA could not start the selected camera.\n\n{message}\n\nCheck Windows camera permissions and that the device is not in use by another application.")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = None
            self._save_position()
        super().mouseReleaseEvent(event)

    def closeEvent(self, event) -> None:  # noqa: ANN001
        self.camera_controller.shutdown()
        self._save_position()
        super().closeEvent(event)
