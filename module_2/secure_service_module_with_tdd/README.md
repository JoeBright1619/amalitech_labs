# Secure Service Module with TDD

A standalone User Authentication Service Module built using Test-Driven Development (TDD) and clean architecture principles.

## Overview

This module provides essential user management features, including registration and authentication, with a strong focus on security and maintainability. It demonstrates the use of dependency injection, interfaces (ABCs), and robust password hashing using `bcrypt`.

## Features

-   **User Registration**: Securely register new users with password policy enforcement (minimum 8 characters).
-   **Authentication**: Verify user credentials with secure password hash comparison.
-   **Security**: Uses `bcrypt` for industry-standard password hashing.
-   **Clean Architecture**: Decouples business logic from data storage and hashing implementation using interfaces.
-   **TDD Process**: Developed following the "Red-Green-Refactor" cycle.

## Project Structure

```
secure_service_module_with_tdd/
├── src/
│   └── secure_service_module_with_tdd/
│       ├── exceptions.py       # Custom authentication exceptions
│       ├── models.py           # User data model (dataclass)
│       ├── service.py          # Main UserService logic
│       ├── interfaces/         # Abstract Base Classes for dependencies
│       │   ├── hasher.py
│       │   └── repository.py
│       └── implementations/    # Concrete implementations of interfaces
│           ├── bcrypt_hasher.py
│           └── memory_repo.py
└── tests/                      # Comprehensive test suite (pytest)
```

## Setup and Usage

### Prerequisites

-   Python 3.10+
-   `poetry`

### Installation

1.  Navigate to the lab directory:
    ```bash
    cd module_2/secure_service_module_with_tdd
    ```

2.  Install dependencies:
    ```bash
    poetry install
    ```

### Usage Example

```python
from secure_service_module_with_tdd.service import UserService
from secure_service_module_with_tdd.implementations.memory_repo import InMemoryUserRepository
from secure_service_module_with_tdd.implementations.bcrypt_hasher import BcryptPasswordHasher

# Initialize dependencies
repo = InMemoryUserRepository()
hasher = BcryptPasswordHasher()

# Create the service
service = UserService(repo, hasher)

# Register a user
service.register_user("john_doe", "secure_password_123")

# Authenticate
user = service.authenticate_user("john_doe", "secure_password_123")
print(f"Authenticated user: {user.username}")
```

## Learning Objectives

This lab focuses on:
-   **Test-Driven Development**: Writing tests before implementation.
-   **Dependency Inversion Principle**: Depending on abstractions, not concretions.
-   **Mocking**: Using `pytest-mock` to isolate the service layer during testing.
-   **Structural Design**: Organizing code into interfaces and implementations.
-   **Security Best Practices**: Safe password storage and verification.
