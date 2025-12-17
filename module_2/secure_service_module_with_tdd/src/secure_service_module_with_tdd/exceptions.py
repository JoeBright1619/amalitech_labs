class AuthServiceError(Exception):
    """Base exception for authentication service."""


class UserAlreadyExistsError(AuthServiceError):
    pass


class UserNotFoundError(AuthServiceError):
    pass


class InvalidPasswordError(AuthServiceError):
    pass
