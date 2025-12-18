# TDD-based API Service Stub

A weather forecast service developed using Test-Driven Development (TDD), demonstrating the use of service stubs and structured logging.

## Overview

This lab demonstrates how to build a service that consumes an external API (simulated via an interface) using TDD. The `WeatherService` provides a high-level API for getting weather forecasts, delegating the actual work to a `WeatherProvider`.

## Features

-   **Service-Oriented Design**: Clean separation between the service layer and the data provider.
-   **Structured Logging**: Uses JSON-formatted logs for better observability.
-   **TDD Methodology**: Built with a "test-first" approach to ensure reliability and correct behavior.
-   **Error Handling**: Custom exceptions for domain-specific errors like `CityNotFoundError`.

## Project Structure

```
tdd-based_api_service_stub/
├── src/
│   └── tdd_based_api_service_stub/
│       ├── exceptions.py       # Custom exceptions
│       ├── logger.py           # Structured logging configuration
│       ├── models.py           # Weather forecast data model
│       ├── provider.py         # Abstract interface for weather data
│       └── service.py          # Core WeatherService logic
└── tests/                      # Pytest test suite
```

## Setup and Usage

### Prerequisites

-   Python 3.10+
-   `poetry`

### Installation

1.  Navigate to the lab directory:
    ```bash
    cd module_2/tdd-based_api_service_stub
    ```

2.  Install dependencies:
    ```bash
    poetry install
    ```

### Running Tests

To run the tests and check coverage:
```bash
poetry run pytest --cov=tdd_based_api_service_stub --cov-report=term-missing
```

## Learning Objectives

This lab covers:
-   **Interface-Based Programming**: Using abstract base classes to define service contracts.
-   **Stubs and Mocks**: How to test services without relying on real external APIs.
-   **Structured Logging**: The importance of machine-readable logs in modern applications.
-   **Advanced TDD**: Handling edge cases and error conditions through tests.