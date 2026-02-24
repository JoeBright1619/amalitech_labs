from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from django.urls import reverse
from shortener.models import URL, Click

User = get_user_model()


class AnalyticsIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            tier="Premium",
            is_premium=True,
        )

    def test_analytics_aggregation(self):
        """
        Test that clicks_per_country returns correct aggregation.
        """
        url_obj = URL.objects.create(
            short_code="analytics", original_url="http://stats.com", owner=self.user
        )

        Click.objects.create(url=url_obj, country="US")
        Click.objects.create(url=url_obj, country="US")
        Click.objects.create(url=url_obj, country="UK")

        stats = url_obj.clicks_per_country()
        # stats should look like [{'country': 'US', 'total_clicks': 2}, {'country': 'UK', 'total_clicks': 1}]

        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0]["country"], "US")
        self.assertEqual(stats[0]["total_clicks"], 2)
        self.assertEqual(stats[1]["country"], "UK")
        self.assertEqual(stats[1]["total_clicks"], 1)

    def test_premium_only_analytics_access(self):
        """Test free users cannot access detailed analytics."""
        free_user = User.objects.create_user(
            username="free_analytics",
            email="free_a@ex.com",
            password="password",
            tier="Free",
        )
        url_obj = URL.objects.create(
            short_code="fcode", original_url="http://x.com", owner=free_user
        )

        self.client = APIClient()
        self.client.force_authenticate(user=free_user)

        analytics_url = reverse(
            "v1:url_analytics", kwargs={"short_code": url_obj.short_code}
        )
        response = self.client.get(analytics_url)

        # Depending on implementation, it might return 200 but WITHOUT geo/time data
        # Check views.py: if user.tier == FREE, it only returns short_code and total_clicks.
        self.assertNotIn("geo_breakdown", response.data)
        self.assertNotIn("time_series", response.data)

    def test_click_count_denormalization(self):
        """Test click_count increments correctly and matches Click records."""
        url_obj = URL.objects.create(
            short_code="denorm", original_url="http://d.com", owner=self.user
        )

        # Initial
        self.assertEqual(url_obj.click_count, 0)

        # Add clicks
        from shortener.tasks import track_click_task

        track_click_task(url_obj.short_code, {"ip_address": "1.1.1.1", "country": "US"})
        track_click_task(url_obj.short_code, {"ip_address": "2.2.2.2", "country": "GH"})

        url_obj.refresh_from_db()
        self.assertEqual(url_obj.click_count, 2)
        self.assertEqual(url_obj.clicks.count(), 2)
