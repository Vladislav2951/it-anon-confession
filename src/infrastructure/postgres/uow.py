from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Self

from domain.interfaces.database.uow import (
    IDatabaseTransactionFactory,
    IDatabaseTransactionUoW,
)
from infrastructure.postgres.repositories import (
    ConfessionRepo,
    PermissionRepo,
    RoleRepo,
    SessionRepo,
    UserRepo,
)

from .db import async_session_maker


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from domain.interfaces.database import (
        IConfessionRepo,
        IPermissionRepo,
        IRoleRepo,
        ISessionRepo,
        IUserRepo,
    )


class TransactionUoW(IDatabaseTransactionUoW):
    def __init__(self, session_factory):
        self._session_factory = session_factory
        self._session: Optional[AsyncSession] = None
        self._repositories = {}

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("UoW is not initialized. Use 'async with'")
        return self._session

    def _get_repo(self, repo_class):
        if repo_class not in self._repositories:
            self._repositories[repo_class] = repo_class(self.session)
        return self._repositories[repo_class]

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                await self.rollback()
            else:
                await self.commit()
        finally:
            await self.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None

    @property
    def user_repo(self) -> IUserRepo:
        return self._get_repo(UserRepo)

    @property
    def session_repo(self) -> ISessionRepo:
        return self._get_repo(SessionRepo)

    @property
    def role_repo(self) -> IRoleRepo:
        return self._get_repo(RoleRepo)

    @property
    def permission_repo(self) -> IPermissionRepo:
        return self._get_repo(PermissionRepo)

    @property
    def confession_repo(self) -> IConfessionRepo:
        return self._get_repo(ConfessionRepo)


class TransactionFactory(IDatabaseTransactionFactory):
    def __call__(self) -> IDatabaseTransactionUoW:
        return TransactionUoW(async_session_maker)
