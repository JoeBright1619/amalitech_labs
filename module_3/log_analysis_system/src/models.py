from typing import NamedTuple
from datetime import datetime


class LogEntry(NamedTuple):
    """
    Represents a single parsed log entry.
    Using NamedTuple for high-performance memory efficiency and immutability.
    """

    ip_address: str
    timestamp: datetime
    method: str  # GET, POST, etc.
    url: str
    status_code: int
    bytes_sent: int
    user_agent: str

    @property
    def is_error(self) -> bool:
        """Returns True if the status code indicates a client or server error (4xx or 5xx)."""
        return self.status_code >= 400

    def __repr__(self) -> str:
        return f"LogEntry({self.ip_address}, {self.status_code}, {self.url})"
