import pytest
from pathlib import Path

from module_2.resilient_data_importer_cli.parsers.csv_parser import parse_csv
from module_2.resilient_data_importer_cli.exceptions.importer_exceptions import (
    FileFormatError,
)


def test_parse_valid_csv(tmp_path: Path) -> None:
    csv_file = tmp_path / "users.csv"
    csv_file.write_text("user_id,name,email\n1,Bright,bright@test.com\n")

    users = parse_csv(str(csv_file))

    assert len(users) == 1
    assert users[0].email == "bright@test.com"


def test_missing_headers(tmp_path: Path) -> None:
    csv_file = tmp_path / "users.csv"
    csv_file.write_text("id,name\n1,Bright\n")

    with pytest.raises(FileFormatError):
        parse_csv(str(csv_file))


def test_file_not_found() -> None:
    with pytest.raises(FileFormatError):
        parse_csv("does_not_exist.csv")
