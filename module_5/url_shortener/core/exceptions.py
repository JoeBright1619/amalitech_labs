from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns a consistent JSON response
    for all exceptions.
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Standardize DRF errors
        data = response.data
        if isinstance(data, list):
            data = {"errors": data}
        elif isinstance(data, dict) and "detail" in data:
            data = {"error": data["detail"]}

        response.data = data
    else:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        response = Response(
            {"error": "Internal configuration error or unexpected fault."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
