from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.entities import Permission


class IPermissionRepo(ABC):
    @abstractmethod
    async def get_one(self, id: UUID7) -> Optional[Permission]: ...

    # @abstractmethod
    # async def get_one_by_name(self, name: str) -> Optional[Permission]: ...

    @abstractmethod
    async def get_all(self) -> list[Permission]: ...

    @abstractmethod
    async def get_permissions_for_element(
        self, user_id: UUID7, business_element_name: str
    ) -> list[Permission]: ...
