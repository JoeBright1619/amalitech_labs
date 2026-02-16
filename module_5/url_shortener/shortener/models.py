from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models import Count


class User(AbstractUser):
    """
    Custom User model extending AbstractUser.
    Includes fields for tier management and premium status.
    """

    class Tier(models.TextChoices):
        FREE = "Free", _("Free")
        PREMIUM = "Premium", _("Premium")
        ADMIN = "Admin", _("Admin")

    email = models.EmailField(_("email address"), unique=True, blank=False)
    is_premium = models.BooleanField(
        default=False, help_text="Designates whether the user has premium access."
    )
    tier = models.CharField(
        max_length=10,
        choices=Tier.choices,
        default=Tier.FREE,
    )

    REQUIRED_FIELDS = ["email", "tier"]

    def __str__(self):
        return self.username


class Tag(models.Model):
    """
    Model for categorizing URLs.
    """

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class URLQuerySet(models.QuerySet):
    """
    Custom QuerySet for URL model with business logic methods.
    """

    def active_urls(self):
        return self.filter(is_active=True)

    def expired_urls(self):
        from django.utils import timezone

        return self.filter(expires_at__lt=timezone.now())

    def popular_urls(self, min_clicks=100):
        return self.filter(click_count__gte=min_clicks)

    def with_details(self):
        return self.select_related("owner").prefetch_related("tags")


class URLManager(models.Manager.from_queryset(URLQuerySet)):
    """
    Custom manager for URL model.
    """

    pass


class URL(models.Model):
    """
    Model to store original and shortened URLs.
    """

    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=10, unique=True, db_index=True)
    custom_alias = models.CharField(max_length=50, unique=True, null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="urls"
    )
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    favicon = models.URLField(null=True, blank=True)
    click_count = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True, related_name="urls")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = URLManager()

    class Meta:
        verbose_name = _("URL")
        verbose_name_plural = _("URLs")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"

    @property
    def is_expired(self):
        """Checks if the URL has passed its expiration date."""
        if self.expires_at:
            from django.utils import timezone

            return timezone.now() > self.expires_at
        return False

    @property
    def is_valid(self):
        """Checks if the URL is active and not expired."""
        return self.is_active and not self.is_expired

    def clicks_per_country(self):
        """
        Returns a list of dicts with country and total clicks.
        Example: [{'country': 'US', 'total_clicks': 10}, ...]
        """
        return (
            self.clicks.values("country")
            .annotate(total_clicks=Count("id"))
            .order_by("-total_clicks")
        )


class Click(models.Model):
    """
    Analytics model to log every visit to a short link.
    """

    url = models.ForeignKey(URL, on_delete=models.CASCADE, related_name="clicks")
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    referrer = models.URLField(max_length=2000, null=True, blank=True)

    class Meta:
        verbose_name = _("Click")
        verbose_name_plural = _("Clicks")
        ordering = ["-clicked_at"]

    def __str__(self):
        return f"Click on {self.url.short_code} at {self.clicked_at}"
