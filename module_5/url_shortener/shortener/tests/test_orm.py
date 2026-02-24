from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch
from shortener.models import URL, Tag, Click

User = get_user_model()


class ORMIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.shorten_url = reverse("v1:url_list_create")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            tier="Free",
            is_premium=False,
        )
        self.premium_user = User.objects.create_user(
            username="premiumuser",
            email="premium@example.com",
            password="password123",
            tier="Premium",
            is_premium=True,
        )
        self.client.force_authenticate(user=self.premium_user)

        # Tags are seeded by migration, check if they exist or create for test
        if not Tag.objects.filter(name="Marketing").exists():
            Tag.objects.create(name="Marketing")

    @patch("api.views.fetch_url_preview_task.delay")
    def test_shorten_url_with_user_and_alias(self, mock_preview_delay):
        """
        Test shortening a URL with an authenticated user and a custom alias.
        """
        data = {"url": "https://www.example.com", "custom_alias": "myalias"}
        response = self.client.post(self.shorten_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["short_code"], "myalias")

        # Verify preview task was triggered
        url = URL.objects.get(short_code="myalias")
        mock_preview_delay.assert_called_once_with(url.id, "https://www.example.com")

        # Verify DB
        url = URL.objects.get(short_code="myalias")
        self.assertEqual(url.original_url, "https://www.example.com")
        self.assertEqual(url.owner, self.premium_user)
        self.assertEqual(url.click_count, 0)

    def test_custom_alias_collision(self):
        """
        Test that using an existing alias fails.
        """
        URL.objects.create(
            short_code="taken", original_url="http://foo.com", owner=self.premium_user
        )

        data = {"url": "https://www.example.com", "custom_alias": "taken"}
        response = self.client.post(self.shorten_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("api.views.track_click_task.delay")
    def test_click_logging(self, mock_click_delay):
        """
        Test that accessing the redirect URL triggers an async click log task.
        """
        code = "clicks"
        URL.objects.create(
            short_code=code,
            original_url="https://www.example.com",
            owner=self.premium_user,
        )
        # We need to make sure the view executes using a tracked URL code
        url = reverse("redirect_url", kwargs={"short_code": code})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # Verify async task was triggered
        self.assertTrue(mock_click_delay.called)
        # Check that it was called with the correct short_code
        args, _ = mock_click_delay.call_args
        self.assertEqual(args[0], code)

    def test_owner_relationship(self):
        """Test owner relationship and cascade delete."""
        url = URL.objects.create(
            short_code="owner", original_url="http://owner.com", owner=self.user
        )
        self.assertEqual(url.owner.username, "testuser")

        # Test cascade delete
        self.user.delete()
        self.assertFalse(URL.objects.filter(short_code="owner").exists())

    def test_tag_relationship(self):
        """Test many-to-many relationship with tags."""
        url = URL.objects.create(
            short_code="tags", original_url="http://tags.com", owner=self.premium_user
        )
        tag1 = Tag.objects.create(name="Tech")
        tag2 = Tag.objects.create(name="News")

        url.tags.add(tag1, tag2)

        self.assertEqual(url.tags.count(), 2)
        self.assertIn(tag1, url.tags.all())

        # Test duplicate tag name uniqueness
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Tech")

    def test_url_manager_methods(self):
        """
        Test custom manager methods.
        """
        from django.utils import timezone
        import datetime

        URL.objects.create(
            short_code="active",
            original_url="http://a.com",
            owner=self.premium_user,
            is_active=True,
        )
        # Note: Previous tests create URLs with active=True by default, so active count might be > 1.
        # We will check based on the ones we create now.
        URL.objects.create(
            short_code="inactive",
            original_url="http://b.com",
            owner=self.premium_user,
            is_active=False,
        )

        # Expired
        URL.objects.create(
            short_code="expired",
            original_url="http://c.com",
            owner=self.premium_user,
            is_active=True,
            expires_at=timezone.now() - datetime.timedelta(days=1),
        )

        # Popular
        URL.objects.create(
            short_code="popular",
            original_url="http://d.com",
            owner=self.premium_user,
            is_active=True,
            click_count=150,
        )

        # check that active_urls filters correctly
        self.assertTrue(
            URL.objects.filter(short_code="active").first() in URL.objects.active_urls()
        )
        self.assertFalse(
            URL.objects.filter(short_code="inactive").first()
            in URL.objects.active_urls()
        )

        # Expired
        self.assertEqual(URL.objects.expired_urls().count(), 1)
        self.assertEqual(URL.objects.expired_urls().first().short_code, "expired")

        # Popular
        self.assertEqual(URL.objects.popular_urls(100).count(), 1)
        self.assertEqual(URL.objects.popular_urls(100).first().short_code, "popular")

    def test_click_logging_integrity(self):
        """Test click logging model integrity."""
        url = URL.objects.create(
            short_code="integrity",
            original_url="http://integrity.com",
            owner=self.premium_user,
        )
        click = Click.objects.create(
            url=url, ip_address="127.0.0.1", user_agent="Mozilla/5.0"
        )

        self.assertEqual(click.url, url)
        self.assertEqual(click.ip_address, "127.0.0.1")
        self.assertEqual(click.user_agent, "Mozilla/5.0")

    def test_n_plus_1_optimization(self):
        """Test that with_details() optimizes queries."""
        for i in range(5):
            u = URL.objects.create(
                short_code=f"opt{i}",
                original_url=f"http://opt{i}.com",
                owner=self.premium_user,
            )
            tag, _ = Tag.objects.get_or_create(name=f"Tag{i}")
            u.tags.add(tag)

        # Using with_details() should result in exactly 2 queries: one for URLs+Owners, one for Tags
        with self.assertNumQueries(2):
            urls = list(URL.objects.with_details())
            for u in urls:
                _ = u.owner.username
                _ = list(u.tags.all())
