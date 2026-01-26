# URL Shortener Microservice

A production-ready URL Shortener built with Django REST Framework and Redis.
Designed for high performance, utilizing Redis as the primary data store for URL mappings.

## Features

- **Shorten URL**: POST to `/api/shorten/` to generate a unique short code.
- **Redirect**: Access `/<short_code>/` to be redirected to the original URL.
- **Redis Backed**: High-speed key-value storage.
- **Dockerized**: Fully containerized with Docker and Docker Compose.
- **OpenAPI Docs**: Auto-generated Swagger UI.
- **Production Ready**: Gunicorn server, Environment variables, Logging.

## Prerequisites

- Docker & Docker Compose
- (Optional) Python 3.12+ and Poetry for local development

## Getting Started

### Using Docker (Recommended)

1.  Clone the repository:

    ```bash
    git clone <repository-url>
    cd url_shortener
    ```

2.  Build and run the containers:

    ```bash
    docker-compose up --build
    ```

3.  Access the service:
    - **API**: `http://localhost:8000/api/shorten/`
    - **Swagger UI**: `http://localhost:8000/api/schema/swagger-ui/`
    - **Redis**: Port `6379` exposed locally if needed.

### Local Development

1.  Install dependencies:

    ```bash
    poetry install
    ```

2.  Start Redis (ensure it's running on localhost:6379 or update .env).

3.  Run the server:

    ```bash
    poetry run python manage.py runserver
    ```

4.  Run tests:
    ```bash
    poetry run python manage.py test shortener
    ```

## API Documentation

Interactive API documentation is available at `/api/schema/swagger-ui/`.

### Endpoints

- `POST /api/shorten/`:
  - Body: `{"url": "https://example.com"}`
  - Response: `{"short_code": "Abc12", "short_url": "http://.../Abc12/"}`

- `GET /<short_code>/`:
  - Redirects to the original URL (302 Found).
  - Returns 404 if code not found.

## Architecture

- **API Layer**: Django REST Framework Views & Serializers.
- **Service Layer**: `UrlShortenerService` handles business logic.
- **Repository Layer**: `RedisUrlRepository` abstracts Redis access.
- **Storage**: Redis (Persistent).

## Configuration

Environment variables are managed via `.env` file (using `python-decouple`).

- `DEBUG`: Toggle debug mode.
- `SECRET_KEY`: Django secret key.
- `REDIS_URL`: Connection string for Redis.
