from .interfaces.repository import UserRepository
from .interfaces.hasher import PasswordHasher
from .models import User
from .exceptions import (
    UserAlreadyExistsError,
    InvalidPasswordError,
    UserNotFoundError,
)


class UserService:
    def __init__(
        self,
        repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._repository = repository
        self._password_hasher = password_hasher

    def register_user(self, username: str, password: str) -> User:
        if len(password) < 8:
            raise InvalidPasswordError("Password too short")

        existing = self._repository.get_by_username(username)
        if existing:
            raise UserAlreadyExistsError(f"User {username} already exists")

        user = user = User(
            username=username, password_hash=self._password_hasher.hash(password)
        )
        self._repository.save(user)
        return user

    def authenticate_user(self, username: str, password: str) -> User:
        user = self._repository.get_by_username(username)

        if not user:
            raise UserNotFoundError(f"User {username} not found")

        if not self._password_hasher.verify(password, user.password_hash):
            raise InvalidPasswordError("Invalid credentials")

        return user
