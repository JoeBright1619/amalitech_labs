import secrets
import string
from .interfaces import IUrlRepository


class UrlShortenerService:
    """
    Service layer containing business logic for URL shortening.
    Uses dependency injection for the repository.
    """

    def __init__(self, repository: IUrlRepository):
        self.repository = repository
        self.CODE_LENGTH = 6
        self.CHAR_SET = string.ascii_letters + string.digits

    def shorten_url(self, original_url: str) -> str:
        """
        Generates a unique short code for the given URL and saves the mapping.
        """
        # Logic to generate unique code
        # simplified collision handling for lab purposes
        short_code = self._generate_random_code()

        # Ensure uniqueness (simple retry mechanism)
        while self.repository.exists(short_code):
            short_code = self._generate_random_code()

        self.repository.save_mapping(short_code, original_url)
        return short_code

    def get_original_url(self, short_code: str) -> str:
        """
        Retrieves the original URL. Returns None if not found.
        (Caller should handle 404)
        """
        return self.repository.get_original_url(short_code)

    def _generate_random_code(self) -> str:
        """Helper to generate a random string."""
        return "".join(secrets.choice(self.CHAR_SET) for _ in range(self.CODE_LENGTH))
