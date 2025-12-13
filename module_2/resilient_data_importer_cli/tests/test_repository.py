import pytest
from pathlib import Path

from module_2.resilient_data_importer_cli.models.user import User
from module_2.resilient_data_importer_cli.repository.user_repository import (
    UserRepository,
)
from module_2.resilient_data_importer_cli.exceptions.importer_exceptions import (
    DuplicateUserError,
)


def test_add_user(tmp_path: Path) -> None:
    db_file = tmp_path / "db.json"
    repo = UserRepository(db_file)

    user = User(user_id="1", name="Bright", email="bright@test.com")
    repo.add(user)

    data = repo.list_all()
    assert "1" in data


def test_duplicate_user_raises(tmp_path: Path) -> None:
    db_file = tmp_path / "db.json"
    repo = UserRepository(db_file)

    user = User(user_id="1", name="Bright", email="bright@test.com")
    repo.add(user)

    with pytest.raises(DuplicateUserError):
        repo.add(user)
