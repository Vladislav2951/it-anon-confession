from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Optional

from sqlalchemy import select
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.dto import RegisterInput
from domain.entities import User
from domain.interfaces.database import IUserRepo
from infrastructure.postgres.repositories.base import BaseRepo
from infrastructure.postgres.tables import user_table


logger = getLogger(__name__)


if TYPE_CHECKING:
    from pydantic import EmailStr
    from sqlalchemy.ext.asyncio import AsyncSession


# * Don't use ORM


class UserRepo(BaseRepo, IUserRepo):
    async def create(self, register_inp: RegisterInput) -> User:
        # TODO implement
        return User(
            id=uuid7(),
            email=register_inp.email,
            password_hash=register_inp.password,
            first_name=register_inp.first_name,
            last_name=register_inp.last_name,
            father_name=register_inp.father_name,
        )

    async def get_one_by_email(self, email: EmailStr) -> Optional[User]:
        stmt = select(
            user_table.c.id,
            user_table.c.email,
            user_table.c.password.label("password_hash"),
            user_table.c.first_name,
            user_table.c.last_name,
            user_table.c.father_name,
            user_table.c.deleted_at,
        ).where(user_table.c.email == email)

        logger.debug("Execute: %s", stmt)
        result = await self._session.execute(stmt)
        row = result.fetchone()
        if not row:
            return None

        return User.model_validate(row)


def user_repo_factory(session: AsyncSession):
    return UserRepo(session)
