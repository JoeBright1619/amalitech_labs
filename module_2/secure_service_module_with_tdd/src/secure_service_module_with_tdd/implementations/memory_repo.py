from ..interfaces.repository import UserRepository
from ..models import User


class InMemoryUserRepository(UserRepository):
    """In-memory implementation of UserRepository for testing and local use."""

    def __init__(self) -> None:
        """Initialize the in-memory store."""
        # Simple in-memory store
        self._users: dict[str, User] = {}

    def get_by_username(self, username: str) -> User | None:
        """Retrieve a user from memory by username."""
        return self._users.get(username)

    def save(self, user: User) -> None:
        """Save a user to memory."""
        self._users[user.username] = user
