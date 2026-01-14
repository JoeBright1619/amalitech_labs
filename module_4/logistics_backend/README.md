# Logistics and Shipment Tracking Backend

Backend data service for a shipment tracking company using PostgreSQL, Redis, and MongoDB.

## ER Diagram

```mermaid
erDiagram
    CUSTOMER ||--o{ PACKAGE : sends
    CUSTOMER ||--o{ PACKAGE : receives
    LOCATION ||--o{ TRACKING_EVENT : occurs_at
    PACKAGE ||--o{ TRACKING_EVENT : has
    PACKAGE ||--|| SHIPMENT : managed_as
    LOCATION ||--o{ SHIPMENT : starts_at
    LOCATION ||--o{ SHIPMENT : ends_at

    CUSTOMER {
        int customer_id PK
        string name
        string email
        string address
    }

    LOCATION {
        int location_id PK
        string location_name
        string city
        string state
        string location_type
    }

    PACKAGE {
        int package_id PK
        string tracking_number
        int sender_id FK
        int recipient_id FK
        string current_status
        decimal weight
        jsonb metadata
    }

    SHIPMENT {
        int shipment_id PK
        int package_id FK
        int origin_location_id FK
        int destination_location_id FK
        timestamp estimated_delivery
        timestamp actual_delivery
    }

    TRACKING_EVENT {
        int event_id PK
        int package_id FK
        int location_id FK
        string status
        timestamp event_timestamp
    }
```

## Setup

1. **Prerequisites**: Docker, Poetry, Python 3.11+
2. **Start Databases**:
   ```bash
   docker-compose up -d
   ```
3. **Install Dependencies**:
   ```bash
   poetry install
   ```

## Schema Explanation

The PostgreSQL database follows the **Third Normal Form (3NF)**:

- **Customers**: Stores distinct user info.
- **Locations**: Centralizes warehouse/hub details to avoid data duplication.
- **Packages**: Contains core shipment details, including a `JSONB` column for flexible metadata (e.g., "fragile").
- **Shipments**: Explicitly links origin and destination hubs.
- **TrackingEvents**: Normalized history log, referencing packages and locations.

## Performance Tuning Report

_(To be updated after Milestone 4)_
