from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from domain.entities import Role
from domain.errors import ConflictError, ForbiddenError, NotFoundError


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.dto import IdentityContext, RoleCreateInput, RoleUpdateInput
    from domain.interfaces.database.uow import IDatabaseTransactionFactory
    from domain.validators import NameStr
    from services import AccessService


class RoleService:
    def __init__(
        self,
        db_transaction_factory: IDatabaseTransactionFactory,
        access_srv: AccessService,
    ):
        self._db_transaction_factory = db_transaction_factory
        self.access_srv = access_srv

    async def create(
        self, role_inp: RoleCreateInput, identity_ctx: IdentityContext
    ) -> Role:
        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
        )

        role = Role.create(name=role_inp.name)

        async with self._db_transaction_factory() as t:
            if await t.role_repo.get_one_by_name(role.name):
                raise ConflictError(f"'{role.name}' already exists")

            return await t.role_repo.create(role)

    async def get_one(self, id: UUID7, identity_ctx: IdentityContext) -> Role:
        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
        )

        async with self._db_transaction_factory() as t:
            role = await t.role_repo.get_one(id)
            if not role:
                raise NotFoundError(f"Role {id} not found")

            return role

    async def get_one_by_name(self, name: NameStr, identity_ctx: IdentityContext) -> Role:
        async with self._db_transaction_factory() as t:
            role = await t.role_repo.get_one_by_name(name)
            await self.access_srv.check_access(
                identity_ctx.current_user,
                identity_ctx.business_element_name,
                identity_ctx.action,
                role.id if role else None,
            )

            if not role:
                raise NotFoundError(f"Role {name} not found")

            return role

    async def get_all(self, identity_ctx: IdentityContext) -> list[Role]:
        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
        )

        async with self._db_transaction_factory() as t:
            return await t.role_repo.get_all()

    async def update(
        self, id: UUID7, update_inp: RoleUpdateInput, identity_ctx: IdentityContext
    ) -> Role:
        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
        )

        async with self._db_transaction_factory() as t:
            role = await t.role_repo.get_one(id)
            if not role:
                raise NotFoundError(f"Role {id} not found")

            if role.is_system:
                raise ConflictError(f"System roles cannot be updated")

            return await t.role_repo.update(id, update_inp)

    async def delete(self, id: UUID7, identity_ctx: IdentityContext) -> None:
        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
        )

        async with self._db_transaction_factory() as t:
            role = await t.role_repo.get_one(id)
            if not role:
                return None

            if role.is_system:
                raise ForbiddenError("System roles cannot be deleted")

            return await t.role_repo.delete(id)

    async def assign_permission(
        self, role_id: UUID7, permission_id: UUID7, identity_ctx: IdentityContext
    ):
        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
        )

        async with self._db_transaction_factory() as t:
            if not await t.role_repo.get_one(role_id):
                raise NotFoundError(f"Role {role_id} not found")

            if not await t.permission_repo.get_one(permission_id):
                raise NotFoundError(f"Permission {permission_id} not found")

            return await t.role_repo.assign_permission(role_id, permission_id)

    async def revoke_permission(
        self, role_id: UUID7, permission_id: UUID7, identity_ctx: IdentityContext
    ):
        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
        )

        async with self._db_transaction_factory() as t:
            if not await t.role_repo.get_one(role_id):
                raise NotFoundError(f"Role {role_id} not found")

            if not await t.permission_repo.get_one(permission_id):
                raise NotFoundError(f"Permission {permission_id} not found")

            return await t.role_repo.revoke_permission(role_id, permission_id)
