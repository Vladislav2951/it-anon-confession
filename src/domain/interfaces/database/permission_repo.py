from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.entities import Permission


class IPermissionRepo(ABC):
    @abstractmethod
    async def get_one(self, id: UUID7) -> Optional[Permission]:
        pass

    @abstractmethod
    async def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> tuple[list[Permission], int]:
        pass

    @abstractmethod
    async def get_permissions_for_element(
        self, user_id: UUID7, business_element_name: str
    ) -> list[Permission]:
        pass
