from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import TYPE_CHECKING, Optional

from sqlalchemy import select, update
from sqlalchemy.orm import joinedload, noload

from domain.dto import RegisterInput
from domain.entities import User
from domain.interfaces.database import IUserRepo
from infrastructure.postgres.models import RoleModel, UserModel
from infrastructure.postgres.repositories.base import BaseRepo


if TYPE_CHECKING:
    from domain.interfaces.database.filters import UserFilter


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from pydantic import UUID7, EmailStr


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

    async def get_one(self, id: UUID7, with_roles: bool = False) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == id, UserModel.deleted_at.is_(None))

        if with_roles:
            stmt = stmt.options(joinedload(UserModel.roles))
        else:
            stmt = stmt.options(noload(UserModel.roles))

        result = await self._session.execute(stmt)

        user_model = result.scalar_one_or_none()
        if not user_model:
            return None

        return User.model_validate(user_model)

    async def get_one_by_email(
        self, email: EmailStr, with_roles: bool = False
    ) -> Optional[User]:
        stmt = select(UserModel).where(
            UserModel.email == email, UserModel.deleted_at.is_(None)
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

    async def get_all(
        self, with_roles: bool = False, filter: Optional[UserFilter] = None
    ) -> list[User]:
        stmt = select(UserModel).where(UserModel.deleted_at.is_(None))

        if filter and filter.roles:
            stmt = stmt.join(UserModel.roles).where(RoleModel.name.in_(filter.roles))

        if with_roles:
            stmt = stmt.options(joinedload(UserModel.roles))
        else:
            stmt = stmt.options(noload(UserModel.roles))

        result = await self._session.execute(stmt)

        user_models = result.scalars().unique().all()
        if not user_models:
            return []

        users: list[User] = []
        for el in user_models:
            users.append(User.model_validate(el))

        return users

    async def soft_delete(self, id: UUID7):
        stmt = (
            update(UserModel)
            .where(UserModel.id == id, UserModel.deleted_at.is_(None))
            .values(deleted_at=datetime.now(timezone.utc))
        )

        await self._session.execute(stmt)
