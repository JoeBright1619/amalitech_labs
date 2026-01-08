"""
Performance comparison and reporting module.
"""

import json

from pathlib import Path
from typing import Dict, Any
from .utils import setup_logger

logger = setup_logger(__name__)


def generate_comparison_report(results: Dict[str, Dict[str, Any]], output_file: Path):
    """
    Generate a performance comparison report.

    Args:
        results: Dictionary of benchmark results from different modes
        output_file: Path to save the report
    """
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("CONCURRENT FILE PROCESSOR - PERFORMANCE COMPARISON REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")

    # Summary table
    report_lines.append("SUMMARY")
    report_lines.append("-" * 80)
    report_lines.append(
        f"{'Mode':<25} {'Files':<10} {'Time (s)':<12} {'Files/sec':<12} {'Workers':<10}"
    )
    report_lines.append("-" * 80)

    for mode, stats in results.items():
        workers = stats.get("max_workers", "N/A")
        report_lines.append(
            f"{mode:<25} {stats['total_files']:<10} "
            f"{stats['elapsed_time']:<12.2f} {stats['files_per_second']:<12.2f} {workers!s:<10}"
        )

    report_lines.append("-" * 80)
    report_lines.append("")

    # Performance comparison
    if len(results) > 1:
        report_lines.append("PERFORMANCE COMPARISON")
        report_lines.append("-" * 80)

        # Find baseline (sequential)
        baseline_time = results.get("sequential", {}).get("elapsed_time", 0)
        if baseline_time > 0:
            report_lines.append(f"Baseline (Sequential): {baseline_time:.2f}s")
            report_lines.append("")

            for mode, stats in results.items():
                if mode != "sequential":
                    speedup = (
                        baseline_time / stats["elapsed_time"]
                        if stats["elapsed_time"] > 0
                        else 0
                    )
                    report_lines.append(f"{mode.capitalize()}:")
                    report_lines.append(f"  Time: {stats['elapsed_time']:.2f}s")
                    report_lines.append(f"  Speedup: {speedup:.2f}x")
                    report_lines.append(f"  Improvement: {((speedup - 1) * 100):.1f}%")
                    report_lines.append("")

        report_lines.append("-" * 80)
        report_lines.append("")

    # GIL observations
    report_lines.append("GIL (Global Interpreter Lock) OBSERVATIONS")
    report_lines.append("-" * 80)
    report_lines.append("1. Threading Performance:")
    report_lines.append(
        "   - Threading shows improvement for I/O-bound tasks (file downloads)"
    )
    report_lines.append(
        "   - Limited by GIL for CPU-bound tasks (image/text processing)"
    )
    report_lines.append(
        "   - Best for I/O-bound operations with multiple network requests"
    )
    report_lines.append("")
    report_lines.append("2. Multiprocessing Performance:")
    report_lines.append("   - Bypasses GIL by using separate processes")
    report_lines.append(
        "   - Significant speedup for CPU-bound tasks (image processing)"
    )
    report_lines.append("   - Higher memory overhead due to process creation")
    report_lines.append("   - Best for CPU-intensive operations")
    report_lines.append("")
    report_lines.append("3. Async Performance:")
    report_lines.append("   - Excellent for I/O-bound tasks with async libraries")
    report_lines.append("   - Single-threaded but non-blocking I/O")
    report_lines.append("   - CPU-bound tasks still run in executor (subject to GIL)")
    report_lines.append("   - Best for high-concurrency I/O operations")
    report_lines.append("")
    report_lines.append("-" * 80)
    report_lines.append("")

    # Recommendations
    report_lines.append("RECOMMENDATIONS")
    report_lines.append("-" * 80)
    report_lines.append("Use Threading when:")
    report_lines.append("  - Tasks are primarily I/O-bound (network, disk)")
    report_lines.append("  - Need shared memory between workers")
    report_lines.append("  - Lower memory overhead is important")
    report_lines.append("")
    report_lines.append("Use Multiprocessing when:")
    report_lines.append("  - Tasks are CPU-intensive (image processing, calculations)")
    report_lines.append("  - Need to bypass GIL limitations")
    report_lines.append("  - Have multiple CPU cores available")
    report_lines.append("")
    report_lines.append("Use Asyncio when:")
    report_lines.append("  - High concurrency I/O operations")
    report_lines.append("  - Working with async-compatible libraries")
    report_lines.append("  - Need efficient handling of many simultaneous connections")
    report_lines.append("")
    report_lines.append("=" * 80)

    # Write report
    report_text = "\n".join(report_lines)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_text)

    logger.info(f"Performance report saved to {output_file}")

    # Also print to console
    print(report_text)

    # Save JSON version
    json_file = output_file.with_suffix(".json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logger.info(f"JSON results saved to {json_file}")


def run_all_benchmarks(
    input_dir: Path, output_base_dir: Path
) -> Dict[str, Dict[str, Any]]:
    """
    Run all benchmark modes and collect results.

    Args:
        input_dir: Directory containing test files
        output_base_dir: Base directory for processed files

    Returns:
        Dictionary of all benchmark results
    """
    from .sequential_processor import run_sequential_benchmark
    from .threading_processor import run_threading_benchmark
    from .multiprocessing_processor import run_multiprocessing_benchmark
    from .async_processor import run_async_benchmark
    from .utils import ensure_dir

    results = {}

    logger.info("Running comprehensive benchmark suite...")
    logger.info("=" * 60)

    # Sequential
    logger.info("1/4: Running Sequential benchmark...")
    output_dir = ensure_dir(output_base_dir / "sequential")
    results["sequential"] = run_sequential_benchmark(input_dir, output_dir)

    # Threading
    logger.info("2/4: Running Threading benchmark...")
    output_dir = ensure_dir(output_base_dir / "threading")
    results["threading"] = run_threading_benchmark(input_dir, output_dir)

    # Multiprocessing
    logger.info("3/4: Running Multiprocessing benchmark...")
    output_dir = ensure_dir(output_base_dir / "multiprocessing")
    results["multiprocessing"] = run_multiprocessing_benchmark(input_dir, output_dir)

    # Async
    logger.info("4/4: Running Async benchmark...")
    output_dir = ensure_dir(output_base_dir / "async")
    results["async"] = run_async_benchmark(input_dir, output_dir)

    logger.info("=" * 60)
    logger.info("All benchmarks completed!")

    return results
