import argparse
from pathlib import Path
import sys

from .repository.user_repository import UserRepository
from .services.importer_service import ImporterService
from .exceptions.importer_exceptions import ImporterError


def main() -> None:
    BASE_DIR = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Import users from a CSV file into a JSON database"
    )
    parser.add_argument(
        "csv_file",
        type=Path,
        help="Path to the CSV file containing user data",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=BASE_DIR / "data" / "database.json",
        help="Path to JSON database file",
    )

    args = parser.parse_args()

    # ensure parent directory exists
    args.db.parent.mkdir(parents=True, exist_ok=True)

    repository = UserRepository(args.db)
    service = ImporterService(repository)

    try:
        imported_users = service.import_from_csv(args.csv_file)
        print(f"Successfully imported {len(imported_users)} users.")
    except ImporterError as exc:
        print(f"Import failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
