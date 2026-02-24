from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.cache import cache
from shortener.models import URL


User = get_user_model()


class AuthTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.register_url = reverse("v1:register")
        self.login_url = reverse("v1:login")
        self.url_list_url = reverse("v1:url_list_create")

    def test_registration_success(self):
        """Test user registration with valid data."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "password_confirm": "password123",
            "tier": "Free",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="newuser")
        self.assertEqual(user.email, "new@example.com")
        self.assertTrue(user.check_password("password123"))
        self.assertFalse(user.is_premium)

    def test_registration_unique_email(self):
        """Test registration fails with duplicate email."""
        User.objects.create_user(
            username="user1", email="duplicate@example.com", password="password123"
        )
        data = {
            "username": "user2",
            "email": "duplicate@example.com",
            "password": "password123",
            "password_confirm": "password123",
            "tier": "Free",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_jwt_login_success(self):
        """Test JWT token issuance with valid credentials."""
        User.objects.create_user(
            username="loginuser", email="login@example.com", password="password123"
        )
        data = {"username": "loginuser", "password": "password123"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_jwt_login_invalid(self):
        """Test login fails with invalid credentials."""
        User.objects.create_user(
            username="loginuser_fail",
            email="login_fail@example.com",
            password="password123",
        )
        data = {"username": "loginuser_fail", "password": "wrongpassword"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PermissionTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="password123",
            is_premium=True,
            tier="Premium",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="password123",
            is_premium=True,
            tier="Premium",
        )
        self.url_obj = URL.objects.create(
            short_code="u1code", original_url="https://user1.com", owner=self.user1
        )
        self.detail_url = reverse(
            "v1:url_detail", kwargs={"short_code": self.url_obj.short_code}
        )

    def test_owner_can_update_delete(self):
        """Test owner can update and delete their own URL."""
        self.client.force_authenticate(user=self.user1)

        # Update
        response = self.client.patch(
            self.detail_url, {"original_url": "https://new.com"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete (deactivate by default)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.url_obj.refresh_from_db()
        self.assertFalse(self.url_obj.is_active)

    def test_non_owner_cannot_update_delete(self):
        """Test user cannot update or delete another user's URL."""
        self.client.force_authenticate(user=self.user2)

        # Update
        response = self.client.patch(
            self.detail_url, {"original_url": "https://hack.com"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Delete
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RBACTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.free_user = User.objects.create_user(
            username="free",
            email="free@example.com",
            password="password",
            tier="Free",
            is_premium=False,
        )
        self.premium_user = User.objects.create_user(
            username="premium",
            email="premium@example.com",
            password="password",
            tier="Premium",
            is_premium=True,
        )
        self.shorten_url = reverse("v1:url_list_create")

    def test_free_user_quota_enforcement(self):
        """Test free users are limited to 10 active URLs."""
        self.client.force_authenticate(user=self.free_user)

        # Create 10 URLs
        for i in range(10):
            URL.objects.create(
                short_code=f"c{i}", original_url="http://x.com", owner=self.free_user
            )

        # 11th attempt should fail
        response = self.client.post(self.shorten_url, {"url": "http://google.com"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("limit", response.data["error"].lower())

    def test_premium_custom_alias_feature(self):
        """Test custom aliases are premium-only."""
        # Free user fails
        self.client.force_authenticate(user=self.free_user)
        response = self.client.post(
            self.shorten_url, {"url": "http://a.com", "custom_alias": "myfav"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Premium user succeeds
        self.client.force_authenticate(user=self.premium_user)
        response = self.client.post(
            self.shorten_url, {"url": "http://a.com", "custom_alias": "myfav"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["short_code"], "myfav")


class ThrottlingTests(APITestCase):
    def setUp(self):
        cache.clear()

    def test_login_rate_limiting(self):
        """Test more than 5 login attempts triggers rate limiting."""
        login_url = reverse("v1:login")
        data = {"username": "user", "password": "wrongpassword"}

        # 5 attempts allowed (assuming default config is 5/min as per requirement)
        for i in range(5):
            response = self.client.post(login_url, data)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 6th attempt should be throttled
        response = self.client.post(login_url, data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
