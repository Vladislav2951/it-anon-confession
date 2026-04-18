from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self


if TYPE_CHECKING:
    from domain.interfaces.database import IUserRepo


class IDatabaseUoW(ABC):
    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(self, exp_type, exp_val, exp_tb): ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

    @property
    @abstractmethod
    def user_repo(self) -> IUserRepo: ...


class IDatabaseUoWFactory(ABC):
    @abstractmethod
    def __call__(self) -> IDatabaseUoW: ...
