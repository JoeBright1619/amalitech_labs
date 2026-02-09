from rest_framework import serializers


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
