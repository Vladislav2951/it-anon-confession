from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Optional

from sqlalchemy import insert, select
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


# * Here I don't use ORM


class UserRepo(BaseRepo, IUserRepo):
    async def create(self, register_inp: RegisterInput) -> User:
        new_id = uuid7()

        stmt = (
            insert(user_table)
            .values(
                id=new_id,
                email=register_inp.email,
                password=register_inp.password.get_secret_value(),
                first_name=register_inp.first_name,
                last_name=register_inp.last_name,
                father_name=register_inp.father_name,
            )
            .returning(
                user_table.c.id,
                user_table.c.email,
                user_table.c.password.label("password_hash"),
                user_table.c.first_name,
                user_table.c.last_name,
                user_table.c.father_name,
            )
        )

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)

        row = result.mappings().fetchone()
        if not row:
            raise RuntimeError("Failed to insert user")

        return User.model_validate(row)

    async def get_one_by_email(self, email: EmailStr) -> Optional[User]:
        stmt = select(
            user_table.c.id,
            user_table.c.email,
            user_table.c.password.label("password_hash"),
            user_table.c.first_name,
            user_table.c.last_name,
            user_table.c.father_name,
        ).where(user_table.c.email == email, user_table.c.deleted_at.is_(None))

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)

        row = result.mappings().fetchone()
        if not row:
            return None

        return User.model_validate(row)


def user_repo_factory(session: AsyncSession):
    return UserRepo(session)
