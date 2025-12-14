from typing import Protocol, Dict
from ..models.user import User


class JsonUserRepository(Protocol):
    def add(self, user: User) -> None: ...

    def list_all(self) -> Dict[str, dict]: ...
