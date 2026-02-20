from celery import shared_task
from django.utils import timezone
from .models import URL
from .repositories import ORMUrlRepository


@shared_task
def track_click_task(short_code, click_data):
    """
    Background task to log a click event for a shortened URL.
    """
    repo = ORMUrlRepository()
    repo.log_click(short_code, click_data)
    return f"Click tracked for {short_code}"


@shared_task
def archive_expired_urls_task():
    """
    Periodic task to deactivate expired URLs.
    """
    # Deactivate URLs that have expired but are still marked active
    updated_count = URL.objects.filter(
        expires_at__lt=timezone.now(), is_active=True
    ).update(is_active=False)

    return f"Deactivated {updated_count} expired URLs"


@shared_task(bind=True, max_retries=3)
def fetch_url_preview_task(self, url_id: int, original_url: str):
    """
    Fetches title, description, favicon from the Preview Service
    and saves them to the URL record.
    """
    from .preview_client import PreviewServiceClient

    try:
        client = PreviewServiceClient()
        preview = client.fetch_preview(original_url)
        URL.objects.filter(pk=url_id).update(
            title=preview.get("title"),
            description=preview.get("description"),
            favicon=preview.get("favicon"),
        )
        return f"Preview fetched for URL ID {url_id}"
    except Exception as exc:
        # Retry with exponential backoff if something unexpected happens
        raise self.retry(exc=exc, countdown=2**self.request.retries)
