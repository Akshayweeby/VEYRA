import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

from veyra.camera.controller import CameraController


class FakeCamera:
    def __init__(self) -> None:
        self.opened = False
        self.closed = False
        self.reads = 0

    def open(self, device_index: int) -> None:
        self.opened = True

    def read(self):
        self.reads += 1
        time.sleep(0.005)
        return object()

    def close(self) -> None:
        self.closed = True


class FailingCamera(FakeCamera):
    def open(self, device_index: int) -> None:
        raise RuntimeError("mock camera unavailable")


def app():
    return QApplication.instance() or QApplication([])


def wait_for_events(milliseconds: int = 250) -> None:
    application = app()
    QTest.qWait(milliseconds)
    application.processEvents()


def wait_until(predicate, timeout: int = 2000) -> None:  # noqa: ANN001
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline and not predicate():
        wait_for_events(50)


def test_camera_starts_off_and_worker_releases_adapter() -> None:
    app()
    adapter = FakeCamera()
    controller = CameraController(lambda: adapter)
    assert controller.state == "CAMERA_OFF"
    assert controller.start() is True
    try:
        wait_until(lambda: controller.state == "CAMERA_ON")
        assert controller.state == "CAMERA_ON"
        assert adapter.opened is True
        controller.stop()
        wait_until(lambda: controller.state == "CAMERA_OFF" and adapter.closed)
        assert controller.state == "CAMERA_OFF"
        assert adapter.closed is True
    finally:
        controller.shutdown()


def test_camera_failure_returns_to_off() -> None:
    app()
    controller = CameraController(FailingCamera)
    controller.start()
    try:
        wait_until(lambda: controller.state == "CAMERA_OFF" and controller.worker is None)
        assert controller.state == "CAMERA_OFF"
    finally:
        controller.shutdown()


def test_selecting_camera_keeps_new_device_off() -> None:
    app()
    adapter = FakeCamera()
    controller = CameraController(lambda: adapter)
    controller.start()
    try:
        wait_until(lambda: controller.state == "CAMERA_ON")
        controller.select_device(1)
        assert controller.selected_device == 1
        assert controller.state == "CAMERA_OFF"
    finally:
        controller.shutdown()
