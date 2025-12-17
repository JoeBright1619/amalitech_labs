import pytest
from src.secure_service_module_with_tdd.service import UserService
from src.secure_service_module_with_tdd.implementations.memory_repo import (
    InMemoryUserRepository,
)
from src.secure_service_module_with_tdd.implementations.bcrypt_hasher import (
    BcryptPasswordHasher,
)
from src.secure_service_module_with_tdd.exceptions import InvalidPasswordError


def test_logs_user_registration(mocker):
    repo = InMemoryUserRepository()
    hasher = BcryptPasswordHasher()
    logger = mocker.Mock()

    service = UserService(repo, hasher, logger=logger)

    service.register_user("alice", "strongpassword")

    logger.info.assert_called_once_with("User registered", extra={"username": "alice"})


def test_logs_failed_login_attempt(mocker):
    repo = InMemoryUserRepository()
    hasher = BcryptPasswordHasher()
    logger = mocker.Mock()

    service = UserService(repo, hasher, logger=logger)
    service.register_user("alice", "strongpassword")

    with pytest.raises(InvalidPasswordError):
        service.authenticate_user("alice", "wrongpassword")

    logger.warning.assert_called_once_with(
        "Failed login attempt", extra={"username": "alice"}
    )
