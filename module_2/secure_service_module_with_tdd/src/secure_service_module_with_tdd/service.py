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
    """
    Service for managing user registration and authentication.

    This service orchestrates the business logic for user management,
    leveraging repository and password hashing abstractions.
    """

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
        """
        Register a new user with a username and password.

        Args:
            username: The unique username for the new user.
            password: The plain-text password (must be at least 8 characters).

        Returns:
            The newly created User object.

        Raises:
            InvalidPasswordError: If the password is less than 8 characters.
            UserAlreadyExistsError: If a user with the same username already exists.
        """
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
        """
        Authenticate a user by username and password.

        Args:
            username: The username of the user.
            password: The plain-text password to verify.

        Returns:
            The authenticated User object.

        Raises:
            UserNotFoundError: If the user does not exist.
            InvalidPasswordError: If the password verification fails.
        """
        user = self._repository.get_by_username(username)

        if not user:
            raise UserNotFoundError(f"User {username} not found")

        if not self._password_hasher.verify(password, user.password_hash):
            self._logger.warning("Failed login attempt", extra={"username": username})
            raise InvalidPasswordError("Invalid credentials")

        return user
