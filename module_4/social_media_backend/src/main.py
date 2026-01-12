import os
from src.database.postgres_db import db
from src.database.redis_cache import redis_cache
from src.database.mongo_logger import mongo_logger


def initialize_system():
    print("Starting Social Media Backend Initialization...")

    # Initialize PostgreSQL Schema
    schema_path = os.path.join(os.path.dirname(__file__), "models", "schema.sql")
    if os.path.exists(schema_path):
        print(f"Loading schema from {schema_path}...")
        db.init_db(schema_path)
    else:
        print(f"Error: Schema file not found at {schema_path}")

    # Check Redis
    if redis_cache.client:
        print("Redis is ready.")
    else:
        print("Warning: Redis client not connected.")

    # Check MongoDB
    if mongo_logger.client:
        print("MongoDB is ready.")
    else:
        print("Warning: MongoDB client not connected.")


if __name__ == "__main__":
    initialize_system()
