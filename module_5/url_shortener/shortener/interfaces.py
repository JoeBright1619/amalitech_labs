from abc import ABC, abstractmethod
from typing import Optional


class IUrlRepository(ABC):
    """
    Interface for URL storage repository.
    Decouples the service layer from the concrete data store (Redis, DB, etc).
    """

    @abstractmethod
    def save_mapping(self, short_code: str, original_url: str) -> None:
        """
        Save a short code to original URL mapping.
        """
        pass

    @abstractmethod
    def get_original_url(self, short_code: str) -> Optional[str]:
        """
        Retrieve the original URL for a given short code.
        Returns None if not found.
        """
        pass

    @abstractmethod
    def exists(self, short_code: str) -> bool:
        """
        Check if a short code already exists.
        """
        pass
