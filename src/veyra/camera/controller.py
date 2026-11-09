"""Camera lifecycle state controller."""

from __future__ import annotations

from typing import Any, Callable

from PySide6.QtCore import QObject, Signal

from veyra.camera.adapter import CameraDevice, OpenCVCameraAdapter
from veyra.camera.worker import CameraWorker


class CameraController(QObject):
    state_changed = Signal(str)
    status_changed = Signal(str)
    error = Signal(str)
    fps_changed = Signal(float)
    devices_changed = Signal(object)

    def __init__(
        self,
        adapter_factory: Callable[[], Any] = OpenCVCameraAdapter,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.adapter_factory = adapter_factory
        self.selected_device = 0
        self.devices: list[CameraDevice] = [CameraDevice(0, "Default camera (0)")]
        self.state = "CAMERA_OFF"
        self.worker: CameraWorker | None = None

    @property
    def is_on(self) -> bool:
        return self.state == "CAMERA_ON"

    def enumerate_devices(self) -> list[CameraDevice]:
        try:
            devices = OpenCVCameraAdapter.enumerate_devices()
        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))
            devices = self.devices
        if devices:
            self.devices = devices
        self.devices_changed.emit(self.devices)
        return self.devices

    def select_device(self, device_index: int) -> None:
        if self.worker is not None and self.worker.isRunning():
            self.stop()
        self.selected_device = device_index
        self._set_state("CAMERA_OFF", "CAMERA OFF  •  READY")

    def start(self) -> bool:
        if self.state != "CAMERA_OFF" or self.worker is not None:
            return False
        self._set_state("CAMERA_STARTING", "CAMERA STARTING  •  CONNECTING")
        self.worker = CameraWorker(self.adapter_factory(), self.selected_device, self)
        self.worker.capture_started.connect(self._on_started)
        self.worker.capture_stopped.connect(self._on_stopped)
        self.worker.error.connect(self._on_error)
        self.worker.heartbeat.connect(self.fps_changed)
        self.worker.finished.connect(self._clear_worker)
        self.worker.start()
        return True

    def stop(self) -> None:
        if self.worker is None:
            self._set_state("CAMERA_OFF", "CAMERA OFF  •  READY")
            return
        self._set_state("CAMERA_STOPPING", "CAMERA STOPPING  •  RELEASING")
        self.worker.request_stop()

    def shutdown(self) -> None:
        self.stop()
        if self.worker is not None:
            self.worker.wait(3000)
        self._clear_worker()

    def _on_started(self) -> None:
        self._set_state("CAMERA_ON", "CAMERA ON  •  CAPTURING LOCALLY")

    def _on_stopped(self) -> None:
        self._set_state("CAMERA_OFF", "CAMERA OFF  •  READY")

    def _on_error(self, message: str) -> None:
        self.error.emit(message)
        self._set_state("CAMERA_OFF", "CAMERA OFF  •  CONNECTION FAILED")
        if self.worker is not None:
            self.worker.request_stop()

    def _set_state(self, state: str, status: str) -> None:
        self.state = state
        self.state_changed.emit(state)
        self.status_changed.emit(status)

    def _clear_worker(self) -> None:
        if self.worker is not None and self.worker.isRunning():
            return
        worker = self.worker
        self.worker = None
        if worker is not None:
            worker.deleteLater()
