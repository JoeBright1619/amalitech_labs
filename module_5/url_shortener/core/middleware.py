import logging
import time

logger = logging.getLogger("django.request")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        # Process request
        response = self.get_response(request)

        duration = time.time() - start_time

        # Log request details
        log_data = {
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration": f"{duration:.4f}s",
            "ip": self.get_client_ip(request),
        }

        logger.info(f"Request: {log_data}")

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
