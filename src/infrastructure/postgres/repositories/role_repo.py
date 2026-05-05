from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Optional

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import noload

from domain.dto import RoleUpdateInput
from domain.entities import Role
from domain.errors import ConflictError, UpdateError
from domain.interfaces.database import IRoleRepo
from infrastructure.postgres.models import RoleModel, role_permissions, user_roles
from infrastructure.postgres.repositories.base import BaseRepo


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.validators import NameStr

logger = logging.getLogger(__name__)


class RoleRepo(BaseRepo, IRoleRepo):
    async def create(self, role: Role) -> Role:
        new_role = RoleModel(id=role.id, name=role.name)

        self._session.add(new_role)
        await self._session.flush()

        return Role.model_validate(new_role)

    async def get_one(self, id: UUID7) -> Optional[Role]:
        stmt = select(RoleModel).where(RoleModel.id == id)

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)

        role_model = result.unique().scalar_one_or_none()
        if not role_model:
            return None

        return Role.model_validate(role_model)

    async def get_one_by_name(self, name: NameStr) -> Optional[Role]:
        stmt = select(RoleModel).where(RoleModel.name == name)

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)

        role_model = result.unique().scalar_one_or_none()
        if not role_model:
            return None

        return Role.model_validate(role_model)

    async def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> tuple[list[Role], int]:
        stmt = select(RoleModel).limit(limit).offset(offset)
        count_stmt = select(func.count()).select_from(RoleModel)

        async with asyncio.TaskGroup() as tg:
            result_task = tg.create_task(self._session.execute(stmt))
            total_result_task = tg.create_task(self._session.execute(count_stmt))

        result = result_task.result()
        total_result = total_result_task.result()

        role_models = result.scalars().unique().all()
        if not role_models:
            return [], 0

        total = total_result.scalar_one()

        return [Role.model_validate(m) for m in role_models], total

    async def update(self, id: UUID7, update_inp: RoleUpdateInput) -> Role:
        to_update = update_inp.model_dump(exclude_unset=True)

        if not to_update:
            raise UpdateError(f"Nothing to update for {id}")

        stmt = (
            update(RoleModel)
            .where(RoleModel.id == id)
            .values(**to_update)
            .returning(RoleModel)
            .options(noload(RoleModel.permissions))
        )

        result = await self._session.execute(stmt)
        role = result.scalar_one()

        return Role.model_validate(role)

    async def delete(self, id: UUID7):
        stmt = delete(RoleModel).where(RoleModel.id == id)
        await self._session.execute(stmt)

    async def get_user_roles(self, user_id: UUID7) -> list[Role]:
        stmt = (
            select(RoleModel)
            .join(user_roles, user_roles.c.role_id == RoleModel.id)
            .where(user_roles.c.user_id == user_id)
        )

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)

        role_models = list(result.scalars().unique().all())

        return [self._to_entity(m) for m in role_models]

    async def assign_permission(self, role_id: UUID7, permission_id: UUID7):
        stmt = insert(role_permissions).values(
            role_id=role_id, permission_id=permission_id
        )
        try:
            await self._session.execute(stmt)
        except IntegrityError:
            raise ConflictError(f"Permission {permission_id} has already been assigned")

    async def revoke_permission(self, role_id: UUID7, permission_id: UUID7):
        stmt = delete(role_permissions).where(
            role_permissions.c.role_id == role_id,
            role_permissions.c.permission_id == permission_id,
        )
        await self._session.execute(stmt)

    def _to_entity(self, model: RoleModel) -> Role:
        return Role(id=model.id, name=model.name, is_system=model.is_system)
