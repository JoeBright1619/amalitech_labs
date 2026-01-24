from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Placeholder views for Milestone 2 - Implementation in Milestone 3


class ShortenUrlView(APIView):
    def post(self, request):
        return Response(
            {"message": "Not implemented yet"}, status=status.HTTP_501_NOT_IMPLEMENTED
        )


class RedirectView(APIView):
    def get(self, request, short_code):
        return Response(
            {"message": "Not implemented yet"}, status=status.HTTP_501_NOT_IMPLEMENTED
        )
