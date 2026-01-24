from django.urls import path
from .views import ShortenUrlView, RedirectView

urlpatterns = [
    path("api/shorten/", ShortenUrlView.as_view(), name="shorten_url"),
    path("<str:short_code>/", RedirectView.as_view(), name="redirect_url"),
]
