from django.contrib import admin
from .models import URL, Click, Tag


@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = (
        "short_code",
        "original_url",
        "owner",
        "click_count",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "owner", "created_at")
    search_fields = ("short_code", "original_url")
    readonly_fields = ("created_at", "updated_at", "click_count")
    ordering = ("-created_at",)


@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ("url", "clicked_at", "ip_address", "country", "user_agent")
    list_filter = ("clicked_at", "country")
    search_fields = ("ip_address", "user_agent")
    readonly_fields = ("clicked_at",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
