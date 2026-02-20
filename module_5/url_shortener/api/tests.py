from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch


from django.contrib.auth import get_user_model

User = get_user_model()


class ApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.shorten_url = reverse("v1:shorten_url")
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.force_authenticate(user=self.user)

    @patch("api.views.UrlShortenerService")
    @patch("api.views.fetch_url_preview_task.delay")
    def test_shorten_url_success(self, mock_preview_delay, mock_service_class):
        """
        Test that posting a valid URL returns a short code and triggers preview task.
        """
        # Mocking the service instance and its method
        mock_service_instance = mock_service_class.return_value
        mock_service_instance.shorten_url.return_value = "TestCode"

        # Mocking URL object return for views logic
        from shortener.models import URL

        with patch("api.views.URL.objects.get") as mock_url_get:
            mock_url_obj = URL(
                id=1, short_code="TestCode", original_url="https://www.example.com"
            )
            mock_url_get.return_value = mock_url_obj

            data = {"url": "https://www.example.com"}
            response = self.client.post(self.shorten_url, data, format="json")

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data["short_code"], "TestCode")
            self.assertIn("/TestCode/", response.data["short_url"])

            # Verify preview task was triggered
            mock_preview_delay.assert_called_once_with(
                mock_url_obj.id, "https://www.example.com"
            )

    def test_shorten_url_invalid(self):
        """
        Test that posting an invalid URL returns 400.
        """
        data = {"url": "not-a-url"}
        response = self.client.post(self.shorten_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("api.views.UrlShortenerService")
    def test_redirect_success(self, mock_service_class):
        """
        Test that accessing a valid short code redirects to the original URL.
        """
        mock_service_instance = mock_service_class.return_value
        mock_service_instance.get_original_url.return_value = "https://www.example.com"

        url = reverse("redirect_url", kwargs={"short_code": "TestCode"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, "https://www.example.com")

    @patch("api.views.UrlShortenerService")
    def test_redirect_not_found(self, mock_service_class):
        """
        Test that accessing a non-existent short code returns 404.
        """
        mock_service_instance = mock_service_class.return_value
        mock_service_instance.get_original_url.return_value = None

        url = reverse("redirect_url", kwargs={"short_code": "Missing"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
