import secrets
import string
from .interfaces import IUrlRepository

# from .exceptions import InvalidUrlException # Not used

# Checking existing exceptions.py: it exists.


class UrlShortenerService:
    """
    Service layer containing business logic for URL shortening.
    Uses dependency injection for the repository.
    """

    def __init__(self, repository: IUrlRepository):
        self.repository = repository
        # Use a slightly longer set or just ascii
        self.CODE_LENGTH = 6
        self.CHAR_SET = string.ascii_letters + string.digits

    def shorten_url(
        self, original_url: str, user=None, custom_alias: str = None, **kwargs
    ) -> str:
        """
        Generates a unique short code for the given URL and saves the mapping.
        If custom_alias is provided, verifies it's available.
        Additional metadata can be passed via kwargs.
        """

        if custom_alias:
            if self.repository.exists(custom_alias):
                raise ValueError(f"Custom alias '{custom_alias}' is already taken.")
            short_code = custom_alias
        else:
            # Logic to generate unique code
            short_code = self._generate_random_code()
            # Ensure uniqueness (simple retry mechanism)
            while self.repository.exists(short_code):
                short_code = self._generate_random_code()

        self.repository.save_mapping(short_code, original_url, user=user, **kwargs)
        return short_code

    def get_original_url(self, short_code: str, click_data: dict = None) -> str:
        """
        Retrieves the original URL and logs the click if found.
        Returns None if not found.
        Raises ValueError if URL is expired or inactive.
        """
        # We need the full object to check business rules
        # ORM repository must implement get_url_by_code
        if hasattr(self.repository, "get_url_by_code"):
            url_obj = self.repository.get_url_by_code(short_code)
        else:
            # Fallback for Redis or other simple repos that haven't implemented this yet
            # This logic assumes simple key-value store where we can't check expiry easily
            return self.repository.get_original_url(short_code)

        if not url_obj:
            return None

        # Business Logic: Check Expiry and Active Status
        if not url_obj.is_active:
            raise ValueError("URL is inactive")

        if url_obj.is_expired:
            raise ValueError("URL has expired")

        # Log Click
        if click_data:
            self.repository.log_click(short_code, click_data)

        return url_obj.original_url

    def _generate_random_code(self) -> str:
        """Helper to generate a random string."""
        return "".join(secrets.choice(self.CHAR_SET) for _ in range(self.CODE_LENGTH))
