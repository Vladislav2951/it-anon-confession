from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from domain.entities import Session


class ISessionRepo(ABC):
    @abstractmethod
    async def create(self, session: Session): ...

    @abstractmethod
    async def get_one(self, id: str, with_user: bool = False) -> Optional[Session]: ...
