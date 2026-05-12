from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import TYPE_CHECKING, Optional

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import noload

from domain.dto import ChangePasswordUserInput, PatchUpdateUserInput
from domain.entities import Permission, User
from domain.errors import ConflictError, UpdateError
from domain.interfaces.database import IUserRepo
from infrastructure.postgres.models import (
    PermissionModel,
    RoleModel,
    UserModel,
    role_permissions,
    user_roles,
)
from infrastructure.postgres.repositories.base import BaseRepo


if TYPE_CHECKING:
    from pydantic import UUID7, EmailStr

    from domain.interfaces.database.filters import UserFilter


logger = logging.getLogger(__name__)


class UserRepo(BaseRepo, IUserRepo):
    async def create(self, user: User) -> User:
        user_model = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash.get_secret_value(),
            nickname=user.nickname,
            bio=user.bio,
        )

        self._session.add(user_model)

        await self._session.flush()

        return User.model_validate(user_model)

    async def get_one(self, id: UUID7) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == id, UserModel.deleted_at.is_(None))

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)

        user_model = result.unique().scalar_one_or_none()
        if not user_model:
            return None

        return User.model_validate(user_model)

    async def get_one_by_email(self, email: EmailStr) -> Optional[User]:
        stmt = select(UserModel).where(
            UserModel.email == email, UserModel.deleted_at.is_(None)
        )

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)

        user_model = result.unique().scalar_one_or_none()
        if not user_model:
            return None

        return User.model_validate(user_model)

    async def get_all(
        self,
        filter: Optional[UserFilter] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[User]:
        stmt = select(UserModel).where(UserModel.deleted_at.is_(None))

        if filter and filter.roles:
            stmt = stmt.where(UserModel.roles.any(RoleModel.name.in_(filter.roles)))

        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)

        user_models = result.scalars().all()
        if not user_models:
            return []

        return [User.model_validate(el) for el in user_models]

    async def count(self, filter: Optional[UserFilter] = None) -> int:
        stmt = (
            select(func.count(UserModel.id))
            .select_from(UserModel)
            .where(UserModel.deleted_at.is_(None))
        )

        if filter and filter.roles:
            stmt = stmt.where(UserModel.roles.any(RoleModel.name.in_(filter.roles)))

        total_result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)

        return total_result.scalar_one()

    async def update(
        self, id: UUID7, update_inp: ChangePasswordUserInput | PatchUpdateUserInput
    ) -> User:
        if isinstance(update_inp, ChangePasswordUserInput):
            to_update = {"password_hash": update_inp.password_hash.get_secret_value()}
        else:
            to_update = update_inp.model_dump(exclude_unset=True)

        if not to_update:
            raise UpdateError(f"Nothing to update for {id}")

        stmt = (
            update(UserModel)
            .where(UserModel.id == id, UserModel.deleted_at.is_(None))
            .values(**to_update)
            .returning(UserModel)
            .options(noload(UserModel.roles))
        )
        try:
            result = await self._session.execute(stmt)
        except IntegrityError as e:
            raise ConflictError(f"User with such email or nickname is already exist: {e}")

        logger.debug("Execute: %s", stmt)
        user = result.scalar_one()

        return User.model_validate(user)

    async def soft_delete(self, id: UUID7):
        stmt = (
            update(UserModel)
            .where(UserModel.id == id, UserModel.deleted_at.is_(None))
            .values(deleted_at=datetime.now(timezone.utc))
        )

        await self._session.execute(stmt)

    async def get_permissions(self, user_id: UUID7) -> list[Permission]:
        stmt = (
            select(PermissionModel)
            .join(
                role_permissions, PermissionModel.id == role_permissions.c.permission_id
            )
            .join(user_roles, role_permissions.c.role_id == user_roles.c.role_id)
            .where(user_roles.c.user_id == user_id)
            .distinct()
        )

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)
        permission_models = result.scalars().all()

        return [Permission.model_validate(p) for p in permission_models]

    async def assign_role(self, user_id: UUID7, role_id: UUID7):
        stmt = insert(user_roles).values(user_id=user_id, role_id=role_id)
        try:
            await self._session.execute(stmt)
        except IntegrityError:
            raise ConflictError(f"Role {role_id} is already assigned to user {user_id}")

    async def revoke_role(self, user_id: UUID7, role_id: UUID7):
        stmt = delete(user_roles).where(
            user_roles.c.user_id == user_id, user_roles.c.role_id == role_id
        )
        await self._session.execute(stmt)

    async def get_id_by_email(self, email: EmailStr) -> Optional[UUID7]:
        stmt = select(UserModel.id).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
