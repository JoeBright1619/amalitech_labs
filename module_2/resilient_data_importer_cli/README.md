# Resilient Data Importer CLI

A robust command-line interface (CLI) tool for importing user data from a CSV file into a JSON database, designed with resilience against errors and adherence to best practices.

## Overview

This tool reads user data from a specified CSV file, validates it, and stores it in a JSON-backed "database". It is built to handle common issues like missing files, malformed data, and duplicate records gracefully, providing feedback to the user via logging.

## Features

-   **Resilient Import**: Handles missing files, invalid CSV formats, and missing fields.
-   **Data Validation**: Ensures required fields (`user_id`, `name`, `email`) are present.
-   **Duplicate Prevention**: Skips duplicate user IDs with a warning log.
-   **Atomic Operations**: Uses a custom context manager for safe file locking and atomic updates to the JSON database.
-   **Logging**: Provides informative logs about the import process.

## Project Structure

```
resilient_data_importer_cli/
├── cli.py              # Main entry point for the CLI
├── context_managers/   # Custom context managers (e.g., file handling)
├── data/               # Data storage (database.json)
├── exceptions/         # Custom exception classes
├── models/             # Data models (e.g., User)
├── parsers/            # Data parsers (e.g., CSV parser)
├── repository/         # Data access layer (Repository pattern)
├── services/           # Business logic service layer
└── tests/              # Unit and integration tests
```

## Setup and Usage

### Prerequisites

-   Python 3.8+
-   `poetry` (optional, for dependency management)

### Installation

1.  Navigate to the project directory:
    ```bash
    cd module_2/resilient_data_importer_cli
    ```

2.  Install dependencies (if using a virtual environment or poetry):
    ```bash
    pip install -r requirements.txt
    # OR
    poetry install
    ```

### Running the Tool

To run the importer, use the following command:

```bash
python -m module_2.resilient_data_importer_cli.cli <path_to_csv_file>
```

**Note**: You might need to run this from the root `amalitech_labs` directory as a module:

```bash
python -m module_2.resilient_data_importer_cli.cli module_2/resilient_data_importer_cli/users.csv
```

### Arguments

-   `csv_file`: Path to the CSV file containing user data (Required).
-   `--db`: Path to the JSON database file (Optional, defaults to `data/database.json`).

## Learning Objectives

This lab demonstrates:
-   **Robust Exception Handling**: Custom exceptions for specific error cases.
-   **SOLID Principles**: Separation of concerns with Repositories and Services.
-   **Context Managers**: Safe resource management.
-   **Design Patterns**: Repository pattern, Service layer.
-   **Code Quality**: Type hinting, docstrings, and modular design.
