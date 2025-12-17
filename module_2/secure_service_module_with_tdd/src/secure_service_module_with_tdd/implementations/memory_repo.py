from ..interfaces.repository import UserRepository
from ..models import User


class InMemoryUserRepository(UserRepository):
    def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError

    def save(self, user: User) -> None:
        raise NotImplementedError
