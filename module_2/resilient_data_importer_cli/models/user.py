from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """
    Represents a user entity.

    Attributes:
        user_id: Unique identifier for the user.
        name: Full name of the user.
        email: Email address of the user.
    """

    user_id: str
    name: str
    email: str
