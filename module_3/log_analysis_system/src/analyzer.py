import itertools
import functools
from collections import Counter
from typing import Dict, Iterable, List, Any, Iterator
from .models import LogEntry
from .utils import timer, log_call


class LogAnalyzer:
    """
    Analyzes log entries using functional programming techniques.
    """

    def __init__(self, entries: Iterable[LogEntry]):
        self.entries = entries

    @timer
    @log_call()
    def get_summary_stats(self) -> Dict:
        """Calculates statistics using functional reduce."""

        def reduce_func(acc: Dict, entry: LogEntry) -> Dict:
            acc["total_requests"] += 1
            acc["total_bytes_sent"] += entry.bytes_sent
            acc["status_code_distribution"][entry.status_code] += 1
            acc["ip_counts"][entry.ip_address] += 1
            if entry.is_error:
                acc["error_count"] += 1
            return acc

        initial_state = {
            "total_requests": 0,
            "total_bytes_sent": 0,
            "status_code_distribution": Counter(),
            "ip_counts": Counter(),
            "error_count": 0,
        }

        # Functional pipeline: existing entries -> reduce
        # Note: In a pure functional approach we might map/filter first,
        # but to get ALL stats in one pass, reduce is best.
        stats = functools.reduce(reduce_func, self.entries, initial_state)

        # Post-processing
        total_reqs = stats["total_requests"]
        return {
            "total_requests": total_reqs,
            "total_bytes_sent": stats["total_bytes_sent"],
            "status_code_distribution": dict(stats["status_code_distribution"]),
            "error_rate": (
                (stats["error_count"] / total_reqs * 100) if total_reqs else 0
            ),
            "unique_ips": len(stats["ip_counts"]),
            "top_ips": stats["ip_counts"].most_common(10),
        }

    @staticmethod
    def get_log_sample(entries: Iterable[LogEntry], n: int = 5) -> List[LogEntry]:
        """Returns the first N entries using itertools.islice."""
        return list(itertools.islice(entries, n))

    @staticmethod
    def group_by_status(entries: Iterable[LogEntry]) -> Dict[int, List[LogEntry]]:
        """Groups logs by status using itertools."""
        # Note: groupby generally requires sorted input
        sorted_entries = sorted(entries, key=lambda x: x.status_code)
        return {
            status: list(group)
            for status, group in itertools.groupby(
                sorted_entries, key=lambda x: x.status_code
            )
        }

    @staticmethod
    def filter_by_time_range(
        entries: Iterable[LogEntry], start_time: Any, end_time: Any
    ) -> Iterator[LogEntry]:
        """
        Filters entries by time range using dropwhile (start) and takewhile (end).
        Assumes entries are sorted by timestamp.
        """
        # Skip until start_time
        after_start = itertools.dropwhile(lambda x: x.timestamp < start_time, entries)
        # Take until end_time
        in_range = itertools.takewhile(lambda x: x.timestamp <= end_time, after_start)
        return in_range

    def chain_operations(self) -> Dict:
        """
        Demonstrates a chained functional pipeline:
        1. Parse logs (implicitly)
        2. Filter only errors (4xx/5xx)
        3. Map to bytes sent
        4. Reduce to total error bytes
        """
        # We need a fresh iterable if self.entries was consumed.
        # Assuming usage where we pass a list or fresh generator.

        # Pipeline: filter(errors) -> map(bytes) -> reduce(sum)
        error_logs = filter(lambda x: x.is_error, self.entries)
        error_bytes = map(lambda x: x.bytes_sent, error_logs)
        total_error_bytes = functools.reduce(lambda x, y: x + y, error_bytes, 0)

        return {"total_error_bytes": total_error_bytes}

    @staticmethod
    def batch_iterator(entries: Iterable[LogEntry], batch_size: int = 1000):
        """Custom iterator to produce batches of logs."""
        it = iter(entries)
        while True:
            batch = list(itertools.islice(it, batch_size))
            if not batch:
                break
            yield batch
