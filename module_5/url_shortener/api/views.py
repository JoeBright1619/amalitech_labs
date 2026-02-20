from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import redirect
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiParameter,
)
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrReadOnly

from .serializers import ShortenUrlSerializer, URLDetailSerializer
from shortener.services import UrlShortenerService
from shortener.repositories import ORMUrlRepository
from shortener.models import URL
from shortener.tasks import fetch_url_preview_task, track_click_task


class ShortenUrlView(GenericAPIView):
    """
    API View to list and create shortened URLs.
    """

    serializer_class = ShortenUrlSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_service(self):
        repo = ORMUrlRepository()
        return UrlShortenerService(repo)

    @extend_schema(
        request=ShortenUrlSerializer,
        responses={
            201: OpenApiResponse(
                description="Short code and full URL created successfully.",
                examples=[
                    OpenApiExample(
                        "Created",
                        value={
                            "short_code": "Ab123",
                            "short_url": "http://localhost:8000/Ab123/",
                        },
                    )
                ],
            )
        },
        description="Submit a long URL to get a shortened code. Supports custom aliases and tags for categorization.",
        examples=[
            OpenApiExample(
                "Basic Usage",
                value={"url": "https://www.google.com"},
                request_only=True,
            ),
            OpenApiExample(
                "Custom Alias & Tags",
                value={
                    "url": "https://www.google.com",
                    "custom_alias": "google-home",
                    "tags": ["Search", "Main"],
                    "title": "Google Search",
                    "description": "Primary search engine",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = request.user
            original_url = serializer.validated_data["url"]
            custom_alias = serializer.validated_data.get("custom_alias")

            # Tiered Logic: Limit Free users to 10 URLs
            if user.tier == user.Tier.FREE:
                active_url_count = URL.objects.filter(
                    owner=user, is_active=True
                ).count()
                if active_url_count >= 10:
                    return Response(
                        {
                            "error": "Free users are limited to 10 active URLs. Upgrade to Premium for unlimited access."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

            # Tiered Logic: Restrict custom aliases to Premium users
            if custom_alias and user.tier == user.Tier.FREE:
                return Response(
                    {"error": "Custom aliases are only available for Premium users."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            service = self.get_service()

            try:
                # Collect all optional fields (excluding title/desc/favicon which are now auto-fetched)
                short_code = service.shorten_url(
                    original_url,
                    user=user,
                    custom_alias=custom_alias,
                    tags=serializer.validated_data.get("tags"),
                    expires_at=serializer.validated_data.get("expires_at"),
                )

                # Trigger Async Preview Fetch
                url_obj = URL.objects.get(short_code=short_code)
                fetch_url_preview_task.delay(url_obj.id, original_url)

                full_short_url = request.build_absolute_uri(f"/{short_code}/")

                return Response(
                    {"short_code": short_code, "short_url": full_short_url},
                    status=status.HTTP_201_CREATED,
                )
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="List all shortened URLs owned by the authenticated user. Supports pagination and search by tag.",
        responses={200: URLDetailSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="tag",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter URLs by tag name.",
            ),
        ],
    )
    def get(self, request):
        # Optimized query using the manager method we defined earlier
        urls = URL.objects.filter(owner=request.user).with_details()

        # Search by tag
        tag_name = request.query_params.get("tag")
        if tag_name:
            urls = urls.filter(tags__name__iexact=tag_name)

        page = self.paginate_queryset(urls)
        if page is not None:
            serializer = URLDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = URLDetailSerializer(urls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RedirectView(APIView):
    """
    View to redirect to the original URL.
    """

    def get_service(self):
        repo = ORMUrlRepository()
        return UrlShortenerService(repo)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    @extend_schema(
        description="Redirect to the original URL based on the short code.",
        responses={302: None, 404: dict, 410: dict},
    )
    def get(self, request, short_code):
        from django.core.cache import cache

        # Check Cache first
        # We store the original_url directly in cache
        cached_url = cache.get(f"url:{short_code}")

        # Simple mock IP intelligence for demonstration
        ip = self.get_client_ip(request)
        country = (
            "US"
            if ip and ip.startswith("192.")
            else "GH" if ip and ip.startswith("127.") else "UK"
        )

        click_data = {
            "ip_address": ip,
            "user_agent": request.META.get("HTTP_USER_AGENT"),
            "referrer": request.META.get("HTTP_REFERER"),
            "city": (
                "Accra"
                if country == "GH"
                else "London" if country == "UK" else "New York"
            ),
            "country": country,
        }

        import logging

        logger = logging.getLogger(__name__)
        print(f"DEBUG: RedirectView hit for {short_code}")

        if cached_url:
            print(f"DEBUG: Cache HIT for {short_code}")
            logger.info(f"Cache HIT for {short_code}")
            # Trigger Async Analytics
            try:
                track_click_task.delay(short_code, click_data)
            except Exception as e:
                logger.error(f"Failed to trigger async task: {e}")
            return redirect(cached_url)

        # Cache Miss
        service = self.get_service()
        try:
            # log_click=False because we will trigger the async task
            original_url = service.get_original_url(
                short_code, click_data=None, log_click=False
            )
        except ValueError as e:
            # Service raises ValueError for expired or inactive URLs
            return Response({"error": str(e)}, status=status.HTTP_410_GONE)

        if original_url:
            logger.info(f"Cache MISS for {short_code}. Caching and redirecting.")
            # Cache the result for 15 minutes
            try:
                cache.set(f"url:{short_code}", original_url, timeout=60 * 15)
            except Exception as e:
                logger.error(f"Failed to set cache: {e}")

            # Trigger Async Analytics
            try:
                track_click_task.delay(short_code, click_data)
            except Exception as e:
                logger.error(f"Failed to trigger async task: {e}")

            return redirect(original_url)

        return Response(
            {"error": "Short code not found"}, status=status.HTTP_404_NOT_FOUND
        )


class UrlAnalyticsView(APIView):
    """
    API View to retrieve analytics for a shortened URL.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get detailed analytics for a shortened URL. Premium users get geo-location and time-series data.",
        responses={
            200: OpenApiResponse(
                description="Analytics data.",
                examples=[
                    OpenApiExample(
                        "Premium Success",
                        value={
                            "short_code": "Ab123",
                            "total_clicks": 255,
                            "geo_breakdown": [
                                {"country": "US", "total_clicks": 150},
                                {"country": "UK", "total_clicks": 85},
                            ],
                            "time_series": [
                                {"date": "2023-10-01", "total_clicks": 10},
                                {"date": "2023-10-02", "total_clicks": 15},
                            ],
                        },
                    ),
                    OpenApiExample(
                        "Free Success",
                        value={
                            "short_code": "Ab123",
                            "total_clicks": 255,
                        },
                    ),
                ],
            ),
            404: OpenApiResponse(description="Short code not found"),
            403: OpenApiResponse(description="Permission denied"),
        },
    )
    def get(self, request, short_code):
        try:
            url_obj = URL.objects.get(short_code=short_code)

            # Authorization check
            if url_obj.owner != request.user:
                return Response(
                    {"error": "You do not have permission to view these analytics."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            response_data = {
                "short_code": short_code,
                "total_clicks": url_obj.click_count,
            }

            # Tiered Logic: Access to detailed analytics restricted to Premium/Admin
            if request.user.tier != request.user.Tier.FREE:
                response_data["geo_breakdown"] = url_obj.clicks_per_country()
                response_data["time_series"] = url_obj.clicks_over_time()

            return Response(response_data, status=status.HTTP_200_OK)
        except URL.DoesNotExist:
            return Response(
                {"error": "Short code not found"}, status=status.HTTP_404_NOT_FOUND
            )


class UrlDetailView(APIView):
    """
    API View to retrieve, update or delete a specific URL.
    """

    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self, short_code):
        try:
            url_obj = URL.objects.get(short_code=short_code)
            self.check_object_permissions(self.request, url_obj)
            return url_obj
        except URL.DoesNotExist:
            return None

    @extend_schema(
        responses={200: URLDetailSerializer},
        description="Get full details of a shortened URL. Only accessible by the owner.",
    )
    def get(self, request, short_code):
        url_obj = self.get_object(short_code)
        if not url_obj:
            return Response(
                {"error": "Short code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = URLDetailSerializer(url_obj)
        return Response(serializer.data)

    @extend_schema(
        request=ShortenUrlSerializer,
        responses={200: URLDetailSerializer},
        description="Update a shortened URL. Only accessible by the owner. Supports optional click count reset.",
        parameters=[
            OpenApiParameter(
                name="reset_clicks",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Reset the click count for this URL if true.",
            ),
        ],
    )
    def put(self, request, short_code):
        url_obj = self.get_object(short_code)
        if not url_obj:
            return Response(
                {"error": "Short code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ShortenUrlSerializer(data=request.data)
        if serializer.is_valid():
            # Apply updates
            url_obj.original_url = serializer.validated_data["url"]
            url_obj.title = serializer.validated_data.get("title", url_obj.title)
            url_obj.description = serializer.validated_data.get(
                "description", url_obj.description
            )
            url_obj.custom_alias = serializer.validated_data.get(
                "custom_alias", url_obj.custom_alias
            )
            url_obj.expires_at = serializer.validated_data.get(
                "expires_at", url_obj.expires_at
            )

            # Click count reset logic
            reset_clicks = (
                request.query_params.get("reset_clicks", "false").lower() == "true"
            )
            if reset_clicks:
                url_obj.click_count = 0
                # Delete related clicks for detailed stats
                url_obj.clicks.all().delete()

            url_obj.save()
            return Response(URLDetailSerializer(url_obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=ShortenUrlSerializer,
        responses={200: URLDetailSerializer},
        description="Partially update a shortened URL. Only accessible by the owner.",
    )
    def patch(self, request, short_code):
        url_obj = self.get_object(short_code)
        if not url_obj:
            return Response(
                {"error": "Short code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ShortenUrlSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            # Apply updates
            if "url" in serializer.validated_data:
                url_obj.original_url = serializer.validated_data["url"]
            if "title" in serializer.validated_data:
                url_obj.title = serializer.validated_data["title"]
            if "description" in serializer.validated_data:
                url_obj.description = serializer.validated_data["description"]
            if "custom_alias" in serializer.validated_data:
                url_obj.custom_alias = serializer.validated_data["custom_alias"]
            if "expires_at" in serializer.validated_data:
                url_obj.expires_at = serializer.validated_data["expires_at"]

            url_obj.save()
            return Response(URLDetailSerializer(url_obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: None},
        description="Delete a shortened URL. Only accessible by the owner.",
    )
    def delete(self, request, short_code):
        url_obj = self.get_object(short_code)
        if not url_obj:
            return Response(
                {"error": "Short code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        url_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
