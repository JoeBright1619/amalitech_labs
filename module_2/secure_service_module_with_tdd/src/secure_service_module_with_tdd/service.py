from .interfaces.repository import UserRepository
from .interfaces.hasher import PasswordHasher
from .models import User
from .exceptions import (
    UserAlreadyExistsError,
    InvalidPasswordError,
    UserNotFoundError,
)
import logging


class UserService:
    def __init__(
        self,
        repository: UserRepository,
        password_hasher: PasswordHasher,
        logger: logging.Logger | None = None,
    ) -> None:
        self._repository = repository
        self._password_hasher = password_hasher
        self._logger = logger or logging.getLogger(__name__)

    def register_user(self, username: str, password: str) -> User:
        if len(password) < 8:
            raise InvalidPasswordError("Password too short")

        if self._repository.get_by_username(username):
            raise UserAlreadyExistsError(f"User {username} already exists")

        password_hash = self._password_hasher.hash(password)
        user = User(username=username, password_hash=password_hash)
        self._repository.save(user)

        self._logger.info("User registered", extra={"username": username})

        return user

    def authenticate_user(self, username: str, password: str) -> User:
        user = self._repository.get_by_username(username)

        if not user:
            raise UserNotFoundError(f"User {username} not found")

        if not self._password_hasher.verify(password, user.password_hash):
            self._logger.warning("Failed login attempt", extra={"username": username})
            raise InvalidPasswordError("Invalid credentials")

        return user
