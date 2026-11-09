"""Local-only application logging for the Phase 0 scaffold."""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOGGER_NAME = "veyra"


def default_log_directory() -> Path:
    """Return a per-user local log directory without creating it."""

    local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return local_app_data / "VEYRA" / "logs"


def configure_logging(log_directory: Path | None = None) -> Path:
    """Configure a rotating file sink and stderr sink; return the log path.

    No network handlers or telemetry sinks are configured.
    """

    directory = log_directory or default_log_directory()
    directory.mkdir(parents=True, exist_ok=True)
    log_path = directory / "veyra.log"

    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return log_path

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    file_handler = RotatingFileHandler(
        log_path, maxBytes=1_000_000, backupCount=2, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.info("VEYRA logging initialized; local-only sinks enabled")
    return log_path

