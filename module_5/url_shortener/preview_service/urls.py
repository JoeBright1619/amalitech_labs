from django.urls import path
from .views import PreviewView

urlpatterns = [
    path("fetch/", PreviewView.as_view(), name="preview_fetch"),
]
