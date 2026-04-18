from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.dto import RegisterInput
from domain.entities import User
from domain.interfaces.database import IUserRepo
from infrastructure.postgres.repositories.base import BaseRepo


if TYPE_CHECKING:
    from pydantic import EmailStr
    from sqlalchemy.ext.asyncio import AsyncSession


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
        return User(
            id=uuid7(),
            email=email,
            password_hash="sdfdsfsdfsdf",
            first_name="Гадя",
            last_name="Хренова",
            father_name="Петрович",
        )

        return None


def user_repo_factory(session: AsyncSession):
    return UserRepo(session)
