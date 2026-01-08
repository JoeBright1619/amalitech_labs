"""
Threading processor - demonstrates threading for I/O-bound tasks.
"""

import time
import threading
from pathlib import Path
from typing import Dict, Any
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import setup_logger, ensure_dir

logger = setup_logger(__name__)


class ThreadSafeCounter:
    """Thread-safe counter using Lock."""

    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self):
        """Increment counter in a thread-safe manner."""
        with self._lock:
            self._value += 1

    @property
    def value(self):
        """Get current counter value."""
        with self._lock:
            return self._value


class ThreadingProcessor:
    """Threading-based file processor for I/O-bound tasks."""

    def __init__(self, input_dir: Path, output_dir: Path, max_workers: int = 4):
        """
        Initialize threading processor.

        Args:
            input_dir: Directory containing files to process
            output_dir: Directory to save processed files
            max_workers: Maximum number of worker threads
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        ensure_dir(self.output_dir)

        # Thread synchronization primitives
        self.progress_counter = ThreadSafeCounter()
        self.file_queue = Queue()
        self.results_lock = threading.Lock()
        self.results = {"images": [], "texts": []}

    def process_file_worker(self, file_path: Path):
        """
        Worker function to process a single file.

        Args:
            file_path: Path to file to process
        """
        from .file_processor import process_image, process_text

        suffix = file_path.suffix.lower()

        if suffix in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]:
            result = process_image(file_path, self.output_dir)
            if result:
                with self.results_lock:
                    self.results["images"].append(result)

        elif suffix in [".txt", ".log", ".md"]:
            result = process_text(file_path, self.output_dir)
            if result:
                with self.results_lock:
                    self.results["texts"].append(result)

        self.progress_counter.increment()

    def process_all_threadpool(self) -> Dict[str, Any]:
        """
        Process all files using ThreadPoolExecutor.

        Returns:
            Dictionary with processing results and statistics
        """
        logger.info("Starting threading processing with ThreadPoolExecutor...")
        start_time = time.time()

        # Get all files
        files = list(self.input_dir.rglob("*"))
        files = [f for f in files if f.is_file()]

        logger.info(
            f"Found {len(files)} files to process with {self.max_workers} workers"
        )

        # Process files using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = [executor.submit(self.process_file_worker, f) for f in files]

            # Wait for completion
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error processing file: {e}")

        end_time = time.time()
        elapsed = end_time - start_time

        stats = {
            "mode": "threading_threadpool",
            "total_files": len(files),
            "processed_images": len(self.results["images"]),
            "processed_texts": len(self.results["texts"]),
            "elapsed_time": elapsed,
            "files_per_second": len(files) / elapsed if elapsed > 0 else 0,
            "max_workers": self.max_workers,
        }

        logger.info(f"Threading processing completed in {elapsed:.2f} seconds")
        logger.info(
            f"Processed {stats['processed_images']} images and {stats['processed_texts']} texts"
        )

        return stats

    def process_all_manual_threads(self) -> Dict[str, Any]:
        """
        Process all files using manual thread management with Queue.

        Returns:
            Dictionary with processing results and statistics
        """
        logger.info("Starting threading processing with manual threads...")
        start_time = time.time()

        # Get all files
        files = list(self.input_dir.rglob("*"))
        files = [f for f in files if f.is_file()]

        logger.info(
            f"Found {len(files)} files to process with {self.max_workers} workers"
        )

        # Populate queue
        for f in files:
            self.file_queue.put(f)

        # Worker function
        def worker():
            while True:
                try:
                    file_path = self.file_queue.get(timeout=1)
                    self.process_file_worker(file_path)
                    self.file_queue.task_done()
                except Exception:
                    break

        # Create and start threads
        threads = []
        for _ in range(self.max_workers):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)

        # Wait for queue to be empty
        self.file_queue.join()

        # Wait for all threads to finish
        for t in threads:
            t.join()

        end_time = time.time()
        elapsed = end_time - start_time

        stats = {
            "mode": "threading_manual",
            "total_files": len(files),
            "processed_images": len(self.results["images"]),
            "processed_texts": len(self.results["texts"]),
            "elapsed_time": elapsed,
            "files_per_second": len(files) / elapsed if elapsed > 0 else 0,
            "max_workers": self.max_workers,
        }

        logger.info(f"Threading processing completed in {elapsed:.2f} seconds")
        logger.info(
            f"Processed {stats['processed_images']} images and {stats['processed_texts']} texts"
        )

        return stats


def run_threading_benchmark(
    input_dir: Path, output_dir: Path, max_workers: int = 4, use_threadpool: bool = True
) -> Dict[str, Any]:
    """
    Run threading processing benchmark.

    Args:
        input_dir: Directory containing test files
        output_dir: Directory to save processed files
        max_workers: Maximum number of worker threads
        use_threadpool: Use ThreadPoolExecutor if True, manual threads if False

    Returns:
        Benchmark statistics
    """
    processor = ThreadingProcessor(input_dir, output_dir, max_workers)

    if use_threadpool:
        return processor.process_all_threadpool()
    else:
        return processor.process_all_manual_threads()
