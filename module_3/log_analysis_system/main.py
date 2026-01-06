import json
from pathlib import Path
from src.context_manager import LogFileContext
from src.parser import log_generator
from src.analyzer import LogAnalyzer
from src.utils import timer


@timer
def run_analysis(log_path: Path, output_path: Path):
    """Orchestrates the log analysis process."""
    print("--- High-Performance Log Analysis System ---")
    print(f"Target File: {log_path}")

    with LogFileContext(str(log_path)) as f:
        # Create a generator for entries
        entries = log_generator(f)

        analyzer = LogAnalyzer(entries)

        print("Processing logs...")
        stats = analyzer.get_summary_stats()

        # Output results
        print("\n--- Analysis Summary ---")
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Error Rate: {stats['error_rate']:.2f}%")
        print(f"Unique IPs: {stats['unique_ips']}")
        print(f"Total Data Sent: {stats['total_bytes_sent'] / (1024*1024):.2f} MB")

        print("\nTop 5 IP Addresses:")
        for ip, count in stats["top_ips"][:5]:
            print(f"  - {ip}: {count} hits")

    # Save to JSON
    with output_path.open("w", encoding="utf-8") as out_f:
        json.dump(stats, out_f, indent=4)
    print(f"\nFull report saved to: {output_path}")


if __name__ == "__main__":
    base_dir = Path(__file__).parent
    log_file = base_dir / "data" / "access.log"
    report_file = base_dir / "data" / "analysis_report.json"

    # Generate logs if they don't exist
    if not log_file.exists():
        from generate_sample_logs import generate_logs

        print("Sample log file not found. Generating...")
        generate_logs(str(log_file), 10000)

    run_analysis(log_file, report_file)
