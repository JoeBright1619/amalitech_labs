import functools
import time
import psutil
import os
from typing import Callable, Any


def timer(func: Callable) -> Callable:
    """Decorator that prints the execution time and memory usage of the function it decorates."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss / (1024 * 1024)
        start_time = time.perf_counter()

        result = func(*args, **kwargs)

        end_time = time.perf_counter()
        end_mem = process.memory_info().rss / (1024 * 1024)

        duration = end_time - start_time
        mem_diff = end_mem - start_mem

        print(f"\n[Performance] Function '{func.__name__}' executed in {duration:.4f}s")
        print(
            f"[Performance] Memory Change: {mem_diff:+.2f} MB (End: {end_mem:.2f} MB)"
        )

        return result

    return wrapper


def get_memory_usage() -> float:
    """Returns the current memory usage of the process in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)
