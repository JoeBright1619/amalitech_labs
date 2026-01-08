"""
Main entry point for Concurrent File Processor.
"""

import argparse
import json
from pathlib import Path
from .dataset_generator import create_test_dataset
from .sequential_processor import run_sequential_benchmark
from .utils import setup_logger, ensure_dir

logger = setup_logger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Concurrent File Processor - Lab 3")

    parser.add_argument(
        "--mode",
        choices=["sequential", "threading", "multiprocessing", "async", "all"],
        default="sequential",
        help="Processing mode to use",
    )

    parser.add_argument(
        "--generate-dataset",
        action="store_true",
        help="Generate test dataset before processing",
    )

    parser.add_argument(
        "--num-images", type=int, default=10, help="Number of test images to generate"
    )

    parser.add_argument(
        "--num-texts",
        type=int,
        default=10,
        help="Number of test text files to generate",
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "test_dataset",
        help="Input directory containing files to process",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "processed",
        help="Output directory for processed files",
    )

    args = parser.parse_args()

    # Generate dataset if requested
    if args.generate_dataset:
        logger.info("Generating test dataset...")
        create_test_dataset(args.input_dir, args.num_images, args.num_texts)

    # Ensure output directory exists
    ensure_dir(args.output_dir)

    # Run processing based on mode
    results = {}

    if args.mode == "sequential" or args.mode == "all":
        logger.info("Running sequential processing...")
        output_dir = args.output_dir / "sequential"
        ensure_dir(output_dir)
        results["sequential"] = run_sequential_benchmark(args.input_dir, output_dir)

    if args.mode == "threading" or args.mode == "all":
        from .threading_processor import run_threading_benchmark

        logger.info("Running threading processing...")
        output_dir = args.output_dir / "threading"
        ensure_dir(output_dir)
        results["threading"] = run_threading_benchmark(args.input_dir, output_dir)

    if args.mode == "multiprocessing" or args.mode == "all":
        from .multiprocessing_processor import run_multiprocessing_benchmark

        logger.info("Running multiprocessing processing...")
        output_dir = args.output_dir / "multiprocessing"
        ensure_dir(output_dir)
        results["multiprocessing"] = run_multiprocessing_benchmark(
            args.input_dir, output_dir
        )

    if args.mode == "async" or args.mode == "all":
        logger.info("Async mode not yet implemented")
        # TODO: Implement async mode

    # Print results
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)
    print(json.dumps(results, indent=2))
    print("=" * 60)


if __name__ == "__main__":
    main()
