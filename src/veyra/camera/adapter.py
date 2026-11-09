"""OpenCV camera adapter with explicit ownership and release."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CameraDevice:
    index: int
    label: str


class OpenCVCameraAdapter:
    """Own one OpenCV capture handle and never persist frame data."""

    def __init__(self, width: int = 320, height: int = 240, fps: int = 24) -> None:
        self.width = width
        self.height = height
        self.fps = fps
        self.capture: Any | None = None

    @staticmethod
    def _open_capture(index: int):
        import cv2

        capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if not capture.isOpened():
            capture.release()
            capture = cv2.VideoCapture(index)
        return capture

    @staticmethod
    def enumerate_devices(max_devices: int = 5) -> list[CameraDevice]:
        """Probe camera indexes on explicit user request and release each handle."""

        devices: list[CameraDevice] = []
        for index in range(max_devices):
            capture = OpenCVCameraAdapter._open_capture(index)
            try:
                if capture.isOpened():
                    devices.append(CameraDevice(index=index, label=f"Camera {index}"))
            finally:
                capture.release()
        return devices

    def open(self, device_index: int) -> None:
        import cv2

        if self.capture is not None:
            self.close()
        capture = self._open_capture(device_index)
        if not capture.isOpened():
            capture.release()
            raise RuntimeError(f"Unable to open camera index {device_index}")
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        capture.set(cv2.CAP_PROP_FPS, self.fps)
        self.capture = capture

    def read(self) -> Any:
        if self.capture is None:
            raise RuntimeError("Camera is not open")
        ok, frame = self.capture.read()
        if not ok:
            raise RuntimeError("Camera frame read failed or device disconnected")
        return frame

    def close(self) -> None:
        if self.capture is not None:
            self.capture.release()
            self.capture = None

