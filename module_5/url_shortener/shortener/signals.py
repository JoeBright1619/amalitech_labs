from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import URL


@receiver(post_save, sender=URL)
@receiver(post_delete, sender=URL)
def invalidate_url_cache(sender, instance, **kwargs):
    """
    Invalidate the Redis cache for a URL when it is created, updated, or deleted.
    """
    cache_key = f"url:{instance.short_code}"
    cache.delete(cache_key)
