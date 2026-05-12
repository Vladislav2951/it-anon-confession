from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from sqlalchemy import func, select

from domain.entities import Permission
from domain.interfaces.database import IPermissionRepo
from infrastructure.postgres.models import (
    BusinessElementModel,
    PermissionModel,
    role_permissions,
    user_roles,
)
from infrastructure.postgres.repositories.base import BaseRepo


if TYPE_CHECKING:
    from pydantic import UUID7

logger = logging.getLogger(__name__)


class PermissionRepo(BaseRepo, IPermissionRepo):
    async def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> list[Permission]:
        stmt = select(PermissionModel).limit(limit).offset(offset)

        result = await self._session.execute(stmt)

        permission_models = result.scalars().all()
        if not permission_models:
            return []

        return [self._to_entity(m) for m in permission_models]

    async def count(self) -> int:
        stmt = select(func.count()).select_from(PermissionModel)
        total_result = await self._session.execute(stmt)
        return total_result.scalar_one()

    async def get_one(self, id: UUID7) -> Optional[Permission]:
        stmt = select(PermissionModel).where(PermissionModel.id == id)

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)

        role_model = result.unique().scalar_one_or_none()
        if not role_model:
            return None

        return self._to_entity(role_model)

    async def get_permissions_for_element(
        self, user_id: UUID7, business_element_name: str
    ) -> list[Permission]:
        stmt = (
            select(PermissionModel)
            .join(
                BusinessElementModel,
                BusinessElementModel.id == PermissionModel.business_element_id,
            )
            .join(
                role_permissions, PermissionModel.id == role_permissions.c.permission_id
            )
            .join(user_roles, role_permissions.c.role_id == user_roles.c.role_id)
            .where(
                user_roles.c.user_id == user_id,
                BusinessElementModel.name == business_element_name,
            )
            .distinct()
        )

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)
        permission_models = result.scalars().all()

        return [Permission.model_validate(p) for p in permission_models]

    def _to_entity(self, model: PermissionModel) -> Permission:
        return Permission.model_validate(model)
