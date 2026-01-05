import logging
from pathlib import Path
from typing import TextIO, Optional

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogFileContext:
    """
    A custom context manager for safe and efficient log file handling.
    Handles file opening/closing and ensures graceful error handling.
    """

    def __init__(self, file_path: str, mode: str = "r"):
        self.file_path = Path(file_path)
        self.mode = mode
        self.file_handle: Optional[TextIO] = None

    def __enter__(self) -> TextIO:
        try:
            if not self.file_path.exists() and "r" in self.mode:
                raise FileNotFoundError(f"Log file not found at: {self.file_path}")

            self.file_handle = self.file_path.open(self.mode, encoding="utf-8")
            logger.info(f"Successfully opened log file: {self.file_path}")
            return self.file_handle
        except Exception as e:
            logger.error(f"Error opening log file {self.file_path}: {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file_handle:
            self.file_handle.close()
            logger.info(f"Closed log file handle: {self.file_path}")

        if exc_type is not None:
            logger.error(f"An error occurred during log processing: {exc_value}")
            return False  # Propagate the exception
        return True
