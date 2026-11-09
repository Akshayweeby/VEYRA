"""Installer-style first-launch setup wizard for Phase 1."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QVBoxLayout, QWidget


@dataclass(frozen=True)
class SetupStep:
    title: str
    heading: str
    body: str
    badge: str


STEPS = (
    SetupStep("Welcome", "Welcome to VEYRA Setup", "VEYRA is a private, local-first gesture controller for Windows.\n\nThis short setup path prepares your workspace and explains what will happen in later phases.", "PHASE 1 UI PREVIEW"),
    SetupStep("Compatibility", "Check your environment", "VEYRA will eventually check Windows, memory, processor capability, and display configuration before enabling tracking.", "FUTURE CHECK"),
    SetupStep("Benchmark", "Measure responsiveness before selecting an engine", "A 30-second benchmark will compare recognition candidates on your computer. The benchmark is intentionally not enabled in Phase 1.", "PLACEHOLDER"),
    SetupStep("Engine", "Choose the best measured engine", "The production engine will be selected from measured accuracy, latency, CPU, memory, and stability results.", "PLACEHOLDER"),
    SetupStep("Camera", "Configure your camera", "Camera selection, permission guidance, and device diagnostics will arrive in Phase 2. The camera remains OFF now.", "CAMERA OFF"),
    SetupStep("Calibration", "Prepare calibration", "Calibration will establish a reliable neutral pose and help tune tracking for your environment.", "PLACEHOLDER"),
    SetupStep("Practice", "Practice the gesture vocabulary", "A guided practice mode will be added with recognition. No gesture recognition runs during this setup.", "PLACEHOLDER"),
    SetupStep("Ready", "Your VEYRA workspace is ready", "You can open the HUD now. Camera access, gesture recognition, and Windows controls remain disabled until their approved phases.", "READY"),
)


class SetupPage(QWidget):
    """High-contrast content page used by the wizard."""

    def __init__(self, step: SetupStep) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(42, 36, 42, 28)
        layout.setSpacing(16)
        badge = QLabel(step.badge)
        badge.setObjectName("wizardBadge")
        layout.addWidget(badge, 0, Qt.AlignmentFlag.AlignLeft)
        title = QLabel(step.heading)
        title.setObjectName("wizardTitle")
        title.setWordWrap(True)
        layout.addWidget(title)
        rule = QFrame()
        rule.setObjectName("wizardRule")
        rule.setFixedHeight(3)
        layout.addWidget(rule)
        body = QLabel(step.body)
        body.setObjectName("wizardBody")
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(body)
        layout.addStretch(1)


class SetupWizard(QDialog):
    """Skippable installer-style setup shell; hardware work is deferred."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._index = 0
        self.setWindowTitle("VEYRA Setup")
        self.setMinimumSize(820, 520)
        self.resize(900, 570)
        self.setModal(True)
        self._build_ui()
        self._update_navigation()

    def _build_ui(self) -> None:
        self.setStyleSheet(
            """
            QDialog { background: #f6f8fa; }
            QFrame#wizardBrandPanel { background: #102a3a; }
            QLabel#wizardLogo { color: #70e7f5; font-size: 31pt; font-weight: 800; letter-spacing: 4px; }
            QLabel#wizardOrbit { color: #70e7f5; font-size: 58pt; font-weight: 300; }
            QLabel#wizardTagline { color: #b6d7df; font-size: 11pt; }
            QLabel#wizardPhase { color: #70e7f5; font-size: 9pt; font-weight: 700; letter-spacing: 1px; }
            QFrame#wizardContent { background: #ffffff; }
            QLabel#wizardBadge { color: #087d8e; font-size: 9pt; font-weight: 800; letter-spacing: 1px; }
            QLabel#wizardTitle { color: #172b36; font-size: 23pt; font-weight: 700; }
            QFrame#wizardRule { background: #33c8d8; border: none; }
            QLabel#wizardBody { color: #3c525d; font-size: 12pt; }
            QFrame#wizardFooter { background: #e9eef1; border-top: 1px solid #cbd7dc; }
            QPushButton { color: #17313e; background: #ffffff; border: 1px solid #9eb3bc; border-radius: 6px; padding: 9px 18px; min-width: 82px; }
            QPushButton:hover { background: #e4f7f9; border-color: #087d8e; }
            QPushButton#nextButton { color: #ffffff; background: #087d8e; border-color: #087d8e; font-weight: 700; }
            QPushButton#nextButton:hover { background: #0b9caf; }
            QPushButton#skipButton { color: #526873; background: transparent; border: none; }
            """
        )
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        brand_panel = QFrame()
        brand_panel.setObjectName("wizardBrandPanel")
        brand_panel.setFixedWidth(220)
        brand_layout = QVBoxLayout(brand_panel)
        brand_layout.setContentsMargins(26, 42, 26, 28)
        orbit = QLabel("◉")
        orbit.setObjectName("wizardOrbit")
        orbit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_layout.addWidget(orbit)
        logo = QLabel("VEYRA")
        logo.setObjectName("wizardLogo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_layout.addWidget(logo)
        tagline = QLabel("The Future Is\nin Your Hands.")
        tagline.setObjectName("wizardTagline")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_layout.addWidget(tagline)
        brand_layout.addStretch(1)
        phase = QLabel("SETUP WIZARD\nPHASE 1")
        phase.setObjectName("wizardPhase")
        phase.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_layout.addWidget(phase)

        content = QFrame()
        content.setObjectName("wizardContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        self.pages = QStackedWidget()
        for step in STEPS:
            self.pages.addWidget(SetupPage(step))
        content_layout.addWidget(self.pages)
        body.addWidget(brand_panel)
        body.addWidget(content, 1)
        outer.addLayout(body, 1)

        footer = QFrame()
        footer.setObjectName("wizardFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 12, 20, 12)
        self.step_label = QLabel()
        self.step_label.setStyleSheet("color: #607681; font-size: 10pt;")
        footer_layout.addWidget(self.step_label)
        footer_layout.addStretch(1)
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self._back)
        footer_layout.addWidget(self.back_button)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        footer_layout.addWidget(cancel)
        self.skip_button = QPushButton("Skip setup")
        self.skip_button.setObjectName("skipButton")
        self.skip_button.clicked.connect(self.reject)
        footer_layout.addWidget(self.skip_button)
        self.next_button = QPushButton("Next")
        self.next_button.setObjectName("nextButton")
        self.next_button.clicked.connect(self._next)
        footer_layout.addWidget(self.next_button)
        outer.addWidget(footer)

    def pageCount(self) -> int:
        return len(STEPS)

    def page(self, index: int) -> SetupPage:
        return self.pages.widget(index)  # type: ignore[return-value]

    def _back(self) -> None:
        if self._index > 0:
            self._index -= 1
            self.pages.setCurrentIndex(self._index)
            self._update_navigation()

    def _next(self) -> None:
        if self._index < self.pageCount() - 1:
            self._index += 1
            self.pages.setCurrentIndex(self._index)
            self._update_navigation()
        else:
            self.accept()

    def _update_navigation(self) -> None:
        self.step_label.setText(f"Step {self._index + 1} of {self.pageCount()}  •  {STEPS[self._index].title}")
        self.back_button.setEnabled(self._index > 0)
        self.next_button.setText("Finish" if self._index == self.pageCount() - 1 else "Next")
