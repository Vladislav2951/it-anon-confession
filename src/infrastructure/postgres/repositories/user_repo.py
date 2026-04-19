from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload, noload

from domain.dto import RegisterInput
from domain.entities import User
from domain.interfaces.database import IUserRepo
from infrastructure.postgres.models import UserModel
from infrastructure.postgres.repositories.base import BaseRepo


logger = getLogger(__name__)


if TYPE_CHECKING:
    from pydantic import EmailStr


class UserRepo(BaseRepo, IUserRepo):
    async def create(self, register_inp: RegisterInput) -> User:
        new_user = UserModel(
            email=register_inp.email,
            password_hash=register_inp.password.get_secret_value(),
            first_name=register_inp.first_name,
            last_name=register_inp.last_name,
            father_name=register_inp.father_name,
            roles=[],  # Важно для lazy='raise'
        )

        self._session.add(new_user)

        await self._session.flush()

        return User.model_validate(new_user)

    async def get_one_by_email(
        self, email: EmailStr, with_roles: bool = False
    ) -> Optional[User]:
        stmt = (
            select(UserModel)
            .where(UserModel.email == email, UserModel.deleted_at.is_(None))
            .options()
        )

        if with_roles:
            stmt = stmt.options(joinedload(UserModel.roles))
        else:
            stmt = stmt.options(noload(UserModel.roles))

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)

        user_model = result.scalar_one_or_none()

        if not user_model:
            return None

        return User.model_validate(user_model)
