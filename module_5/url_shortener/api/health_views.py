from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache
from drf_spectacular.utils import extend_schema


class HealthCheckView(APIView):
    """
    Health check endpoint to verify DB and Cache connectivity.
    """

    permission_classes = []

    @extend_schema(
        description="Check health status of the service (DB and Redis).",
        responses={200: dict, 503: dict},
    )
    def get(self, request):
        health_status = {"status": "ok", "components": {}}

        # Check Database
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status["components"]["db"] = "healthy"
        except Exception as e:
            health_status["status"] = "error"
            health_status["components"]["db"] = f"unhealthy: {str(e)}"

        # Check Redis
        try:
            cache.set("health_check_key", "value", timeout=1)
            value = cache.get("health_check_key")
            if value == "value":
                health_status["components"]["redis"] = "healthy"
            else:
                raise Exception("Redis set/get failed")
        except Exception as e:
            health_status["status"] = "error"
            health_status["components"]["redis"] = f"unhealthy: {str(e)}"

        status_code = (
            status.HTTP_200_OK
            if health_status["status"] == "ok"
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        return Response(health_status, status=status_code)
