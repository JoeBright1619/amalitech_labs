from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    ShortenUrlView,
    UrlAnalyticsView,
    UserUrlListView,
    UrlDetailView,
)
from .auth_views import RegisterView, LoginView
from .health_views import HealthCheckView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("shorten/", ShortenUrlView.as_view(), name="shorten_url"),
    path("my-urls/", UserUrlListView.as_view(), name="user_urls"),
    path(
        "analytics/<str:short_code>/",
        UrlAnalyticsView.as_view(),
        name="url_analytics",
    ),
    path(
        "urls/<str:short_code>/",
        UrlDetailView.as_view(),
        name="url_detail",
    ),
    path("health/", HealthCheckView.as_view(), name="health_check"),
]
