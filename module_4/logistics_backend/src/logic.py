from src.db import DatabaseManager


def process_tracking_scan(package_id, location_id, status):
    """
    Processes a tracking scan as a single ACID transaction.
    - Inserts into TrackingEvents
    - Updates Packages status
    """
    conn = DatabaseManager.get_connection()
    try:
        with conn:  # Starts transaction
            with conn.cursor() as cur:
                # 1. Insert tracking event
                cur.execute(
                    """
                    INSERT INTO tracking_events (package_id, location_id, status)
                    VALUES (%s, %s, %s)
                    """,
                    (package_id, location_id, status),
                )

                # 2. Update package current status
                cur.execute(
                    """
                    UPDATE packages
                    SET current_status = %s
                    WHERE package_id = %s
                    """,
                    (status, package_id),
                )
        print(f"Processed scan for package {package_id}: {status}")
        return True
    except Exception as e:
        print(f"Transaction failed: {e}")
        conn.rollback()
        return False
    finally:
        DatabaseManager.release_connection(conn)
