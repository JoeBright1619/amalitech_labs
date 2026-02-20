"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from api.views import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/v1/", include(("api.urls", "api"), namespace="v1")),
    path(
        "preview/",
        include(("preview_service.urls", "preview_service"), namespace="preview"),
    ),
    # Root redirect handled by API view now
    path("<str:short_code>/", RedirectView.as_view(), name="redirect_url"),
]
