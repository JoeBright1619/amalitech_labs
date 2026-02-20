import httpx
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from shortener.preview_client import PreviewServiceClient
from django.core.cache import cache


class PreviewServiceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.fetch_url = reverse("preview:preview_fetch")

    @patch("preview_service.views.httpx.Client")
    def test_preview_fetch_success(self, mock_client):
        """
        Test that PreviewView successfully parses a mock HTML response.
        """
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="This is a test description">
                <link rel="icon" href="/favicon.ico">
            </head>
            <body></body>
        </html>
        """
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_instance = mock_client.return_value.__enter__.return_value
        mock_instance.get.return_value = mock_response

        response = self.client.post(
            self.fetch_url, {"url": "https://example.com"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Page")
        self.assertEqual(response.data["description"], "This is a test description")
        self.assertEqual(response.data["favicon"], "https://example.com/favicon.ico")

    def test_preview_fetch_missing_url(self):
        response = self.client.post(self.fetch_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PreviewClientTests(TestCase):
    def setUp(self):
        self.client = PreviewServiceClient()
        cache.clear()

    @patch("shortener.preview_client.httpx.Client")
    def test_client_retry_logic(self, mock_client):
        """
        Test that PreviewServiceClient retries on failure.
        """
        mock_instance = mock_client.return_value.__enter__.return_value

        # Fail twice, then succeed
        mock_instance.post.side_effect = [
            httpx.RequestError("Network error"),
            httpx.RequestError("Network error"),
            MagicMock(
                status_code=200,
                json=lambda: {
                    "title": "Success",
                    "description": "Desc",
                    "favicon": "Fav",
                },
            ),
        ]

        # Note: We need to decrease the wait time for tests to run fast
        # But PreviewServiceClient uses wait_exponential.
        # We can patch the retry decorator or just wait.
        # For simplicity in this environment, let's just assert the call count.

        with patch("tenacity.nap.time.sleep", return_value=None):
            result = self.client.fetch_preview("https://retry.com")

        self.assertEqual(result["title"], "Success")
        self.assertEqual(mock_instance.post.call_count, 3)

    @patch("shortener.preview_client.httpx.Client")
    def test_circuit_breaker_opens(self, mock_client):
        """
        Test that circuit breaker opens after multiple failures.
        """
        mock_instance = mock_client.return_value.__enter__.return_value
        mock_instance.post.side_effect = httpx.RequestError("Permanent error")

        # 5 failures should open the circuit
        for _ in range(5):
            self.client.fetch_preview("https://fail.com")

        self.assertEqual(
            mock_instance.post.call_count, 5 * 3
        )  # 5 attempts * 3 retries each

        # 6th call should skip and return circuit open message
        result = self.client.fetch_preview("https://fail.com")
        self.assertEqual(result["description"], "Circuit Open")
        self.assertEqual(mock_instance.post.call_count, 15)  # No more calls to httpx
