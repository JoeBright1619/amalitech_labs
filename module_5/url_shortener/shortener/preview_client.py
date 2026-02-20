import httpx
import logging
from django.conf import settings
from django.core.cache import cache
from urllib.parse import urlparse
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)


class PreviewServiceClient:
    """
    Client for interacting with the external Preview Service.
    Includes retry logic (exponential backoff) and a circuit breaker.
    """

    FAILURE_THRESHOLD = 5
    COOLDOWN_SECONDS = 60

    def fetch_preview(self, url: str) -> dict:
        domain = self._get_domain(url)

        if self._is_circuit_open(domain):
            logger.warning(
                f"Circuit open for domain: {domain}. Skipping preview fetch."
            )
            return {"title": None, "description": "Circuit Open", "favicon": None}

        try:
            preview = self._call_service_with_retry(url)
            self._record_success(domain)
            return preview
        except Exception as e:
            logger.error(f"Failed to fetch preview for {url} after retries: {str(e)}")
            self._record_failure(domain)
            return {
                "title": None,
                "description": f"Fetch failed: {str(e)}",
                "favicon": None,
            }

    @retry(
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _call_service_with_retry(self, url: str) -> dict:
        with httpx.Client(timeout=5.0) as client:
            response = client.post(settings.PREVIEW_SERVICE_URL, json={"url": url})
            response.raise_for_status()
            return response.json()

    def _get_domain(self, url: str) -> str:
        try:
            return urlparse(url).netloc
        except Exception:
            return "unknown"

    def _is_circuit_open(self, domain: str) -> bool:
        failures = cache.get(f"cb:failures:{domain}", 0)
        return failures >= self.FAILURE_THRESHOLD

    def _record_failure(self, domain: str):
        key = f"cb:failures:{domain}"
        current = cache.get(key, 0)
        cache.set(key, current + 1, timeout=self.COOLDOWN_SECONDS)

    def _record_success(self, domain: str):
        cache.delete(f"cb:failures:{domain}")
