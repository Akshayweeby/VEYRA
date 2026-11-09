"""Dedicated camera capture thread."""

from __future__ import annotations

import threading
import time
from typing import Any

from PySide6.QtCore import QThread, Signal


class CameraWorker(QThread):
    """Owns one adapter and runs capture outside the UI thread."""

    capture_started = Signal()
    capture_stopped = Signal()
    error = Signal(str)
    heartbeat = Signal(float)

    def __init__(self, adapter: Any, device_index: int, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)
        self.adapter = adapter
        self.device_index = device_index
        self._stop_event = threading.Event()

    def run(self) -> None:
        try:
            self.adapter.open(self.device_index)
            self.capture_started.emit()
            frames = 0
            started_at = time.monotonic()
            last_report = started_at
            while not self._stop_event.is_set():
                self.adapter.read()
                frames += 1
                now = time.monotonic()
                if now - last_report >= 1.0:
                    self.heartbeat.emit(frames / max(now - started_at, 0.001))
                    last_report = now
        except Exception as exc:  # noqa: BLE001
            if not self._stop_event.is_set():
                self.error.emit(str(exc))
        finally:
            self.adapter.close()
            self.capture_stopped.emit()

    def request_stop(self) -> None:
        self._stop_event.set()
