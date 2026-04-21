from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self


if TYPE_CHECKING:
    from domain.interfaces.database import (
        IPermissionRepo,
        IRoleRepo,
        ISessionRepo,
        IUserRepo,
    )


class IDatabaseTransactionUoW(ABC):
    @abstractmethod
    async def __aenter__(self) -> Self:
        pass

    @abstractmethod
    async def __aexit__(self, exp_type, exp_val, exp_tb):
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @property
    @abstractmethod
    def user_repo(self) -> IUserRepo:
        pass

    @property
    @abstractmethod
    def session_repo(self) -> ISessionRepo:
        pass

    @property
    @abstractmethod
    def role_repo(self) -> IRoleRepo:
        pass

    @property
    @abstractmethod
    def permission_repo(self) -> IPermissionRepo:
        pass


class IDatabaseTransactionFactory(ABC):
    @abstractmethod
    def __call__(self) -> IDatabaseTransactionUoW:
        pass
