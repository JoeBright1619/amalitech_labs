import redis
from django.conf import settings
from .interfaces import IUrlRepository
from typing import Optional


class RedisUrlRepository(IUrlRepository):
    """
    Redis-backed implementation of the URL repository.
    """

    def __init__(self):
        # Establish connection using the REDIS_URL from settings
        # decode_responses=True ensures we get strings back instead of bytes
        self.client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    def save_mapping(self, short_code: str, original_url: str) -> None:
        """
        Save the mapping to Redis.
        Key: short_code, Value: original_url
        """
        self.client.set(short_code, original_url)

    def get_original_url(self, short_code: str) -> Optional[str]:
        """
        Retrieve original URL from Redis.
        """
        return self.client.get(short_code)

    def exists(self, short_code: str) -> bool:
        """
        Check if the short code exists in Redis.
        """
        return bool(self.client.exists(short_code))
