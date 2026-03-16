"""
utils/logger.py
---------------
Structured logger — writes to console (INFO+) and rotating file (DEBUG+).

Usage in any module:
  from utils.logger import get_logger
  logger = get_logger(__name__)
  logger.info("Navigating to login page")
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from config.settings import LOGS_DIR


def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)

    # Guard: don't add handlers twice (happens with pytest-xdist parallel workers)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console — INFO and above (keeps terminal readable)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # Rotating file — DEBUG and above (full detail for debugging failures)
    log_path = LOGS_DIR / "automation.log"
    fh = RotatingFileHandler(
        log_path, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger
