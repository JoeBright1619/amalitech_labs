import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db import DatabaseManager
import time


def run_benchmark():
    conn = DatabaseManager.get_connection()
    try:
        with conn.cursor() as cur:
            # Complex Query: Reconstruct history with time spread
            query = """
            WITH package_history AS (
                SELECT 
                    package_id,
                    status,
                    location_id,
                    event_timestamp,
                    LAG(event_timestamp) OVER (PARTITION BY package_id ORDER BY event_timestamp) as prev_timestamp
                FROM tracking_events
            )
            SELECT 
                package_id,
                status,
                event_timestamp,
                prev_timestamp,
                EXTRACT(EPOCH FROM (event_timestamp - prev_timestamp)) as quantity_seconds_diff
            FROM package_history
            WHERE package_id = 1
            ORDER BY event_timestamp;
            """

            print("--- Running EXPLAIN ANALYZE (Before Index) ---")
            cur.execute(f"EXPLAIN ANALYZE {query}")
            for row in cur.fetchall():
                print(row[0])

            # Create Composite Index
            print("\n--- Creating Composite Index ---")
            start_time = time.time()
            cur.execute(
                "CREATE INDEX idx_tracking_composite ON tracking_events (package_id, event_timestamp);"
            )
            conn.commit()
            print(f"Index created in {time.time() - start_time:.4f}s")

            print("\n--- Running EXPLAIN ANALYZE (After Index) ---")
            cur.execute(f"EXPLAIN ANALYZE {query}")
            for row in cur.fetchall():
                print(row[0])

    except Exception as e:
        print(f"Benchmark failed: {e}")
    finally:
        DatabaseManager.release_connection(conn)


if __name__ == "__main__":
    run_benchmark()
