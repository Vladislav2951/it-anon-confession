from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from domain.errors import NotFoundError


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.dto import IdentityContext
    from domain.entities import BusinessElement
    from domain.interfaces.database.uow import IDatabaseTransactionFactory
    from services import AccessService

logger = logging.getLogger(__name__)


class BusinessElementService:
    """
    Сервис управления бизнес-элементами (контекстами прав доступа).
    """

    def __init__(
        self,
        db_transaction_factory: IDatabaseTransactionFactory,
        access_srv: AccessService,
    ):
        self._db_transaction_factory = db_transaction_factory
        self.access_srv = access_srv

    async def get_one(self, id: UUID7, identity_ctx: IdentityContext) -> BusinessElement:
        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
        )

        async with self._db_transaction_factory() as t:
            business_element = await t.business_element_repo.get_one(id)
            if not business_element:
                raise NotFoundError(f"BusinessElement {id} not found")

            return business_element

    async def get_all(
        self, identity_ctx: IdentityContext, limit: int = 20, offset: Optional[int] = None
    ) -> tuple[list[BusinessElement], int]:
        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
        )

        async with self._db_transaction_factory() as t:
            return await t.business_element_repo.get_all(limit, offset)
