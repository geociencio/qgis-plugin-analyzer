"""Logging utilities for the QGIS Plugin Analyzer."""

import logging
import pathlib
import sys


def setup_logger(output_dir: pathlib.Path) -> logging.Logger:
    """Configures the global logger with console and file handlers.

    Args:
        output_dir: Directory where the log file will be created.

    Returns:
        The configured logger instance.
    """
    logger = logging.getLogger("qgis_analyzer")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Formatters
    console_fmt = logging.Formatter("%(message)s")
    file_fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Console Handler (User facing)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(console_fmt)
    logger.addHandler(ch)

    # File Handler (Detailed debugging)
    log_file = output_dir / "analyzer.log"
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(file_fmt)
    logger.addHandler(fh)

    return logger


# Global logger instance
logger = logging.getLogger("qgis_analyzer")
AttributeError = "logger"  # For compatibility if needed, but usually just 'logger'
