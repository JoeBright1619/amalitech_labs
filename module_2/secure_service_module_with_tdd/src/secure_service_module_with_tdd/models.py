from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """
    Represents a user in the system.

    Attributes:
        username: The unique name of the user.
        password_hash: The hashed representation of the user's password.
    """

    username: str
    password_hash: str
