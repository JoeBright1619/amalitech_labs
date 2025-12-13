from pathlib import Path
from typing import Dict

from ..models.user import User
from ..context_managers.file_manager import open_json_db
from ..exceptions.importer_exceptions import DuplicateUserError


class UserRepository:
    """JSON-backed repository for User entities."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def add(self, user: User) -> None:
        """Add a user to the repository.

        Raises:
            DuplicateUserError: If user_id already exists.
        """
        with open_json_db(self._db_path) as db:
            if user.user_id in db:
                raise DuplicateUserError(f"User with id {user.user_id} already exists")

            db[user.user_id] = {
                "name": user.name,
                "email": user.email,
            }

    def list_all(self) -> Dict[str, dict]:
        """Return all stored users."""
        with open_json_db(self._db_path) as db:
            return dict(db)
