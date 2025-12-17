import pytest
from src.secure_service_module_with_tdd.service import UserService
from src.secure_service_module_with_tdd.implementations.memory_repo import (
    InMemoryUserRepository,
)
from src.secure_service_module_with_tdd.implementations.bcrypt_hasher import (
    BcryptPasswordHasher,
)
from src.secure_service_module_with_tdd.exceptions import UserAlreadyExistsError


def test_register_user_success():
    repo = InMemoryUserRepository()
    hasher = BcryptPasswordHasher()
    service = UserService(repository=repo, password_hasher=hasher)

    user = service.register_user("alice", "strongpassword")
    assert user.username == "alice"


def test_register_user_duplicate():
    repo = InMemoryUserRepository()
    hasher = BcryptPasswordHasher()
    service = UserService(repository=repo, password_hasher=hasher)

    service.register_user("alice", "strongpassword")

    with pytest.raises(UserAlreadyExistsError):
        service.register_user("alice", "anotherpassword")


def test_register_user_stores_hashed_password():
    repo = InMemoryUserRepository()
    hasher = BcryptPasswordHasher()
    service = UserService(repository=repo, password_hasher=hasher)

    user = service.register_user("bob", "strongpassword")

    # Password stored should not be the plain password
    assert user.password_hash != "strongpassword"
    # And verify method should return True
    assert hasher.verify("strongpassword", user.password_hash)
