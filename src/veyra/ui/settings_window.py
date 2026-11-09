"""Settings window for Phase 1 appearance preferences."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QFormLayout,
    QPushButton,
    QSlider,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from veyra.settings import SettingsStore
from veyra.camera.adapter import CameraDevice


class SettingsWindow(QMainWindow):
    themeChanged = Signal(str)
    transparencyChanged = Signal(int)
    hudSizeChanged = Signal(str)
    hudLayoutChanged = Signal(str)

    def __init__(self, settings: SettingsStore, camera_controller=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.camera_controller = camera_controller
        self.setWindowTitle("VEYRA Settings")
        self.setMinimumSize(760, 500)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QHBoxLayout(root)
        sidebar = QListWidget()
        sidebar.setFixedWidth(170)
        for label in ["General", "Camera", "Gestures", "Performance", "Appearance", "Developer"]:
            QListWidgetItem(label, sidebar)
        sidebar.setCurrentRow(0)
        self.pages = QStackedWidget()
        self.pages.addWidget(self._general_page())
        self.pages.addWidget(self._camera_page())
        self.pages.addWidget(self._placeholder_page("Gestures", "Gesture preferences will be implemented with recognition."))
        self.pages.addWidget(self._placeholder_page("Performance", "Benchmark and performance controls are future-phase features."))
        self.pages.addWidget(self._appearance_page())
        self.pages.addWidget(self._placeholder_page("Developer", "Developer diagnostics will be added in a later phase."))
        sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)
        layout.addWidget(sidebar)
        layout.addWidget(self.pages, 1)
        self.setCentralWidget(root)

    def _general_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("General")
        title.setObjectName("brand")
        layout.addWidget(title)
        layout.addWidget(QLabel("Local preferences are saved automatically.", objectName="muted"))
        layout.addStretch()
        return page

    def _placeholder_page(self, title_text: str, body: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel(title_text)
        title.setObjectName("brand")
        detail = QLabel(body)
        detail.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(detail)
        layout.addStretch()
        return page

    def _camera_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Camera")
        title.setObjectName("brand")
        layout.addWidget(title)
        description = QLabel("Select a webcam for the next confirmed Camera ON attempt. Refresh is the only action that probes devices.")
        description.setWordWrap(True)
        description.setObjectName("muted")
        layout.addWidget(description)
        form = QFormLayout()
        self.camera_combo = QComboBox()
        self.camera_combo.addItem("Default camera (0)", 0)
        self.camera_combo.currentIndexChanged.connect(self._camera_selected)
        form.addRow("Selected camera", self.camera_combo)
        layout.addLayout(form)
        refresh = QPushButton("Refresh available cameras")
        refresh.clicked.connect(self._refresh_cameras)
        layout.addWidget(refresh)
        note = QLabel("Camera state: OFF at startup. No camera is opened by this settings page until Refresh or a confirmed Camera ON action.")
        note.setWordWrap(True)
        note.setObjectName("muted")
        layout.addWidget(note)
        layout.addStretch()
        if self.camera_controller is not None:
            self.camera_controller.devices_changed.connect(self._set_camera_devices)
        return page

    def _refresh_cameras(self) -> None:
        if self.camera_controller is not None:
            self.camera_controller.enumerate_devices()

    def _set_camera_devices(self, devices: object) -> None:
        if not isinstance(devices, list):
            return
        self.camera_combo.blockSignals(True)
        self.camera_combo.clear()
        for device in devices:
            if isinstance(device, CameraDevice):
                self.camera_combo.addItem(device.label, device.index)
        self.camera_combo.blockSignals(False)

    def _camera_selected(self, index: int) -> None:
        if self.camera_controller is not None:
            device_index = self.camera_combo.itemData(index)
            if device_index is not None:
                self.camera_controller.select_device(int(device_index))

    def _appearance_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Appearance")
        title.setObjectName("brand")
        layout.addWidget(title)
        form = QFormLayout()

        theme = QComboBox()
        theme.addItems(["dark", "light"])
        theme.setCurrentText(self.settings.theme)
        theme.currentTextChanged.connect(lambda value: self._set_theme(value))
        form.addRow("Theme", theme)

        transparency = QSlider(Qt.Orientation.Horizontal)
        transparency.setRange(70, 100)
        transparency.setValue(int(self.settings.values["transparency"]))
        transparency.valueChanged.connect(self._set_transparency)
        form.addRow("HUD transparency", transparency)

        size = QComboBox()
        size.addItems(["small", "medium", "large"])
        size.setCurrentText(str(self.settings.values["hud_size"]))
        size.currentTextChanged.connect(self._set_hud_size)
        form.addRow("HUD size", size)

        layout_choice = QComboBox()
        layout_choice.addItems(["minimal", "detailed"])
        layout_choice.setCurrentText(str(self.settings.values["hud_layout"]))
        layout_choice.currentTextChanged.connect(self._set_hud_layout)
        form.addRow("HUD layout", layout_choice)
        layout.addLayout(form)
        layout.addStretch()
        return page

    def _set_value(self, key: str, value: object) -> None:
        self.settings.set(key, value)

    def _set_transparency(self, value: int) -> None:
        self._set_value("transparency", value)
        self.transparencyChanged.emit(value)

    def _set_hud_size(self, value: str) -> None:
        self._set_value("hud_size", value)
        self.hudSizeChanged.emit(value)

    def _set_hud_layout(self, value: str) -> None:
        self._set_value("hud_layout", value)
        self.hudLayoutChanged.emit(value)

    def _set_theme(self, theme: str) -> None:
        self.settings.set("theme", theme)
        self.themeChanged.emit(theme)
