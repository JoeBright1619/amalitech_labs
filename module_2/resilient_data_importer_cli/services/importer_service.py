from pathlib import Path
from typing import List

from ..models.user import User
from ..parsers.csv_parser import parse_csv
from ..repository.json_user_repository import JsonUserRepository
from ..exceptions.importer_exceptions import DuplicateUserError
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class ImporterService:
    """Service that imports users from CSV into the repository."""

    def __init__(self, repository: JsonUserRepository):
        self.repository = repository

    def import_from_csv(self, file_path: Path) -> List[User]:
        """Parse CSV and store users in the repository.

        Returns:
            List of successfully imported User objects.
        """
        imported_users: List[User] = []

        users = parse_csv(str(file_path))

        for user in users:
            try:
                self.repository.add(user)
                imported_users.append(user)
                logger.info(f"Imported user {user.user_id}")
            except DuplicateUserError:
                logger.warning(f"Duplicate user {user.user_id} skipped")

        return imported_users
