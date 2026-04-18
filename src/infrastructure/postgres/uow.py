from __future__ import annotations

from typing import TYPE_CHECKING, Self

from domain.interfaces.database.uow import IDatabaseUoW, IDatabaseUoWFactory
from infrastructure.postgres.repositories import UserRepo

from .db import async_session_maker


if TYPE_CHECKING:
    from domain.interfaces.database import IUserRepo


class SQLAlchemyUoW(IDatabaseUoW):
    async def __aenter__(self) -> Self:
        self._session = async_session_maker()
        self._transaction = self._session.begin()
        return self

    async def __aexit__(self, exp_type, exp_val, exp_tb):
        if exp_type is None:
            await self._transaction.commit()
        else:
            await self._transaction.rollback()

        await self._session.close()

    async def commit(self):
        await self._transaction.commit()

    async def rollback(self):
        await self._transaction.rollback()

    async def close(self):
        await self._session.close()

    @property
    def user_repo(self) -> IUserRepo:
        return UserRepo(self._session)


class SQLAlchemyUoWFactory(IDatabaseUoWFactory):
    def __call__(self) -> IDatabaseUoW:
        return SQLAlchemyUoW()
