from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import ShortenUrlSerializer
from .services import UrlShortenerService
from .repositories import RedisUrlRepository


class ShortenUrlView(APIView):
    """
    API View to shorten a URL.
    """

    serializer_class = ShortenUrlSerializer

    def get_service(self):
        repo = RedisUrlRepository()
        return UrlShortenerService(repo)

    @extend_schema(
        request=ShortenUrlSerializer,
        responses={
            201: OpenApiExample(
                "Created",
                value={
                    "short_code": "Ab123",
                    "short_url": "http://localhost:8000/Ab123/",
                },
            )
        },
        description="Submit a long URL to get a shortened code.",
        examples=[
            OpenApiExample(
                "Valid Example",
                value={"url": "https://www.google.com"},
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            original_url = serializer.validated_data["url"]
            service = self.get_service()

            try:
                short_code = service.shorten_url(original_url)
                full_short_url = request.build_absolute_uri(f"/{short_code}/")

                return Response(
                    {"short_code": short_code, "short_url": full_short_url},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RedirectView(APIView):
    """
    View to redirect to the original URL.
    """

    def get_service(self):
        repo = RedisUrlRepository()
        return UrlShortenerService(repo)

    @extend_schema(
        description="Redirect to the original URL based on the short code.",
        responses={302: None, 404: dict},
    )
    def get(self, request, short_code):
        service = self.get_service()
        original_url = service.get_original_url(short_code)

        if original_url:
            return redirect(original_url)

        return Response(
            {"error": "Short code not found"}, status=status.HTTP_404_NOT_FOUND
        )
