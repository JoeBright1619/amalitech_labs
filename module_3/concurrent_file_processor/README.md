# Lab 3: Concurrent File Processor with Threading & Multiprocessing

**Assessment**: Python Advanced  
**Complexity**: Medium  
**Estimated Time**: 6-10 hours

## Objectives

- Understand threading fundamentals and the GIL (Global Interpreter Lock)
- Implement thread-safe operations using Lock, RLock, Semaphore
- Use Queue for thread-safe communication
- Apply concurrent.futures (ThreadPoolExecutor, ProcessPoolExecutor)
- Understand when to use threading vs. multiprocessing
- Implement basic async patterns with asyncio (introduction level)

## Description

Build a Concurrent File Processor that downloads files from URLs, processes them (image resize, text analysis, data conversion), and saves results. You'll implement four versions: sequential, threaded (for I/O-bound tasks), multiprocessed (for CPU-bound tasks), and async. Learn thread synchronization using locks and queues. Use concurrent.futures for clean concurrent code. Measure and compare performance across approaches.

## Installation

### Using Poetry (Recommended)

```bash
poetry install
```

### Using pip

```bash
pip install -r requirements.txt
```

## Usage

### Generate Test Dataset

```bash
# Using Poetry
poetry run python -m src.main --generate-dataset --num-images 10 --num-texts 10

# Or using pip
python -m src.main --generate-dataset --num-images 10 --num-texts 10
```

### Run Individual Modes

**Sequential (Baseline)**

```bash
python -m src.main --mode sequential
```

**Threading**

```bash
python -m src.main --mode threading
```

**Multiprocessing**

```bash
python -m src.main --mode multiprocessing
```

**Async**

```bash
python -m src.main --mode async
```

### Run All Modes and Generate Comparison Report

```bash
poetry run python -m src.main --compare --generate-dataset
```

This will:

1. Generate a test dataset
2. Run all four processing modes
3. Generate a detailed performance comparison report
4. Save results to `data/processed/performance_report.txt`

## Running Tests

```bash
# Using Poetry
poetry run pytest tests/ -v

# Or using pip
pytest tests/ -v
```

## Project Structure

```
concurrent_file_processor/
├── src/
│   ├── __init__.py
│   ├── main.py                      # CLI entry point
│   ├── utils.py                     # Logging, timing utilities
│   ├── dataset_generator.py         # Test dataset creation
│   ├── file_downloader.py           # File download logic
│   ├── file_processor.py            # Image/text processing
│   ├── sequential_processor.py      # Sequential baseline
│   ├── threading_processor.py       # Threading with Lock, Queue
│   ├── multiprocessing_processor.py # Multiprocessing with Pool
│   ├── async_processor.py           # Asyncio implementation
│   └── performance_comparison.py    # Benchmarking & reporting
├── tests/
│   ├── __init__.py
│   └── test_processors.py           # Unit tests
├── data/
│   ├── test_dataset/                # Generated test files
│   └── processed/                   # Processed output
├── requirements.txt
└── README.md
```

## Key Concepts Demonstrated

### Threading

- **ThreadSafeCounter**: Lock-based thread-safe counter
- **Queue**: Thread-safe task distribution
- **ThreadPoolExecutor**: High-level threading interface
- **Manual Threads**: Low-level thread management

### Multiprocessing

- **ProcessPoolExecutor**: High-level multiprocessing interface
- **Pool**: Classic multiprocessing pool
- **GIL Bypass**: True parallelism for CPU-bound tasks

### Asyncio

- **async/await**: Asynchronous programming
- **aiohttp**: Async HTTP requests
- **asyncio.gather**: Concurrent task execution
- **run_in_executor**: Running CPU-bound tasks in async context

## Performance Insights

The comparison report will show:

- **Sequential**: Baseline performance
- **Threading**: Best for I/O-bound tasks (limited by GIL for CPU work)
- **Multiprocessing**: Best for CPU-bound tasks (bypasses GIL)
- **Async**: Best for high-concurrency I/O operations
