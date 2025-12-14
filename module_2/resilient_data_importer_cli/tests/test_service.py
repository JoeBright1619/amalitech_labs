from typing import Dict
from pathlib import Path

from module_2.resilient_data_importer_cli.models.user import User
from module_2.resilient_data_importer_cli.services.importer_service import (
    ImporterService,
)

from module_2.resilient_data_importer_cli.exceptions.importer_exceptions import (
    DuplicateUserError,
)


class FakeRepo:
    def __init__(self):
        self.users = {}

    def add(self, user: User) -> None:
        if user.user_id in self.users:
            raise DuplicateUserError()
        self.users[user.user_id] = user

    def list_all(self) -> Dict[str, dict]:
        return self.users


def test_importer_service_success(tmp_path: Path, monkeypatch):
    # Fake CSV parser
    fake_csv = tmp_path / "users.csv"
    fake_csv.write_text(
        "user_id,name,email\n1,Bright,bright@test.com\n2,Alice,alice@test.com\n"
    )

    fake_users = [
        User(user_id="1", name="Bright", email="bright@test.com"),
        User(user_id="2", name="Alice", email="alice@test.com"),
    ]

    monkeypatch.setattr(
        "module_2.resilient_data_importer_cli.services.importer_service.parse_csv",
        lambda _: fake_users,
    )

    repo = FakeRepo()
    service = ImporterService(repo)

    imported = service.import_from_csv(fake_csv)
    assert len(imported) == 2
    assert "1" in repo.users
    assert "2" in repo.users


def test_importer_service_skips_duplicates(monkeypatch):
    fake_users = [
        User(user_id="1", name="Bright", email="bright@test.com"),
        User(user_id="1", name="Bright Duplicate", email="bright2@test.com"),
    ]

    monkeypatch.setattr(
        "module_2.resilient_data_importer_cli.services.importer_service.parse_csv",
        lambda _: fake_users,
    )

    repo = FakeRepo()
    service = ImporterService(repo)

    imported = service.import_from_csv(Path("dummy.csv"))
    assert len(imported) == 1  # only first user added
