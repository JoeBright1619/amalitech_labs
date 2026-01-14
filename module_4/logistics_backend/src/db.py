import os
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    _pool = None

    @classmethod
    def initialize_pool(cls):
        if cls._pool is None:
            try:
                cls._pool = pool.SimpleConnectionPool(
                    1,
                    10,
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    host=os.getenv("DB_HOST"),
                    port=os.getenv("DB_PORT"),
                    database=os.getenv("DB_NAME"),
                )
                print("Connection pool initialized successfully.")
            except Exception as e:
                print(f"Error initializing connection pool: {e}")
                raise

    @classmethod
    def get_connection(cls):
        if cls._pool is None:
            cls.initialize_pool()
        return cls._pool.getconn()

    @classmethod
    def release_connection(cls, conn):
        if cls._pool:
            cls._pool.putconn(conn)

    @classmethod
    def close_all(cls):
        if cls._pool:
            cls._pool.closeall()
