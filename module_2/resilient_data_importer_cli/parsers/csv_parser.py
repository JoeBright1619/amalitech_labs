import csv
from typing import List

from ..models.user import User
from ..exceptions.importer_exceptions import FileFormatError, MissingFieldError


REQUIRED_FIELDS = {"user_id", "name", "email"}


def parse_csv(file_path: str) -> List[User]:
    """Parse a CSV file and return a list of User objects.

    Args:
        file_path: Path to the CSV file.

    Raises:
        FileFormatError: If CSV headers are invalid.
        MissingFieldError: If a row is missing required fields.
    """
    users: List[User] = []

    try:
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            if not reader.fieldnames:
                raise FileFormatError("CSV file has no headers")

            missing_headers = REQUIRED_FIELDS - set(reader.fieldnames)
            if missing_headers:
                raise FileFormatError(
                    f"Missing required headers: {', '.join(missing_headers)}"
                )

            for row_number, row in enumerate(reader, start=2):
                try:
                    users.append(
                        User(
                            user_id=row["user_id"].strip(),
                            name=row["name"].strip(),
                            email=row["email"].strip(),
                        )
                    )
                except KeyError as exc:
                    raise MissingFieldError(
                        f"Missing field in row {row_number}"
                    ) from exc

    except FileNotFoundError as exc:
        raise FileFormatError("CSV file not found") from exc

    return users
