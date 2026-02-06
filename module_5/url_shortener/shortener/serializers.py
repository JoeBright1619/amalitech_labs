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

    def validate_url(self, value):
        blocked_domains = ["localhost", "127.0.0.1"]

        if value.startswith("ftp://"):
            raise serializers.ValidationError("Only HTTP/HTTPS URLs are allowed.")

        for domain in blocked_domains:
            if domain in value:
                raise serializers.ValidationError("This domain is not allowed.")

        return value
