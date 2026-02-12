from rest_framework import serializers
from shortener.models import URL, Tag


class ShortenUrlSerializer(serializers.Serializer):
    """
    Serializer for validating the URL input.
    """

    url = serializers.URLField(
        required=True,
        error_messages={
            "invalid": "Enter a valid URL.",
            "required": "URL field is required.",
        },
    )
    custom_alias = serializers.CharField(
        required=False,
        allow_null=True,
        max_length=10,
        help_text="Optional custom alias for premium users.",
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        help_text="Optional list of tags for categorization.",
    )
    title = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    favicon = serializers.URLField(required=False, allow_null=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name"]


class URLDetailSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = URL
        fields = [
            "short_code",
            "original_url",
            "custom_alias",
            "title",
            "description",
            "click_count",
            "owner_username",
            "tags",
            "created_at",
        ]
