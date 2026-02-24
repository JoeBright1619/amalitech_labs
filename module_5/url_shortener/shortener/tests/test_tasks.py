from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from shortener.models import URL, Click
from shortener.tasks import track_click_task, archive_expired_urls_task
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@ex.com", password="password"
        )
        self.url_obj = URL.objects.create(
            short_code="task-test", original_url="https://example.com", owner=self.user
        )

    def test_track_click_task(self):
        """Test track_click_task creates a Click record."""
        click_data = {
            "ip_address": "8.8.8.8",
            "user_agent": "TestBot",
            "referer": "http://ref.com",
        }

        result = track_click_task(self.url_obj.short_code, click_data)

        self.assertIn("Click tracked", result)
        self.assertTrue(
            Click.objects.filter(url=self.url_obj, ip_address="8.8.8.8").exists()
        )
        self.url_obj.refresh_from_db()
        self.assertEqual(self.url_obj.click_count, 1)

    def test_archive_expired_urls_task(self):
        """Test periodic task deactivates expired URLs."""
        # Active but expired
        URL.objects.create(
            short_code="expired-1",
            original_url="http://expired.com",
            owner=self.user,
            is_active=True,
            expires_at=timezone.now() - timedelta(hours=1),
        )
        # Not expired
        URL.objects.create(
            short_code="active-1",
            original_url="http://active.com",
            owner=self.user,
            is_active=True,
            expires_at=timezone.now() + timedelta(hours=1),
        )

        result = archive_expired_urls_task()
        self.assertIn("Deactivated 1", result)

        self.assertFalse(URL.objects.get(short_code="expired-1").is_active)
        self.assertTrue(URL.objects.get(short_code="active-1").is_active)
