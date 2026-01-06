from datetime import datetime
from src.models import LogEntry
from src.parser import parse_log_line
from src.analyzer import LogAnalyzer


def test_log_entry_error_property():
    entry_ok = LogEntry("1.1.1.1", datetime.now(), "GET", "/", 200, 100, "agent")
    entry_err = LogEntry("1.1.1.1", datetime.now(), "GET", "/", 404, 100, "agent")
    assert entry_ok.is_error is False
    assert entry_err.is_error is True


def test_parse_log_line():
    line = (
        '127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /index.html HTTP/1.0" 200 2326'
    )
    entry = parse_log_line(line)
    assert entry is not None
    assert entry.ip_address == "127.0.0.1"
    assert entry.status_code == 200
    assert entry.method == "GET"


def test_analyzer_summary():
    entries = [
        LogEntry("1.1.1.1", datetime.now(), "GET", "/a", 200, 100, "agent"),
        LogEntry("1.1.1.1", datetime.now(), "GET", "/b", 404, 200, "agent"),
        LogEntry("2.2.2.2", datetime.now(), "POST", "/c", 500, 300, "agent"),
    ]
    analyzer = LogAnalyzer(entries)
    stats = analyzer.get_summary_stats()

    assert stats["total_requests"] == 3
    assert stats["error_rate"] == (2 / 3 * 100)
    assert stats["unique_ips"] == 2
    assert stats["total_bytes_sent"] == 600
