import itertools
from collections import Counter
from typing import Dict, Iterable, List
from .models import LogEntry
from .utils import timer


class LogAnalyzer:
    """
    Analyzes log entries using efficient iteration and collection utilities.
    Works with generators to keep memory usage low.
    """

    def __init__(self, entries: Iterable[LogEntry]):
        # We store the entries as an iterable to allow multiple passes if needed,
        # but caution: if it's a generator, it can only be consumed once.
        # In a real system, we'd process in a single pass.
        self.entries = entries

    @timer
    def get_summary_stats(self) -> Dict:
        """Calculates basic summary statistics in a single pass."""
        total_requests = 0
        total_bytes = 0
        status_counts = Counter()
        ip_counts = Counter()
        error_count = 0

        # Consuming the iterable once for all stats
        for entry in self.entries:
            total_requests += 1
            total_bytes += entry.bytes_sent
            status_counts[entry.status_code] += 1
            ip_counts[entry.ip_address] += 1
            if entry.is_error:
                error_count += 1

        return {
            "total_requests": total_requests,
            "total_bytes_sent": total_bytes,
            "status_code_distribution": dict(status_counts),
            "error_rate": (
                (error_count / total_requests * 100) if total_requests > 0 else 0
            ),
            "unique_ips": len(ip_counts),
            "top_ips": ip_counts.most_common(10),
        }

    @staticmethod
    def get_log_sample(entries: Iterable[LogEntry], n: int = 5) -> List[LogEntry]:
        """Returns the first N entries using itertools.islice."""
        return list(itertools.islice(entries, n))

    @staticmethod
    def group_by_status(entries: Iterable[LogEntry]) -> Dict[int, List[LogEntry]]:
        """
        Groups log entries by status code using itertools.groupby.
        Requires the input to be sorted by status code.
        """
        sorted_entries = sorted(entries, key=lambda x: x.status_code)
        grouped = {}
        for status, group in itertools.groupby(
            sorted_entries, key=lambda x: x.status_code
        ):
            grouped[status] = list(group)
        return grouped
