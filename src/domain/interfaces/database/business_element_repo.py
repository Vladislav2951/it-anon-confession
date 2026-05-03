from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.entities import BusinessElement
    from domain.validators import NameStr


class IBusinessElementRepo(ABC):
    @abstractmethod
    async def get_one(self, id: UUID7) -> Optional[BusinessElement]:
        pass

    @abstractmethod
    async def get_one_by_name(self, name: NameStr) -> Optional[BusinessElement]:
        pass

    @abstractmethod
    async def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> tuple[list[BusinessElement], int]:
        pass
