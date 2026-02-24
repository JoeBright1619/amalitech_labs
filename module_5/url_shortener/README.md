# AmaliTech URL Shortener API

A professional, high-performance, and feature-rich URL shortener microservice built with **Django REST Framework**, **PostgreSQL**, **Redis**, and **Celery**.

## 🚀 Overview

This service provides robust URL shortening capabilities with a focus on high performance, scalability, and developer experience. It features tiered user access (Free vs. Premium), real-time analytics, async metadata fetching, and microservice integration for URL previews.

## 🏗️ Architecture Diagram

![Architecture Diagram](./architecture_diagram.svg)

## 🛠️ Getting Started (Docker)

The project is fully containerized for a seamless development experience.

### 1. Build and Run

```bash
# Build and start all services (API, DB, Redis, Celery)
docker-compose up --build
```

### 2. Database Setup

```bash
# Run migrations
docker-compose exec api python manage.py migrate

# Create a superuser (for Admin access)
docker-compose exec api python manage.py createsuperuser
```

### 3. Run Tests

```bash
# Run the complete test suite (38+ tests)
docker-compose exec api poetry run python manage.py test shortener.tests
```

The API will be available at `http://localhost:8000`.

## 🔌 API Endpoints

### Authentication

| Method | Endpoint                 | Description                        | Access |
| :----- | :----------------------- | :--------------------------------- | :----- |
| POST   | `/api/v1/register/`      | Register a new user (Free/Premium) | Public |
| POST   | `/api/v1/login/`         | Obtain JWT Access & Refresh tokens | Public |
| POST   | `/api/v1/token/refresh/` | Refresh existing access token      | Public |

### URL Management

| Method | Endpoint               | Description                             | Access        |
| :----- | :--------------------- | :-------------------------------------- | :------------ |
| POST   | `/api/v1/urls/`        | Shorten a long URL                      | Authenticated |
| GET    | `/api/v1/urls/`        | List URLs owned by user (supports tags) | Authenticated |
| GET    | `/api/v1/urls/{code}/` | Get detailed URL metadata               | Owner         |
| PATCH  | `/api/v1/urls/{code}/` | Update original URL or alias            | Owner         |
| DELETE | `/api/v1/urls/{code}/` | Deactivate or permanently delete URL    | Owner         |

### Redirect & Analytics

| Method | Endpoint                         | Description                               | Access |
| :----- | :------------------------------- | :---------------------------------------- | :----- |
| GET    | `/{code}/`                       | High-speed redirect to original URL       | Public |
| GET    | `/api/v1/urls/{code}/analytics/` | Click stats (Geo/Time-series for Premium) | Owner  |

### System Health

| Method | Endpoint          | Description                 | Access |
| :----- | :---------------- | :-------------------------- | :----- |
| GET    | `/api/v1/health/` | Health check for DB & Redis | Public |

## 🌟 Key Features

- **Caching**: 0.1ms redirects using Redis key-value storage.
- **Analytics**: Geo-location inference and click tracking denormalization.
- **Microservices**: Async preview generation with circuit breakers and retries.
- **Security**: JWT-based auth, RBAC, and login rate limiting (throttling).
- **Optimization**: N+1 query prevention using `select_related` and `prefetch_related`.

## 📖 Documentation

Interactive Swagger UI is available at `http://localhost:8000/api/schema/swagger-ui/`.
