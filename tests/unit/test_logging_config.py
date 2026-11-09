from pathlib import Path

from veyra.logging_config import configure_logging


def test_logging_uses_local_rotating_file(tmp_path: Path) -> None:
    log_path = configure_logging(tmp_path)

    assert log_path == tmp_path / "veyra.log"
    assert log_path.is_file()

