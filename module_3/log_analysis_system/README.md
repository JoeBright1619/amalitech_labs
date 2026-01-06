# High-Performance Log Analysis System

A Pythonic tool designed to process large log files efficiently using generators, regular expressions, and advanced collection utilities.

## Features

- **Memory Efficient**: Uses Python generators to process files line-by-line, ensuring low memory usage even for multi-gigabyte files.
- **Performance Monitoring**: Includes a `@timer` decorator that tracks execution time and peak memory usage.
- **Regex Parsing**: Robust parsing of Standard Apache/Nginx log formats.
- **Advanced Analytics**: Utilizes `itertools` and `collections.Counter` for fast statistical aggregation.

## Requirements

- Python 3.11+
- Poetry

## Setup & Usage

1. Open your terminal in the lab directory:
   `D:\projects\amaliTech\amalitech_labs\module_3\log_analysis_system`
2. Configure environment and install dependencies:
   ```bash
   poetry env use python
   poetry install
   ```
3. Run the analysis (automatically generates sample logs if missing):
   ```bash
   poetry run python main.py
   ```
4. Run tests:
   ```bash
   poetry run python -m pytest
   ```

## Implementation Details

- **Data Model**: `NamedTuple` is used for `LogEntry` to minimize object overhead in memory.
- **Custom Context Manager**: `LogFileContext` ensures safe file handling and logging of resource lifecycle.
- **Itertools**: Used `islice` for sampling and `groupby` for status-based aggregation.
