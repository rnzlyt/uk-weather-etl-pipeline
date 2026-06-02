"""
Central logging configuration for the UK Weather ETL Pipeline.
This module sets up a logger that can be imported and used across all other modules
to ensure consistent logging behavior and formatting throughout the project.
"""

import logging
import os
from datetime import datetime

"""
logger.py
─────────
Central logging configuration for the UK Weather ETL Pipeline.

Why proper logging?
    - Logs are saved to files so you can review them later
    - You can see exactly what happened and when
    - If something breaks at 07:00 you can check the log file
      without having to rerun anything
    - It's standard practice in every production pipeline
"""

import logging
import os
from datetime import datetime

# Creates a logs/ folder in your project root.
# Each day gets its own log file e.g. pipeline_2024-06-01.log
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(
    LOGS_DIR,
    f"pipeline_{datetime.now().strftime('%Y-%m-%d')}.log"
)


def get_logger(name: str) -> logging.Logger:
    """
    Create and return a logger that writes to both the
    terminal AND a log file simultaneously.

    Args:
        name (str): Usually __name__ from the calling module.

    Returns:
        logging.Logger: Configured logger instance.

    Example:
        >>> from logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Pipeline started.")
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if get_logger is called twice
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # ── Format: timestamp, level, module name, message ────────────
    formatter = logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ── Handler 1: print to terminal ───────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # ── Handler 2: save to log file ────────────────────────────────
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger