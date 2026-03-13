"""Logging utility with automatic daily rotation and cleanup.

This module provides a Logger class that writes log messages to both a file
(with daily rotation) and the console.
"""

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class Logger:
    """Logger that writes messages to a rotating file and prints to console.

    Attributes:
        log_file: Path to the log file (will rotate daily).
    """

    def __init__(self, log_file: Path, backup_count: int = 30) -> None:
        """Initialize the logger.

        Args:
            log_file: Path to the log file where messages will be written.
            backup_count: Number of old log files to keep (default: 30 days).
        """
        self.log_file = log_file
        self.backup_count = backup_count
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Set up Python's standard logger with file and console handlers."""
        logger = logging.getLogger("scacchi_bot")
        logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers if Logger is instantiated multiple times
        if logger.handlers:
            return logger

        # File handler with daily rotation, keeping 30 days of backups
        file_handler = TimedRotatingFileHandler(
            filename=self.log_file,
            when="midnight",
            interval=1,
            backupCount=self.backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Formatter: [YYYY-MM-DD HH:MM:SS] [LEVEL] message
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        formatter.datefmt = "%Y-%m-%d %H:%M:%S"
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self.logger.error(message)

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self.logger.debug(message)

    def success(self, message: str) -> None:
        """Log a success message."""
        self.logger.info(f"✓ {message}")

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(message)
