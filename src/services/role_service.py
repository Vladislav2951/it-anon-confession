from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from domain.entities import Role
from domain.errors import ConflictError, NotFoundError


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.dto import RoleCreateInput, RoleUpdateInput
    from domain.interfaces.database.uow import IDatabaseTransactionFactory
    from domain.validators import NameStr
    from services import AccessService

logger = logging.getLogger(__name__)


class RoleService:
    """
    Сервис управления ролями и их связями с разрешениями.
    """

    def __init__(
        self,
        db_transaction_factory: IDatabaseTransactionFactory,
        access_srv: AccessService,
    ):
        self._db_transaction_factory = db_transaction_factory
        self.access_srv = access_srv

    async def create(self, role_inp: RoleCreateInput) -> Role:
        role = Role.create(name=role_inp.name)

        async with self._db_transaction_factory() as t:
            if await t.role_repo.get_one_by_name(role.name):
                raise ConflictError(f"'{role.name}' already exists")

            return await t.role_repo.create(role)

    async def get_one(self, id: UUID7) -> Role:
        async with self._db_transaction_factory() as t:
            role = await t.role_repo.get_one(id)
            if not role:
                raise NotFoundError(f"Role {id} not found")

            return role

    async def get_one_by_name(self, name: NameStr) -> Role:
        async with self._db_transaction_factory() as t:
            role = await t.role_repo.get_one_by_name(name)
            if not role:
                raise NotFoundError(f"Role {name} not found")

            return role

    async def get_all(
        self, limit: int = 20, offset: Optional[int] = None
    ) -> tuple[list[Role], int]:
        async with self._db_transaction_factory() as t:
            if count := await t.role_repo.count():
                roles = await t.role_repo.get_all(limit, offset)
                return roles, count
            else:
                return [], 0

    async def update(self, id: UUID7, update_inp: RoleUpdateInput) -> Role:
        async with self._db_transaction_factory() as t:
            role = await t.role_repo.get_one(id)
            if not role:
                raise NotFoundError(f"Role {id} not found")

            if role.is_system:
                raise ConflictError(f"System roles cannot be updated")

            return await t.role_repo.update(id, update_inp)

    async def delete(self, id: UUID7) -> None:
        async with self._db_transaction_factory() as t:
            role = await t.role_repo.get_one(id)
            if not role:
                return None

            if role.is_system:
                raise ConflictError("System roles cannot be deleted")

            return await t.role_repo.delete(id)

    async def assign_permission(self, role_id: UUID7, permission_id: UUID7):
        async with self._db_transaction_factory() as t:
            role = await t.role_repo.get_one(role_id)
            if not role:
                raise NotFoundError(f"Role {role_id} not found")

            if role.is_system:
                raise ConflictError("System roles cannot be updated")

            if not await t.permission_repo.get_one(permission_id):
                raise NotFoundError(f"Permission {permission_id} not found")

            return await t.role_repo.assign_permission(role_id, permission_id)

    async def revoke_permission(self, role_id: UUID7, permission_id: UUID7):
        async with self._db_transaction_factory() as t:
            role = await t.role_repo.get_one(role_id)
            if not role:
                raise NotFoundError(f"Role {role_id} not found")

            if role.is_system:
                raise ConflictError("System roles cannot be updated")

            if not await t.permission_repo.get_one(permission_id):
                raise NotFoundError(f"Permission {permission_id} not found")

            return await t.role_repo.revoke_permission(role_id, permission_id)
