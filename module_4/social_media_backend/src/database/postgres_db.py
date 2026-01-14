import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()


class PostgresDB:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostgresDB, cls).__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance

    def _initialize_pool(self):
        try:
            self._pool = pool.SimpleConnectionPool(
                1,
                10,
                user=os.getenv("PG_USER"),
                password=os.getenv("PG_PASSWORD"),
                host=os.getenv("PG_HOST"),
                port=os.getenv("PG_PORT"),
                database=os.getenv("PG_DB"),
            )
            print("PostgreSQL connection pool initialized.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error while connecting to PostgreSQL: {error}")
            self._pool = None

    def get_connection(self):
        if self._pool:
            return self._pool.getconn()
        return None

    def put_connection(self, conn):
        if self._pool:
            self._pool.putconn(conn)

    def close_all_connections(self):
        if self._pool:
            self._pool.closeall()

    def init_db(self, schema_file_path):
        """Initializes the database with the provided schema file."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    with open(schema_file_path, "r") as f:
                        cursor.execute(f.read())
                conn.commit()
                print("Database initialized successfully.")
            except (Exception, psycopg2.DatabaseError) as error:
                print(f"Error initializing database: {error}")
                conn.rollback()
            finally:
                self.put_connection(conn)


db = PostgresDB()
