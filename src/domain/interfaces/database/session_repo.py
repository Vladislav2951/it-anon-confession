from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.entities import Session


class ISessionRepo(ABC):
    @abstractmethod
    async def create(self, session: Session):
        pass

    @abstractmethod
    async def get_one(self, id: str, with_user: bool = False) -> Optional[Session]:
        pass

    @abstractmethod
    async def delete(self, id: str):
        pass

    @abstractmethod
    async def delete_all_for_user(self, user_id: UUID7):
        pass
