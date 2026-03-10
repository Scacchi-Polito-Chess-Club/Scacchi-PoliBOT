"""Logging utility.

This module provides a simple logger class that writes log messages
to both a file and the console.
"""

from datetime import datetime
from pathlib import Path


class Logger:
    """Logger that writes messages to a file and prints to console.

    Attributes:
        log_file: Path to the log file.
    """

    def __init__(self, log_file: Path) -> None:
        """Initialize the logger.

        Args:
            log_file: Path to the log file where messages will be written.
        """
        self.log_file = log_file

    def log(self, level: str, message: str) -> None:
        """Write a log entry with the given level and message.

        Args:
            level: The log level (e.g., INFO, ERROR, DEBUG).
            message: The message to log.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] {message}\n"

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(entry)
        print(entry.strip())

    def info(self, message: str) -> None:
        """Log an info message."""
        self.log("INFO", message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self.log("ERROR", message)

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self.log("DEBUG", message)

    def success(self, message: str) -> None:
        """Log a success message."""
        self.log("SUCCESS", message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.log("WARNING", message)
