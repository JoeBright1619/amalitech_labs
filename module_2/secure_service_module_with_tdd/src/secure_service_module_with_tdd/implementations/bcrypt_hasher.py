import bcrypt
from ..interfaces.hasher import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    """Implementation of PasswordHasher using the bcrypt library."""

    def hash(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
