import re
from datetime import datetime
from typing import Generator, Optional
from .models import LogEntry

# Combined Log Format (CLF) / Nginx pattern:
# 127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /index.html HTTP/1.0" 200 2326 "http://referer.com" "UserAgent"
LOG_PATTERN = re.compile(
    r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3}) - - \[(?P<timestamp>.*?)\] "
    r'"(?P<method>\w+) (?P<url>.*?) HTTP/.*?" '
    r'(?P<status>\d{3}) (?P<bytes>\d+|-)(?: "(?P<referer>.*?)" "(?P<agent>.*?)")?'
)


def parse_log_line(line: str) -> Optional[LogEntry]:
    """Parses a single log line into a LogEntry object."""
    match = LOG_PATTERN.match(line)
    if not match:
        return None

    data = match.groupdict()

    # Parse timestamp: 10/Oct/2000:13:55:36 -0700
    try:
        ts_str = data["timestamp"].split(" ")[0]  # Remove timezone for simplicity
        timestamp = datetime.strptime(ts_str, "%d/%b/%Y:%H:%M:%S")
    except ValueError:
        timestamp = datetime.now()

    return LogEntry(
        ip_address=data["ip"],
        timestamp=timestamp,
        method=data["method"],
        url=data["url"],
        status_code=int(data["status"]),
        bytes_sent=int(data["bytes"]) if data["bytes"] != "-" else 0,
        user_agent=data["agent"] or "Unknown",
    )


def log_generator(file_handle) -> Generator[LogEntry, None, None]:
    """
    A generator that yields parsed LogEntry objects one by one.
    Memory efficient for large files.
    """
    for line in file_handle:
        entry = parse_log_line(line.strip())
        if entry:
            yield entry
