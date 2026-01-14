-- DDL for Logistics System

-- 1. Customers Table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Locations Table
CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    location_type VARCHAR(50) CHECK (location_type IN ('Warehouse', 'Distribution Center', 'Retail Hub', 'Customer Address'))
);

-- 3. Packages Table
CREATE TABLE packages (
    package_id SERIAL PRIMARY KEY,
    tracking_number VARCHAR(50) UNIQUE NOT NULL,
    sender_id INTEGER REFERENCES customers(customer_id),
    recipient_id INTEGER REFERENCES customers(customer_id),
    current_status VARCHAR(50) DEFAULT 'Created',
    weight DECIMAL(10, 2),
    metadata JSONB, -- Stores "fragile", "requires signature", etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Shipments Table (Aggregates multiple packages if needed, but here simple relation)
CREATE TABLE shipments (
    shipment_id SERIAL PRIMARY KEY,
    package_id INTEGER UNIQUE REFERENCES packages(package_id),
    origin_location_id INTEGER REFERENCES locations(location_id),
    destination_location_id INTEGER REFERENCES locations(location_id),
    estimated_delivery TIMESTAMP WITH TIME ZONE,
    actual_delivery TIMESTAMP WITH TIME ZONE
);

-- 5. TrackingEvents Table
CREATE TABLE tracking_events (
    event_id SERIAL PRIMARY KEY,
    package_id INTEGER REFERENCES packages(package_id),
    location_id INTEGER REFERENCES locations(location_id),
    status VARCHAR(50) NOT NULL,
    event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Indexes (Basic ones, composite will be added in Milestone 4)
CREATE INDEX idx_packages_tracking_number ON packages(tracking_number);
CREATE INDEX idx_tracking_events_package_id ON tracking_events(package_id);
