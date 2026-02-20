import httpx
from bs4 import BeautifulSoup
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny


@method_decorator(csrf_exempt, name="dispatch")
class PreviewView(APIView):
    """
    Standalone microservice view to fetch metadata (title, description, favicon)
    from a target URL.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        print("DATA:", request.data)
        print("CONTENT TYPE:", request.content_type)

        url = request.data.get("url")

        if not url:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"PreviewView received unexpected data: {request.data}")
            return Response(
                {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch the page
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            with httpx.Client(follow_redirects=True, timeout=5.0) as client:
                resp = client.get(url, headers=headers)
                resp.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(resp.text, "html.parser")

            # 1. Title
            title = soup.title.string.strip() if soup.title else None

            # 2. Description
            desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find(
                "meta", attrs={"property": "og:description"}
            )
            description = (
                desc_tag["content"].strip()
                if desc_tag and desc_tag.has_attr("content")
                else None
            )

            # 3. Favicon
            icon_tag = soup.find("link", rel=lambda r: r and "icon" in r.lower())
            favicon = None
            if icon_tag and icon_tag.has_attr("href"):
                favicon = icon_tag["href"]
                # Resolve relative URLs
                if favicon.startswith("//"):
                    favicon = f"https:{favicon}"
                elif favicon.startswith("/"):
                    from urllib.parse import urljoin

                    favicon = urljoin(url, favicon)
                elif not favicon.startswith("http"):
                    from urllib.parse import urljoin

                    favicon = urljoin(url, favicon)

            if not favicon:
                from urllib.parse import urljoin

                favicon = urljoin(url, "/favicon.ico")

            return Response(
                {"title": title, "description": description, "favicon": favicon},
                status=status.HTTP_200_OK,
            )

        except httpx.HTTPStatusError as e:
            return Response(
                {
                    "title": None,
                    "description": f"HTTP Error: {e.response.status_code}",
                    "favicon": None,
                },
                status=status.HTTP_200_OK,
            )  # Return 200 with nulls as per plan
        except Exception as e:
            return Response(
                {"title": None, "description": str(e), "favicon": None},
                status=status.HTTP_200_OK,
            )
