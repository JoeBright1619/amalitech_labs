"""
Unit tests for the concurrent file processor.
"""

import pytest
from pathlib import Path
import tempfile
import threading
import time
from PIL import Image


class TestUtils:
    """Test utility functions."""

    def test_ensure_dir(self):
        """Test directory creation."""
        from src.utils import ensure_dir

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test" / "nested" / "dir"
            result = ensure_dir(test_dir)

            assert result.exists()
            assert result.is_dir()

    def test_timer_decorator(self):
        """Test timer decorator."""
        from src.utils import timer

        @timer
        def slow_function():
            time.sleep(0.1)
            return "done"

        result = slow_function()
        assert result == "done"


class TestThreadSafety:
    """Test thread-safe operations."""

    def test_thread_safe_counter(self):
        """Test ThreadSafeCounter with multiple threads."""
        from src.threading_processor import ThreadSafeCounter

        counter = ThreadSafeCounter()
        num_threads = 10
        increments_per_thread = 100

        def increment_counter():
            for _ in range(increments_per_thread):
                counter.increment()

        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=increment_counter)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        expected = num_threads * increments_per_thread
        assert counter.value == expected


class TestFileProcessing:
    """Test file processing functions."""

    def test_process_image(self):
        """Test image processing."""
        from src.file_processor import process_image

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test image
            img = Image.new("RGB", (1000, 800), color="red")
            input_path = tmpdir / "test.jpg"
            img.save(input_path)

            # Process image
            output_dir = tmpdir / "output"
            result = process_image(input_path, output_dir)

            assert result is not None
            assert result.exists()

            # Check processed image
            processed_img = Image.open(result)
            assert processed_img.size == (800, 600)
            assert processed_img.mode == "L"  # Grayscale

    def test_process_text(self):
        """Test text processing."""
        from src.file_processor import process_text

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test text file
            input_path = tmpdir / "test.txt"
            test_content = "Hello world! This is a test file.\nIt has multiple lines."
            with open(input_path, "w") as f:
                f.write(test_content)

            # Process text
            output_dir = tmpdir / "output"
            result = process_text(input_path, output_dir)

            assert result is not None
            assert result["total_words"] == 11
            assert result["total_lines"] == 2


class TestSequentialProcessor:
    """Test sequential processor."""

    def test_sequential_processing(self):
        """Test sequential file processing."""
        from src.sequential_processor import SequentialProcessor
        from src.dataset_generator import create_test_dataset

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test dataset
            input_dir = tmpdir / "input"
            create_test_dataset(input_dir, num_images=2, num_texts=2)

            # Process files
            output_dir = tmpdir / "output"
            processor = SequentialProcessor(input_dir, output_dir)
            stats = processor.process_all()

            assert stats["mode"] == "sequential"
            assert stats["total_files"] == 4
            assert stats["processed_images"] == 2
            assert stats["processed_texts"] == 2
            assert stats["elapsed_time"] > 0


class TestThreadingProcessor:
    """Test threading processor."""

    def test_threadpool_processing(self):
        """Test ThreadPoolExecutor processing."""
        from src.threading_processor import ThreadingProcessor
        from src.dataset_generator import create_test_dataset

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test dataset
            input_dir = tmpdir / "input"
            create_test_dataset(input_dir, num_images=2, num_texts=2)

            # Process files
            output_dir = tmpdir / "output"
            processor = ThreadingProcessor(input_dir, output_dir, max_workers=2)
            stats = processor.process_all_threadpool()

            assert stats["mode"] == "threading_threadpool"
            assert stats["total_files"] == 4
            assert stats["max_workers"] == 2


class TestMultiprocessingProcessor:
    """Test multiprocessing processor."""

    def test_processpoolexecutor_processing(self):
        """Test ProcessPoolExecutor processing."""
        from src.multiprocessing_processor import MultiprocessingProcessor
        from src.dataset_generator import create_test_dataset

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test dataset
            input_dir = tmpdir / "input"
            create_test_dataset(input_dir, num_images=2, num_texts=2)

            # Process files
            output_dir = tmpdir / "output"
            processor = MultiprocessingProcessor(input_dir, output_dir, max_workers=2)
            stats = processor.process_all_processpoolexecutor()

            assert stats["mode"] == "multiprocessing_processpoolexecutor"
            assert stats["total_files"] == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
