from django.urls import path
from .views import ShortenUrlView, RedirectView, UrlAnalyticsView, UserUrlListView

urlpatterns = [
    path("api/shorten/", ShortenUrlView.as_view(), name="shorten_url"),
    path("api/my-urls/", UserUrlListView.as_view(), name="user_urls"),
    path(
        "api/analytics/<str:short_code>/",
        UrlAnalyticsView.as_view(),
        name="url_analytics",
    ),
    path("<str:short_code>/", RedirectView.as_view(), name="redirect_url"),
]
