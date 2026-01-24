from .interfaces import IUrlRepository
from typing import Optional, Dict


class RedisUrlRepository(IUrlRepository):
    """
    Temporary In-Memory implementation for Milestone 3.
    Will be replaced with actual Redis implementation in Milestone 4.
    """

    _storage: Dict[str, str] = {}

    def save_mapping(self, short_code: str, original_url: str) -> None:
        self._storage[short_code] = original_url

    def get_original_url(self, short_code: str) -> Optional[str]:
        return self._storage.get(short_code)

    def exists(self, short_code: str) -> bool:
        return short_code in self._storage
