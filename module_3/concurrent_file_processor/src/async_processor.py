"""
Async processor - demonstrates asyncio for I/O-bound tasks.
"""

import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List
import aiohttp
import aiofiles
from .utils import setup_logger, ensure_dir

logger = setup_logger(__name__)


async def async_download_file(
    session: aiohttp.ClientSession, url: str, save_path: Path
) -> bool:
    """
    Asynchronously download a file from a URL.

    Args:
        session: aiohttp client session
        url: URL to download from
        save_path: Local path to save the file

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Async downloading {url}")

        async with session.get(
            url, timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            response.raise_for_status()

            # Ensure parent directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file asynchronously
            async with aiofiles.open(save_path, "wb") as f:
                async for chunk in response.content.iter_chunked(8192):
                    await f.write(chunk)

        logger.info(f"Async downloaded {url} to {save_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to async download {url}: {e}")
        return False


async def async_process_files(files: List[Path], output_dir: Path) -> Dict[str, List]:
    """
    Asynchronously process files (CPU-bound work still runs in executor).

    Args:
        files: List of file paths to process
        output_dir: Directory to save processed files

    Returns:
        Dictionary with lists of processed images and text analyses
    """
    from .file_processor import process_image, process_text

    results = {"images": [], "texts": []}

    # Process files in executor (since they're CPU-bound)
    loop = asyncio.get_event_loop()

    tasks = []
    for file_path in files:
        suffix = file_path.suffix.lower()

        if suffix in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]:
            task = loop.run_in_executor(None, process_image, file_path, output_dir)
            tasks.append(("image", task))
        elif suffix in [".txt", ".log", ".md"]:
            task = loop.run_in_executor(None, process_text, file_path, output_dir)
            tasks.append(("text", task))

    # Gather all results
    for file_type, task in tasks:
        result = await task
        if result:
            if file_type == "image":
                results["images"].append(result)
            elif file_type == "text":
                results["texts"].append(result)

    return results


class AsyncProcessor:
    """Async-based file processor for I/O-bound tasks."""

    def __init__(self, input_dir: Path, output_dir: Path):
        """
        Initialize async processor.

        Args:
            input_dir: Directory containing files to process
            output_dir: Directory to save processed files
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        ensure_dir(self.output_dir)

    async def process_all_async(self) -> Dict[str, Any]:
        """
        Process all files asynchronously.

        Returns:
            Dictionary with processing results and statistics
        """
        logger.info("Starting async processing...")
        start_time = time.time()

        # Get all files
        files = list(self.input_dir.rglob("*"))
        files = [f for f in files if f.is_file()]

        logger.info(f"Found {len(files)} files to process asynchronously")

        # Process files
        results = await async_process_files(files, self.output_dir)

        end_time = time.time()
        elapsed = end_time - start_time

        stats = {
            "mode": "async",
            "total_files": len(files),
            "processed_images": len(results["images"]),
            "processed_texts": len(results["texts"]),
            "elapsed_time": elapsed,
            "files_per_second": len(files) / elapsed if elapsed > 0 else 0,
        }

        logger.info(f"Async processing completed in {elapsed:.2f} seconds")
        logger.info(
            f"Processed {stats['processed_images']} images and {stats['processed_texts']} texts"
        )

        return stats


def run_async_benchmark(input_dir: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Run async processing benchmark.

    Args:
        input_dir: Directory containing test files
        output_dir: Directory to save processed files

    Returns:
        Benchmark statistics
    """
    processor = AsyncProcessor(input_dir, output_dir)

    # Run async processing
    return asyncio.run(processor.process_all_async())
