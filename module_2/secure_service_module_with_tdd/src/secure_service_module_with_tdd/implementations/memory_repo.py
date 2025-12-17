from ..interfaces.repository import UserRepository
from ..models import User


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        # Simple in-memory store
        self._users: dict[str, User] = {}

    def get_by_username(self, username: str) -> User | None:
        return self._users.get(username)

    def save(self, user: User) -> None:
        self._users[user.username] = user
