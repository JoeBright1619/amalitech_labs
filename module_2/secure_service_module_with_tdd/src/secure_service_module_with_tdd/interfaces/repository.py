from abc import ABC, abstractmethod
from ..models import User


class UserRepository(ABC):
    """Interface for user data storage."""

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        """Retrieve a user by their username."""
        raise NotImplementedError

    @abstractmethod
    def save(self, user: User) -> None:
        """Save a user to the repository."""
        raise NotImplementedError
