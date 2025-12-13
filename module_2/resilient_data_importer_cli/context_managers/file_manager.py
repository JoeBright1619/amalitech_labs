import json
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, Any


@contextmanager
def open_json_db(file_path: Path) -> Iterator[Dict[str, Any]]:
    """Safely open a JSON file as a mutable dictionary."""
    if not file_path.exists():
        file_path.write_text("{}", encoding="utf-8")

    with file_path.open("r+", encoding="utf-8") as file:
        data = json.load(file)
        yield data
        file.seek(0)
        json.dump(data, file, indent=2)
        file.truncate()
