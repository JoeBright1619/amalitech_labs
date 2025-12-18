from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    """Interface for password hashing and verification."""

    @abstractmethod
    def hash(self, password: str) -> str:
        """Hash a plain-text password."""
        raise NotImplementedError

    @abstractmethod
    def verify(self, password: str, password_hash: str) -> bool:
        """Verify a plain-text password against a hash."""
        raise NotImplementedError
