from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.dto import ConfessionUpdateInput
    from domain.entities import Confession


class IConfessionRepo(ABC):
    @abstractmethod
    async def create(self, confession: Confession) -> Confession:
        pass

    @abstractmethod
    async def get_one(self, id: UUID7) -> Optional[Confession]:
        pass

    @abstractmethod
    async def get_all(self) -> list[Confession]:
        pass

    @abstractmethod
    async def update(self, id: UUID7, update_inp: ConfessionUpdateInput) -> Confession:
        pass

    @abstractmethod
    async def delete(self, id: UUID7) -> None:
        pass
