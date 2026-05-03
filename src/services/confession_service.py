from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from domain.entities import Confession
from domain.errors import ForbiddenError, NotFoundError


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.dto import ConfessionCreateInput, ConfessionUpdateInput, IdentityContext
    from domain.interfaces.database.uow import IDatabaseTransactionFactory
    from services import AccessService


class ConfessionService:
    """
    Сервис управления признаниями.
    """

    def __init__(
        self,
        db_transaction_factory: IDatabaseTransactionFactory,
        access_srv: AccessService,
    ):
        self._db_transaction_factory = db_transaction_factory
        self.access_srv = access_srv

    async def create(
        self, confession_inp: ConfessionCreateInput, identity_ctx: IdentityContext
    ) -> Confession:
        current_user = identity_ctx.current_user
        if not current_user:
            raise RuntimeError("Current user must be presented")

        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
            current_user.id,
        )

        confession = Confession.create(
            title=confession_inp.title,
            body=confession_inp.body,
            authored_by=current_user.nickname,
            user_id=current_user.id,
        )

        async with self._db_transaction_factory() as t:
            return await t.confession_repo.create(confession)

    async def get_one(self, id: UUID7, identity_ctx: IdentityContext) -> Confession:
        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
            identity_ctx.current_user.id if identity_ctx.current_user else None,
        )

        async with self._db_transaction_factory() as t:
            confession = await t.confession_repo.get_one(id)
            if not confession:
                raise NotFoundError(f"Confession {id} not found")

            return confession

    async def get_all(
        self, identity_ctx: IdentityContext, limit: int = 20, offset: Optional[int] = None
    ) -> tuple[list[Confession], int]:
        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
            identity_ctx.current_user.id if identity_ctx.current_user else None,
        )

        async with self._db_transaction_factory() as t:
            return await t.confession_repo.get_all(limit, offset)

    async def update(
        self, id: UUID7, update_inp: ConfessionUpdateInput, identity_ctx: IdentityContext
    ) -> Confession:

        async with self._db_transaction_factory() as t:
            confession = await t.confession_repo.get_one(id)

            owner_id = confession.user_id if confession else None
            await self.access_srv.check_access(
                identity_ctx.current_user,
                identity_ctx.business_element_name,
                identity_ctx.action,
                owner_id,
            )

            if not confession:
                raise NotFoundError(f"Confession {id} not found")

            return await t.confession_repo.update(id, update_inp)

    async def delete(self, id: UUID7, identity_ctx: IdentityContext) -> None:

        async with self._db_transaction_factory() as t:
            confession = await t.confession_repo.get_one(id)

            owner_id = confession.user_id if confession else None
            await self.access_srv.check_access(
                identity_ctx.current_user,
                identity_ctx.business_element_name,
                identity_ctx.action,
                owner_id,
            )

            if not confession:
                return None

            await t.confession_repo.delete(id)
