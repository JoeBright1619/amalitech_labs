from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APIClient
from shortener.models import URL
from django.contrib.auth import get_user_model

User = get_user_model()


class CachingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear()
        self.user = User.objects.create_user(
            username="testuser", password="password", tier="Premium", is_premium=True
        )
        self.client.force_authenticate(user=self.user)
        self.url_obj = URL.objects.create(
            short_code="cached", original_url="https://example.com", owner=self.user
        )

    def test_redis_cache_hit_on_redirect(self):
        """Test that redirect uses cache on second attempt."""
        redirect_url = reverse(
            "redirect_url", kwargs={"short_code": self.url_obj.short_code}
        )

        # First request: Cache Miss, should hit DB (we can't easily assertNumQueries if service is reused, but we check cache)
        response = self.client.get(redirect_url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(
            cache.get(f"url:{self.url_obj.short_code}"), self.url_obj.original_url
        )

        # Second request: Cache Hit
        # We can patch RedirectView.get_service to ensure it's not called if hit cache (actually views.py checks cache FIRST)
        with patch("api.views.RedirectView.get_service") as mock_service:
            response = self.client.get(redirect_url)
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            # Service should NOT be called because it returns from cache early
            self.assertFalse(mock_service.called)

    def test_cache_invalidation_on_update(self):
        """Test that updating a URL clears its cache entry."""
        # Prime the cache
        cache.set(f"url:{self.url_obj.short_code}", "https://old.com")

        # Update via API
        detail_url = reverse(
            "v1:url_detail", kwargs={"short_code": self.url_obj.short_code}
        )
        self.client.patch(detail_url, {"original_url": "https://new.com"})

        # Cache should be invalidated (actually we need to check if the View/Model handles invalidation)
        # Note: I need to verify if the codebase actually implements invalidation.
        # Checking views.py: class UrlDetailView: put/patch calls url_obj.save().
        # Does the model have a signal or does the view clear cache? Actually, I don't see it in views.py.
        # I might need to suggest/implement it.

        # Let's check the current value. If it's still "old.com", invalidation failed.
        self.assertIsNone(cache.get(f"url:{self.url_obj.short_code}"))


class HealthEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.health_url = reverse("v1:health_check")

    def test_health_success(self):
        """Test health endpoint returns 200 when everything is up."""
        response = self.client.get(self.health_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")

    @patch("django.db.connection.cursor")
    def test_health_db_fails(self, mock_cursor):
        """Test health endpoint returns 503 when DB is down."""
        mock_cursor.side_effect = Exception("DB Connection Error")
        response = self.client.get(self.health_url)
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["status"], "error")
        self.assertIn("db", response.data["components"])

    @patch("django.core.cache.cache.set")
    def test_health_redis_fails(self, mock_cache_set):
        """Test health endpoint returns 503 when Redis is down."""
        mock_cache_set.side_effect = Exception("Redis Error")
        response = self.client.get(self.health_url)
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["status"], "error")
        self.assertIn("redis", response.data["components"])
