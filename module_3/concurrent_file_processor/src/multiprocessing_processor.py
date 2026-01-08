"""
Multiprocessing processor - demonstrates multiprocessing for CPU-bound tasks.
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Pool
from .utils import setup_logger, ensure_dir

logger = setup_logger(__name__)


def process_single_file(file_path: Path, output_dir: Path) -> Optional[Dict[str, Any]]:
    """
    Process a single file (used by multiprocessing workers).

    This function must be at module level for pickling.

    Args:
        file_path: Path to file to process
        output_dir: Directory to save processed files

    Returns:
        Dictionary with processing result or None
    """
    from .file_processor import process_image, process_text

    suffix = file_path.suffix.lower()

    if suffix in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]:
        result = process_image(file_path, output_dir)
        if result:
            return {"type": "image", "path": result}

    elif suffix in [".txt", ".log", ".md"]:
        result = process_text(file_path, output_dir)
        if result:
            return {"type": "text", "data": result}

    return None


class MultiprocessingProcessor:
    """Multiprocessing-based file processor for CPU-bound tasks."""

    def __init__(self, input_dir: Path, output_dir: Path, max_workers: int = None):
        """
        Initialize multiprocessing processor.

        Args:
            input_dir: Directory containing files to process
            output_dir: Directory to save processed files
            max_workers: Maximum number of worker processes (None = CPU count)
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        ensure_dir(self.output_dir)

    def process_all_processpoolexecutor(self) -> Dict[str, Any]:
        """
        Process all files using ProcessPoolExecutor.

        Returns:
            Dictionary with processing results and statistics
        """
        logger.info("Starting multiprocessing with ProcessPoolExecutor...")
        start_time = time.time()

        # Get all files
        files = list(self.input_dir.rglob("*"))
        files = [f for f in files if f.is_file()]

        logger.info(
            f"Found {len(files)} files to process with {self.max_workers or 'CPU count'} workers"
        )

        results = {"images": [], "texts": []}

        # Process files using ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(process_single_file, f, self.output_dir): f
                for f in files
            }

            # Collect results
            for future in as_completed(future_to_file):
                try:
                    result = future.result()
                    if result:
                        if result["type"] == "image":
                            results["images"].append(result["path"])
                        elif result["type"] == "text":
                            results["texts"].append(result["data"])
                except Exception as e:
                    logger.error(f"Error processing file: {e}")

        end_time = time.time()
        elapsed = end_time - start_time

        stats = {
            "mode": "multiprocessing_processpoolexecutor",
            "total_files": len(files),
            "processed_images": len(results["images"]),
            "processed_texts": len(results["texts"]),
            "elapsed_time": elapsed,
            "files_per_second": len(files) / elapsed if elapsed > 0 else 0,
            "max_workers": self.max_workers or "CPU count",
        }

        logger.info(f"Multiprocessing completed in {elapsed:.2f} seconds")
        logger.info(
            f"Processed {stats['processed_images']} images and {stats['processed_texts']} texts"
        )

        return stats

    def process_all_pool(self) -> Dict[str, Any]:
        """
        Process all files using multiprocessing.Pool.

        Returns:
            Dictionary with processing results and statistics
        """
        logger.info("Starting multiprocessing with Pool...")
        start_time = time.time()

        # Get all files
        files = list(self.input_dir.rglob("*"))
        files = [f for f in files if f.is_file()]

        logger.info(
            f"Found {len(files)} files to process with {self.max_workers or 'CPU count'} workers"
        )

        results = {"images": [], "texts": []}

        # Process files using Pool
        with Pool(processes=self.max_workers) as pool:
            # Use starmap to pass multiple arguments
            file_output_pairs = [(f, self.output_dir) for f in files]
            pool_results = pool.starmap(process_single_file, file_output_pairs)

            # Collect results
            for result in pool_results:
                if result:
                    if result["type"] == "image":
                        results["images"].append(result["path"])
                    elif result["type"] == "text":
                        results["texts"].append(result["data"])

        end_time = time.time()
        elapsed = end_time - start_time

        stats = {
            "mode": "multiprocessing_pool",
            "total_files": len(files),
            "processed_images": len(results["images"]),
            "processed_texts": len(results["texts"]),
            "elapsed_time": elapsed,
            "files_per_second": len(files) / elapsed if elapsed > 0 else 0,
            "max_workers": self.max_workers or "CPU count",
        }

        logger.info(f"Multiprocessing completed in {elapsed:.2f} seconds")
        logger.info(
            f"Processed {stats['processed_images']} images and {stats['processed_texts']} texts"
        )

        return stats


def run_multiprocessing_benchmark(
    input_dir: Path,
    output_dir: Path,
    max_workers: int = None,
    use_processpoolexecutor: bool = True,
) -> Dict[str, Any]:
    """
    Run multiprocessing processing benchmark.

    Args:
        input_dir: Directory containing test files
        output_dir: Directory to save processed files
        max_workers: Maximum number of worker processes
        use_processpoolexecutor: Use ProcessPoolExecutor if True, Pool if False

    Returns:
        Benchmark statistics
    """
    processor = MultiprocessingProcessor(input_dir, output_dir, max_workers)

    if use_processpoolexecutor:
        return processor.process_all_processpoolexecutor()
    else:
        return processor.process_all_pool()
