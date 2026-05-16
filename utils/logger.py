"""Logging configuration for the IRCTC Train Ticket Analyzer.

Sets up dual-handler logging:
  - Console handler: INFO+ (or DEBUG if verbose)
  - File handler: WARNING+ with detailed formatting for post-mortem analysis
"""

import logging
import sys
from pathlib import Path

from utils.constants import ERROR_LOG_FILENAME


def setup_logger(
    output_dir: Path,
    verbose: bool = False,
) -> logging.Logger:
    """Configure and return the application logger.

    Args:
        output_dir: Directory where the error log file will be written.
        verbose: If True, console output includes DEBUG-level messages.

    Returns:
        Configured root logger instance.
    """
    logger = logging.getLogger("irctc_analyzer")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    # ---- Console handler (human-friendly) ----
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    # ---- File handler (detailed, for debugging) ----
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / ERROR_LOG_FILENAME

    file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.WARNING)
    file_fmt = logging.Formatter(
        fmt=(
            "[%(asctime)s]\n"
            "LEVEL: %(levelname)s\n"
            "MODULE: %(module)s\n"
            "MESSAGE: %(message)s\n"
            "%(separator)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_fmt)
    file_handler.addFilter(_SeparatorFilter())
    logger.addHandler(file_handler)

    return logger


class _SeparatorFilter(logging.Filter):
    """Injects a visual separator into every log record for readability."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.separator = "-" * 60  # type: ignore[attr-defined]
        return True
