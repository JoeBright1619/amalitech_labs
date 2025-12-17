from abc import ABC, abstractmethod
from ..models import User


class UserRepository(ABC):
    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, user: User) -> None:
        raise NotImplementedError
