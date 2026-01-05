# Student Grade Analytics Tool

This tool processes student records and course grades to provide statistical insights. It utilizes Python's advanced collections for efficient data processing.

## Features

- **Data Models**: Built with `dataclasses` and `NamedTuple`.
- **Aggregation**: Uses `Counter` for distributions and `defaultdict` for grouping.
- **Trend Analysis**: Implements a rolling average using `deque`.
- **Reporting**: Generates ordered JSON reports using `OrderedDict` and `TypedDict`.
- **Visualizations**: Automatically generates bar and pie charts for analysis results.

## Requirements

- Python 3.11+
- Poetry (for dependency management)

## Setup & Usage

1. Navigate to the lab directory:
   ```bash
   cd module_3/student_grade_analytics
   ```
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Run the tool:
   ```bash
   poetry run python main.py
   ```
4. Run tests:
   ```bash
   poetry run pytest
   ```

## Design Considerations

- **Memory Efficiency**: `NamedTuple` is used for `Course` objects to reduce memory overhead.
- **Performance**: `deque` is used for the rolling average to ensure $O(1)$ amortized append and pop operations.
- **Type Safety**: Comprehensive type hints and `TypedDict` are used throughout the codebase.
