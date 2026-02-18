from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import URL


@receiver(pre_save, sender=URL)
def invalidate_url_cache_on_update(sender, instance, **kwargs):
    # If object is new, skip
    if not instance.pk:
        return

    try:
        old_instance = URL.objects.get(pk=instance.pk)
    except URL.DoesNotExist:
        return

    # Only invalidate if original_url changed
    if old_instance.original_url != instance.original_url:
        cache_key = f"url:{instance.short_code}"
        cache.delete(cache_key)
        print(f"Cache invalidated for {cache_key}")


@receiver(post_delete, sender=URL)
def invalidate_url_cache_on_delete(sender, instance, **kwargs):
    cache_key = f"url:{instance.short_code}"
    cache.delete(cache_key)
    print(f"Cache invalidated (delete) for {cache_key}")
