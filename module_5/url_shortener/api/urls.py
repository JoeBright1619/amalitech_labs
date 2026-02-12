from django.urls import path
from .views import ShortenUrlView, RedirectView, UrlAnalyticsView, UserUrlListView

urlpatterns = [
    path("shorten/", ShortenUrlView.as_view(), name="shorten_url"),
    path("my-urls/", UserUrlListView.as_view(), name="user_urls"),
    path(
        "analytics/<str:short_code>/",
        UrlAnalyticsView.as_view(),
        name="url_analytics",
    ),
    path("r/<str:short_code>/", RedirectView.as_view(), name="redirect_url_api"),
]
