from src.db import DatabaseManager
import redis
import pymongo
import os
import json
import datetime

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    decode_responses=True,
)

# MongoDB connection
mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"))
mongo_db = mongo_client[os.getenv("MONGO_DB", "logistics_logs")]
mongo_collection = mongo_db["scan_events"]


def process_tracking_scan(package_id, location_id, status):
    """
    Processes a tracking scan as a single ACID transaction (PG)
    plus updates Redis cache and logs to MongoDB.
    """
    conn = DatabaseManager.get_connection()
    try:
        # 1. PostgreSQL Transaction
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO tracking_events (package_id, location_id, status) VALUES (%s, %s, %s)",
                    (package_id, location_id, status),
                )
                cur.execute(
                    "UPDATE packages SET current_status = %s WHERE package_id = %s",
                    (status, package_id),
                )

        print(f"PG: Processed scan for package {package_id}: {status}")

        # 2. Redis Cache Update
        cache_key = f"package:{package_id}:status"
        cache_value = json.dumps(
            {
                "status": status,
                "location_id": location_id,
                "updated_at": datetime.datetime.now().isoformat(),
            }
        )
        redis_client.set(cache_key, cache_value)
        print(f"Redis: Updated cache for {cache_key}")

        # 3. MongoDB Logging
        log_entry = {
            "package_id": package_id,
            "location_id": location_id,
            "status": status,
            "raw_timestamp": datetime.datetime.now(),
            "scanner_id": "SCAN_001",  # Placeholder
            "meta": "Raw scan data",
        }
        mongo_collection.insert_one(log_entry)
        print(f"Mongo: Logged raw event for {package_id}")

        return True

    except Exception as e:
        print(f"Transaction/Processing failed: {e}")
        conn.rollback()
        return False
    finally:
        DatabaseManager.release_connection(conn)


def get_package_status(package_id):
    """Retrieves status from Redis cache or falls back to DB."""
    cache_key = f"package:{package_id}:status"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Fallback to DB (simplified)
    # In real app, query PG and populate cache
    return None
