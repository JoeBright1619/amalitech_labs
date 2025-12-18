from typing import Protocol, Dict
from ..models.user import User


class JsonUserRepository(Protocol):
    """Protocol defining the interface for a user repository."""

    def add(self, user: User) -> None:
        """Add a user to the repository."""
        ...

    def list_all(self) -> Dict[str, dict]:
        """List all users in the repository."""
        ...
