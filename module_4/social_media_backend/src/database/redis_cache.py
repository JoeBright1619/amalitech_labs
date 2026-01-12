import os
import redis
from dotenv import load_dotenv

load_dotenv()


class RedisCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisCache, cls).__new__(cls)
            cls._instance._initialize_client()
        return cls._instance

    def _initialize_client(self):
        try:
            self.client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                decode_responses=True,
            )
            print("Redis client initialized.")
        except Exception as e:
            print(f"Error connecting to Redis: {e}")
            self.client = None

    def set_cache(self, key, value, ex=None):
        if self.client:
            self.client.set(key, value, ex=ex)

    def get_cache(self, key):
        if self.client:
            return self.client.get(key)
        return None


redis_cache = RedisCache()
