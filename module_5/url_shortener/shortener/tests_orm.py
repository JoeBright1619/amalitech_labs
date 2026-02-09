from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import URL, Tag, Click

User = get_user_model()


class ORMIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.shorten_url = reverse("shorten_url")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            tier="Premium",
        )
        # Authenticate usually via token in DRF, but here we can force login if using session or just mock request.user
        self.client.force_authenticate(user=self.user)

        # Tags are seeded by migration, check if they exist or create for test
        if not Tag.objects.filter(name="Marketing").exists():
            Tag.objects.create(name="Marketing")

    def test_shorten_url_with_user_and_alias(self):
        """
        Test shortening a URL with an authenticated user and a custom alias.
        """
        data = {"url": "https://www.example.com", "custom_alias": "myalias"}
        response = self.client.post(self.shorten_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["short_code"], "myalias")

        # Verify DB
        url = URL.objects.get(short_code="myalias")
        self.assertEqual(url.original_url, "https://www.example.com")
        self.assertEqual(url.owner, self.user)
        self.assertEqual(url.click_count, 0)

    def test_custom_alias_collision(self):
        """
        Test that using an existing alias fails.
        """
        URL.objects.create(
            short_code="taken", original_url="http://foo.com", owner=self.user
        )

        data = {"url": "https://www.example.com", "custom_alias": "taken"}
        response = self.client.post(self.shorten_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_click_logging(self):
        """
        Test that accessing the redirect URL logs a click.
        """
        code = "clicks"
        url_obj = URL.objects.create(
            short_code=code, original_url="https://www.example.com", owner=self.user
        )

        url = reverse("redirect_url", kwargs={"short_code": code})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # Refresh from DB
        url_obj.refresh_from_db()
        self.assertEqual(url_obj.click_count, 1)

        # Check Click model
        self.assertTrue(Click.objects.filter(url=url_obj).exists())
        click = Click.objects.filter(url=url_obj).first()
        self.assertIsNotNone(click.ip_address)

    def test_url_manager_methods(self):
        """
        Test custom manager methods.
        """
        URL.objects.create(
            short_code="active",
            original_url="http://a.com",
            owner=self.user,
            is_active=True,
        )
        URL.objects.create(
            short_code="inactive",
            original_url="http://b.com",
            owner=self.user,
            is_active=False,
        )

        self.assertEqual(URL.objects.active_urls().count(), 1)
        # Note: Previous tests created generic URLs which might default to active=True, so count might be higher if DB not flushed properly per test
        # Django TestCase flushes DB between tests, so it should be fine.
        # However, setUp creates nothing.
        # test_shorten_url_with_user_and_alias creates one if run before. But independent transactions.

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
