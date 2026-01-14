import sys
import os

# Add the current directory to sys.path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db import DatabaseManager
from src.logic import process_tracking_scan


def seed_data():
    conn = DatabaseManager.get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Clear existing data
                cur.execute(
                    "TRUNCATE tracking_events, shipments, packages, locations, customers RESTART IDENTITY CASCADE"
                )

                # 1. Locations
                cur.execute(
                    "INSERT INTO locations (location_name, city, state, location_type) VALUES ('Accra Hub', 'Accra', 'Greater Accra', 'Warehouse') RETURNING location_id"
                )
                loc1 = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO locations (location_name, city, state, location_type) VALUES ('Kumasi Sorting Office', 'Kumasi', 'Ashanti', 'Distribution Center') RETURNING location_id"
                )
                loc2 = cur.fetchone()[0]

                # 2. Customers
                cur.execute(
                    "INSERT INTO customers (name, email, address) VALUES ('Alice Mensah', 'alice@example.com', '123 Osu St, Accra') RETURNING customer_id"
                )
                c1 = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO customers (name, email, address) VALUES ('Bob Kojo', 'bob@example.com', '456 Adum Rd, Kumasi') RETURNING customer_id"
                )
                c2 = cur.fetchone()[0]

                # 3. Packages
                cur.execute(
                    "INSERT INTO packages (tracking_number, sender_id, recipient_id, weight, metadata) VALUES (%s, %s, %s, %s, %s) RETURNING package_id",
                    ("PKG-ABC-001", c1, c2, 12.5, '{"fragile": true, "express": true}'),
                )
                p1 = cur.fetchone()[0]

        print("Base data seeded successfully.")

        # Test transactional scan processing
        print("Processing scans...")
        process_tracking_scan(p1, loc1, "Picked Up")
        process_tracking_scan(p1, loc1, "In Transit")
        process_tracking_scan(p1, loc2, "Arrived at Facility")

    except Exception as e:
        print(f"Error seeding data: {e}")
    finally:
        DatabaseManager.release_connection(conn)


if __name__ == "__main__":
    seed_data()
