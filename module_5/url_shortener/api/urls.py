from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    ShortenUrlView,
    UrlAnalyticsView,
    UrlDetailView,
)
from .auth_views import RegisterView, LoginView
from .health_views import HealthCheckView

app_name = "api"

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # URL Operations
    path("urls/", ShortenUrlView.as_view(), name="url_list_create"),
    path("urls/<str:short_code>/", UrlDetailView.as_view(), name="url_detail"),
    path(
        "analytics/<str:short_code>/",
        UrlAnalyticsView.as_view(),
        name="url_analytics",
    ),
    path("health/", HealthCheckView.as_view(), name="health_check"),
]
