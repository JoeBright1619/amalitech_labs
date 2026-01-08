"""
Sequential processor - baseline implementation without concurrency.
"""

import time
from pathlib import Path
from typing import Dict, Any
from .file_processor import process_files_sequential
from .utils import setup_logger, ensure_dir

logger = setup_logger(__name__)


class SequentialProcessor:
    """Sequential file processor for baseline performance measurement."""

    def __init__(self, input_dir: Path, output_dir: Path):
        """
        Initialize sequential processor.

        Args:
            input_dir: Directory containing files to process
            output_dir: Directory to save processed files
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        ensure_dir(self.output_dir)

    def process_all(self) -> Dict[str, Any]:
        """
        Process all files in input directory sequentially.

        Returns:
            Dictionary with processing results and statistics
        """
        logger.info("Starting sequential processing...")
        start_time = time.time()

        # Get all files
        files = list(self.input_dir.rglob("*"))
        files = [f for f in files if f.is_file()]

        logger.info(f"Found {len(files)} files to process")

        # Process files
        results = process_files_sequential(files, self.output_dir)

        end_time = time.time()
        elapsed = end_time - start_time

        stats = {
            "mode": "sequential",
            "total_files": len(files),
            "processed_images": len(results["images"]),
            "processed_texts": len(results["texts"]),
            "elapsed_time": elapsed,
            "files_per_second": len(files) / elapsed if elapsed > 0 else 0,
        }

        logger.info(f"Sequential processing completed in {elapsed:.2f} seconds")
        logger.info(
            f"Processed {stats['processed_images']} images and {stats['processed_texts']} texts"
        )

        return stats


def run_sequential_benchmark(input_dir: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Run sequential processing benchmark.

    Args:
        input_dir: Directory containing test files
        output_dir: Directory to save processed files

    Returns:
        Benchmark statistics
    """
    processor = SequentialProcessor(input_dir, output_dir)
    return processor.process_all()
