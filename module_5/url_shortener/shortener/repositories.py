import redis
from django.conf import settings
from .interfaces import IUrlRepository
from typing import Optional


from .models import URL, Click, Tag


class RedisUrlRepository(IUrlRepository):
    """
    Redis-backed implementation of the URL repository.
    """

    def __init__(self):
        # Establish connection using the REDIS_URL from settings
        # decode_responses=True ensures we get strings back instead of bytes
        self.client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    def save_mapping(
        self, short_code: str, original_url: str, user=None, **kwargs
    ) -> None:
        """
        Save the mapping to Redis.
        Key: short_code, Value: original_url
        """
        # Redis doesn't store user/ownership in this simple key-value implementation
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

    def log_click(self, short_code: str, click_data: dict) -> None:
        """
        Log click in Redis (Simple counter impl or pass).
        """
        # For this lab, we focus on ORM analytics.
        pass


class ORMUrlRepository(IUrlRepository):
    """
    Django ORM-backed implementation of the URL repository.
    """

    def save_mapping(
        self, short_code: str, original_url: str, user=None, **kwargs
    ) -> None:
        """
        Save the mapping to the Database.
        """
        url_obj = URL.objects.create(
            short_code=short_code,
            original_url=original_url,
            owner=user,
            title=kwargs.get("title"),
            description=kwargs.get("description"),
            favicon=kwargs.get("favicon"),
            expires_at=kwargs.get("expires_at"),
            custom_alias=kwargs.get("custom_alias"),
        )

        # Handle tags
        tags = kwargs.get("tags", [])
        if tags:
            for tag_name in tags:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                url_obj.tags.add(tag)

    def get_original_url(self, short_code: str) -> Optional[str]:
        """
        Retrieve original URL from Database.
        """
        try:
            url_obj = URL.objects.get(short_code=short_code)
            return url_obj.original_url
        except URL.DoesNotExist:
            return None

    def get_url_by_code(self, short_code: str) -> Optional[URL]:
        """
        Retrieve URL object from Database.
        """
        try:
            return URL.objects.get(short_code=short_code)
        except URL.DoesNotExist:
            return None

    def exists(self, short_code: str) -> bool:
        """
        Check if the short code exists in Database.
        """
        return URL.objects.filter(short_code=short_code).exists()

    def log_click(self, short_code: str, click_data: dict) -> None:
        """
        Log a click in the database.
        """
        try:
            url_obj = URL.objects.get(short_code=short_code)
            # Increment counter
            url_obj.click_count += 1
            url_obj.save(update_fields=["click_count"])

            # Create detailed click record
            Click.objects.create(
                url=url_obj,
                ip_address=click_data.get("ip_address"),
                city=click_data.get("city"),
                country=click_data.get("country"),
                user_agent=click_data.get("user_agent"),
                referrer=click_data.get("referrer"),
            )
        except URL.DoesNotExist:
            pass
