from .interfaces.repository import UserRepository
from .interfaces.hasher import PasswordHasher


class UserService:
    def __init__(
        self,
        repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._repository = repository
        self._password_hasher = password_hasher
